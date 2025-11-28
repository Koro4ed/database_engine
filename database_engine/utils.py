import json
import os
from typing import Any, Dict, List

from database_engine.constants import DB_META_FILE, DATA_DIR
from database_engine.decorators import handle_db_errors, cache_results


class FileManager:
    """Handles all file operations for the database."""

    @staticmethod
    @handle_db_errors
    def read_json(filepath: str) -> Any:
        """Read JSON file."""
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)

    @staticmethod
    @handle_db_errors
    def write_json(filepath: str, data: Any) -> None:
        """Write data to JSON file."""
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    @staticmethod
    @handle_db_errors
    @cache_results
    def read_table_metadata() -> Dict[str, Any]:
        """Read database metadata."""
        if not os.path.exists(DB_META_FILE):
            return {}
        return FileManager.read_json(DB_META_FILE)

    @staticmethod
    @handle_db_errors
    def write_table_metadata(metadata: Dict[str, Any]) -> None:
        """Write database metadata."""
        FileManager.write_json(DB_META_FILE, metadata)

    @staticmethod
    @handle_db_errors
    def read_table_data(table_name: str) -> List[Dict[str, Any]]:
        """Read table data from file."""
        filepath = os.path.join(DATA_DIR, f"{table_name}.json")
        if not os.path.exists(filepath):
            return []
        return FileManager.read_json(filepath)

    @staticmethod
    @handle_db_errors
    def write_table_data(table_name: str, data: List[Dict[str, Any]]) -> None:
        """Write table data to file."""
        filepath = os.path.join(DATA_DIR, f"{table_name}.json")
        FileManager.write_json(filepath, data)

    @staticmethod
    def table_exists(table_name: str) -> bool:
        """Check if table exists."""
        metadata = FileManager.read_table_metadata()
        return table_name in metadata

    @staticmethod
    def delete_table_file(table_name: str) -> None:
        """Delete table data file."""
        filepath = os.path.join(DATA_DIR, f"{table_name}.json")
        if os.path.exists(filepath):
            os.remove(filepath)


class DataValidator:
    """Validates data types and constraints."""

    @staticmethod
    def validate_row_data(
        columns: Dict[str, str], row_data: List[Any]
    ) -> Dict[str, Any]:
        """Validate row data against column definitions."""
        if len(row_data) != len(columns) - 1:  # -1 for auto ID
            raise ValueError(f"Expected {len(columns) - 1} values, got {len(row_data)}")

        validated_row = {}
        col_names = [name for name in columns.keys() if name != "id"]

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
                if value.lower() in ("true", "1", "yes"):
                    return True
                elif value.lower() in ("false", "0", "no"):
                    return False
            raise ValueError(f"Value {value} cannot be cast to bool")
        else:  # str
            return str(value)
