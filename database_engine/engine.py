from typing import Any

from database_engine.core import DatabaseEngine
from database_engine.parser import CommandParser
from database_engine.decorators import handle_db_errors
from database_engine.utils import FileManager


class DatabaseSession:
    """Handles database sessions and command execution."""

    def __init__(self):
        self.engine = DatabaseEngine()
        self.parser = CommandParser()
        self.file_manager = FileManager()

    @handle_db_errors
    def execute_command(self, command: str) -> Any:
        """Execute a SQL-like command."""
        command = command.strip().upper()

        try:
            if command.startswith("CREATE TABLE"):
                table_name, columns = self.parser.parse_create_table(command)
                return self.engine.create_table(table_name, columns)

            elif command.startswith("DROP TABLE"):
                table_name = self.parser.parse_drop_table(command)
                return self.engine.drop_table(table_name)

            elif command == "LIST TABLES":
                tables = self.engine.list_tables()
                return tables if tables else "No tables exist"

            elif command.startswith("INSERT INTO"):
                table_name, values = self.parser.parse_insert(command)
                return self.engine.insert_row(table_name, values)

            elif command.startswith("SELECT"):
                table_name, columns, where_condition = self.parser.parse_select(command)
                return self.engine.select_rows(table_name, columns, where_condition)

            elif command.startswith("UPDATE"):
                table_name, updates, where_condition = self.parser.parse_update(command)
                return self.engine.update_rows(table_name, updates, where_condition)

            elif command.startswith("DELETE FROM"):
                table_name, where_condition = self.parser.parse_delete(command)
                return self.engine.delete_rows(table_name, where_condition)

            else:
                return "Error: Unknown command"

        except Exception as e:
            return f"Error: {str(e)}"

    def get_table_info(self) -> dict:
        return self.file_manager.read_table_metadata()
