import re
from typing import Any, Dict, List, Tuple, Optional

from database_engine.constants import ERROR_MESSAGES, SUPPORTED_TYPES


class DataValidator:
    """Validates data types and constraints."""

    @staticmethod
    def validate_row_data(
        columns: Dict[str, str], row_data: List[Any]
    ) -> Dict[str, Any]:
        """Validate row data against column definitions."""
        data_columns = {k: v for k, v in columns.items() if k != "id"}

        if len(row_data) != len(data_columns):
            raise ValueError(
                f"Expected {len(data_columns)} values, got {len(row_data)}"
            )

        validated_row = {}
        col_names = list(data_columns.keys())

        for col_name, value in zip(col_names, row_data):
            expected_type = columns[col_name]
            validated_row[col_name] = DataValidator._cast_value(value, expected_type)

        return validated_row

    @staticmethod
    def _cast_value(value: Any, expected_type: str) -> Any:
        """Cast value to expected type."""
        if expected_type == "int":
            try:
                return int(value)
            except (ValueError, TypeError):
                raise ValueError(f"Value {value} cannot be cast to int")
        elif expected_type == "float":
            try:
                return float(value)
            except (ValueError, TypeError):
                raise ValueError(f"Value {value} cannot be cast to float")
        elif expected_type == "bool":
            if isinstance(value, bool):
                return value
            if isinstance(value, str):
                if value.lower() in ("true", "1", "yes", "t"):
                    return True
                elif value.lower() in ("false", "0", "no", "f"):
                    return False
            if isinstance(value, int):
                return bool(value)
            raise ValueError(f"Value {value} cannot be cast to bool")
        else:  # str
            return str(value)


class CommandParser:
    """Parser for SQL-like commands."""

    @staticmethod
    def parse_create_table(command: str) -> Tuple[str, Dict[str, str]]:
        """Parse CREATE TABLE command.

        Example: CREATE TABLE users (id int, name str, age int)
        """
        pattern = r"CREATE\s+TABLE\s+(\w+)\s*\((.+)\)"
        match = re.match(pattern, command, re.IGNORECASE)

        if not match:
            raise ValueError(ERROR_MESSAGES["invalid_syntax"])

        table_name = match.group(1)
        columns_str = match.group(2)

        # Parse columns
        columns = {}
        for col_def in columns_str.split(","):
            col_def = col_def.strip()
            if not col_def:
                continue
            parts = [part.strip() for part in col_def.split() if part.strip()]
            if len(parts) < 2:
                raise ValueError(ERROR_MESSAGES["invalid_syntax"])

            col_name = parts[0]
            col_type = parts[1].lower()

            if col_type not in SUPPORTED_TYPES:
                raise ValueError(f"{ERROR_MESSAGES['invalid_type']}: {col_type}")

            columns[col_name] = col_type

        return table_name, columns

    @staticmethod
    def parse_insert(command: str) -> Tuple[str, List[Any]]:
        """Parse INSERT command.

        Example: INSERT INTO users VALUES (1, "John", 25)
        """
        pattern = r"INSERT INTO (\w+) VALUES \((.+)\)"
        match = re.match(pattern, command, re.IGNORECASE)

        if not match:
            raise ValueError(ERROR_MESSAGES["invalid_syntax"])

        table_name = match.group(1)
        values_str = match.group(2)

        # Parse values
        values = []
        for value in CommandParser._split_values(values_str):
            values.append(CommandParser._parse_value(value.strip()))

        return table_name, values

    @staticmethod
    def parse_select(command: str) -> Tuple[str, List[str], Optional[str]]:
        """Parse SELECT command.

        Examples:
        - SELECT * FROM users
        - SELECT name, age FROM users WHERE age > 25
        """
        # Pattern for SELECT with WHERE
        where_pattern = r"SELECT (.+) FROM (\w+) WHERE (.+)"
        match = re.match(where_pattern, command, re.IGNORECASE)

        if match:
            columns_str = match.group(1)
            table_name = match.group(2)
            where_condition = match.group(3)
        else:
            # Pattern for SELECT without WHERE
            simple_pattern = r"SELECT (.+) FROM (\w+)"
            match = re.match(simple_pattern, command, re.IGNORECASE)
            if not match:
                raise ValueError(ERROR_MESSAGES["invalid_syntax"])

            columns_str = match.group(1)
            table_name = match.group(2)
            where_condition = None

        # Parse columns
        if columns_str.strip() == "*":
            columns = ["*"]
        else:
            columns = [col.strip() for col in columns_str.split(",")]

        return table_name, columns, where_condition

    @staticmethod
    def parse_update(command: str) -> Tuple[str, Dict[str, Any], Optional[str]]:
        """Parse UPDATE command.

        Example: UPDATE users SET age = 26 WHERE name = "John"
        """
        # Improved pattern to handle WHERE clause properly
        pattern = r"UPDATE\s+(\w+)\s+SET\s+(.+?)(?:\s+WHERE\s+(.+))?$"
        match = re.match(pattern, command, re.IGNORECASE)

        if not match:
            raise ValueError(ERROR_MESSAGES["invalid_syntax"])

        table_name = match.group(1)
        set_clause = match.group(2).strip()
        where_condition = match.group(3).strip() if match.group(3) else None

        # Parse SET clause more carefully
        updates = {}
        assignments = [a.strip() for a in set_clause.split(",")]

        for assignment in assignments:
            if "=" not in assignment:
                raise ValueError(f"Invalid assignment: {assignment}")

            # Split on first '=' only to handle values that might contain '='
            parts = assignment.split("=", 1)
            if len(parts) != 2:
                raise ValueError(f"Invalid assignment syntax: {assignment}")

            col_name = parts[0].strip()
            value_str = parts[1].strip()

            # Parse the value
            value = CommandParser._parse_value(value_str)
            updates[col_name] = value

        return table_name, updates, where_condition

    @staticmethod
    def parse_delete(command: str) -> Tuple[str, Optional[str]]:
        """Parse DELETE command.

        Examples:
        - DELETE FROM users
        - DELETE FROM users WHERE age < 18
        """
        pattern = r"DELETE FROM (\w+)(?: WHERE (.+))?"
        match = re.match(pattern, command, re.IGNORECASE)

        if not match:
            raise ValueError(ERROR_MESSAGES["invalid_syntax"])

        table_name = match.group(1)
        where_condition = match.group(2) if match.group(2) else None

        return table_name, where_condition

    @staticmethod
    def parse_drop_table(command: str) -> str:
        """Parse DROP TABLE command."""
        pattern = r"DROP TABLE (\w+)"
        match = re.match(pattern, command, re.IGNORECASE)

        if not match:
            raise ValueError(ERROR_MESSAGES["invalid_syntax"])

        return match.group(1)

    @staticmethod
    def _split_values(values_str: str) -> List[str]:
        """Split values string while respecting quotes."""
        values = []
        current = ""
        in_quotes = False
        quote_char = None
        escape_char = False

        for i, char in enumerate(values_str):
            if escape_char:
                current += char
                escape_char = False
            elif char == "\\":
                escape_char = True
            elif char in ('"', "'") and not in_quotes:
                in_quotes = True
                quote_char = char
                current += char
            elif char == quote_char and in_quotes:
                in_quotes = False
                quote_char = None
                current += char
            elif char == "," and not in_quotes:
                values.append(current.strip())
                current = ""
            else:
                current += char

        if current.strip():
            values.append(current.strip())

        return values

    @staticmethod
    def _parse_value(value: str) -> Any:
        """Parse a string value to appropriate Python type."""
        # Handle quoted strings
        if (value.startswith('"') and value.endswith('"')) or (
            value.startswith("'") and value.endswith("'")
        ):
            return value[1:-1]

        # Handle booleans
        if value.lower() == "true":
            return True
        elif value.lower() == "false":
            return False
        elif value.lower() == "null" or value.lower() == "none":
            return None

        # Handle numbers
        try:
            return int(value)
        except ValueError:
            try:
                return float(value)
            except ValueError:
                # Return as string if nothing else works
                return value

    @staticmethod
    def evaluate_condition(row: Dict[str, Any], condition: str) -> bool:
        """Evaluate WHERE condition for a row."""
        operators = [">=", "<=", "!=", "=", ">", "<"]

        for op in operators:
            if op in condition:
                left, right = condition.split(op, 1)
                left = left.strip()
                right = right.strip()

                # Get actual value from row
                left_val = row.get(left)
                right_val = CommandParser._parse_value(right)

                # Compare based on operator
                if op == "=":
                    return left_val == right_val
                elif op == "!=":
                    return left_val != right_val
                elif op == ">":
                    return left_val > right_val
                elif op == "<":
                    return left_val < right_val
                elif op == ">=":
                    return left_val >= right_val
                elif op == "<=":
                    return left_val <= right_val

        return True
