from typing import Any, Dict, List, Optional

from database_engine.constants import (
    ID_COLUMN,
    DEFAULT_COLUMNS,
    SUCCESS_MESSAGES,
    ERROR_MESSAGES,
)
from database_engine.decorators import handle_db_errors, confirm_action, log_time
from database_engine.utils import FileManager, DataValidator
from database_engine.parser import CommandParser


class DatabaseEngine:
    """Main database engine class."""

    def __init__(self):
        self.parser = CommandParser()
        self.file_manager = FileManager()

    @handle_db_errors
    @log_time
    def create_table(self, table_name: str, columns: Dict[str, str]) -> str:
        """Create a new table."""
        if self.file_manager.table_exists(table_name):
            return f"Error: {ERROR_MESSAGES['table_exists']}"
        all_columns = {**DEFAULT_COLUMNS, **columns}

        metadata = self.file_manager.read_table_metadata()
        metadata[table_name] = all_columns
        self.file_manager.write_table_metadata(metadata)

        self.file_manager.write_table_data(table_name, [])

        return SUCCESS_MESSAGES["table_created"]

    @handle_db_errors
    @confirm_action("drop this table and all its data")
    def drop_table(self, table_name: str) -> str:
        """Drop an existing table."""
        if not self.file_manager.table_exists(table_name):
            return f"Error: {ERROR_MESSAGES['table_not_exists']}"

        metadata = self.file_manager.read_table_metadata()
        del metadata[table_name]
        self.file_manager.write_table_metadata(metadata)

        self.file_manager.delete_table_file(table_name)

        return SUCCESS_MESSAGES["table_dropped"]

    @handle_db_errors
    def list_tables(self) -> List[str]:
        """List all tables."""
        metadata = self.file_manager.read_table_metadata()
        return list(metadata.keys())

    @handle_db_errors
    @log_time
    def insert_row(self, table_name: str, values: List[Any]) -> str:
        """Insert a new row into table."""
        if not self.file_manager.table_exists(table_name):
            return f"Error: {ERROR_MESSAGES['table_not_exists']}"

        metadata = self.file_manager.read_table_metadata()
        columns = metadata[table_name]
        data = self.file_manager.read_table_data(table_name)

        validated_data = DataValidator.validate_row_data(columns, values)

        new_id = max([row.get(ID_COLUMN, 0) for row in data], default=0) + 1
        validated_data[ID_COLUMN] = new_id

        data.append(validated_data)
        self.file_manager.write_table_data(table_name, data)

        return SUCCESS_MESSAGES["row_inserted"]

    @handle_db_errors
    @log_time
    def select_rows(
        self, table_name: str, columns: List[str], where_condition: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Select rows from table."""
        if not self.file_manager.table_exists(table_name):
            raise ValueError(ERROR_MESSAGES["table_not_exists"])

        data = self.file_manager.read_table_data(table_name)

        if where_condition:
            data = [
                row
                for row in data
                if self.parser.evaluate_condition(row, where_condition)
            ]

        if columns != ["*"]:
            result = []
            for row in data:
                result_row = {}
                for col in columns:
                    if col in row:
                        result_row[col] = row[col]
                result.append(result_row)
            return result

        return data

    @handle_db_errors
    @log_time
    def update_rows(
        self,
        table_name: str,
        updates: Dict[str, Any],
        where_condition: Optional[str] = None,
    ) -> str:
        """Update rows in table."""
        if not self.file_manager.table_exists(table_name):
            return f"Error: {ERROR_MESSAGES['table_not_exists']}"

        metadata = self.file_manager.read_table_metadata()
        columns = metadata[table_name]
        data = self.file_manager.read_table_data(table_name)

        for col_name, new_value in updates.items():
            if col_name not in columns:
                return f"Error: Column {col_name} not found"
            expected_type = columns[col_name]
            try:
                updates[col_name] = DataValidator._cast_value(new_value, expected_type)
            except ValueError as e:
                return f"Error: {str(e)}"

        updated_count = 0
        for row in data:
            if not where_condition or self.parser.evaluate_condition(
                row, where_condition
            ):
                row.update(updates)
                updated_count += 1

        self.file_manager.write_table_data(table_name, data)

        return f"{updated_count}{SUCCESS_MESSAGES['rows_updated']}"

    @handle_db_errors
    @confirm_action("delete these rows")
    @log_time
    def delete_rows(
        self, table_name: str, where_condition: Optional[str] = None
    ) -> str:
        """Delete rows from table."""
        if not self.file_manager.table_exists(table_name):
            return f"Error: {ERROR_MESSAGES['table_not_exists']}"

        data = self.file_manager.read_table_data(table_name)

        if where_condition:
            new_data = [
                row
                for row in data
                if not self.parser.evaluate_condition(row, where_condition)
            ]
            deleted_count = len(data) - len(new_data)
        else:
            new_data = []
            deleted_count = len(data)
        self.file_manager.write_table_data(table_name, new_data)

        return f"{deleted_count}{SUCCESS_MESSAGES['rows_deleted']}"
