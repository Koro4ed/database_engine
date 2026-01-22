#Pavlov Arseniy
#Вариант 13-14
#Таблицы коллекции и экспонаты без связей с другими таблицами.

from prompt_toolkit import prompt
from prompt_toolkit.history import FileHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prettytable import PrettyTable

from database_engine.engine import DatabaseSession
from database_engine.decorators import handle_db_errors


class DatabaseCLI:
    """Command Line Interface for the database engine."""

    def __init__(self):
        self.session = DatabaseSession()
        self.history = FileHistory(".db_history")

    def display_results(self, result: any) -> None:
        """Display query results in a formatted table."""
        if isinstance(result, str):
            print(result)
        elif isinstance(result, list):
            if not result:
                print("No results found")
                return

            if isinstance(result[0], dict):
                table = PrettyTable()
                table.field_names = result[0].keys()
                for row in result:
                    table.add_row(row.values())
                print(table)
            else:
                for item in result:
                    print(item)
        else:
            print(result)

    @handle_db_errors
    def run(self) -> None:
        """Run the database CLI."""
        print("Welcome to Simple Database Engine!")
        print("Type 'EXIT' to quit, 'HELP' for commands\n")

        while True:
            try:
                user_input = prompt(
                    "db> ", history=self.history, auto_suggest=AutoSuggestFromHistory()
                ).strip()

                if not user_input:
                    continue

                if user_input.upper() == "EXIT":
                    print("Goodbye!")
                    break
                elif user_input.upper() == "HELP":
                    self.show_help()
                    continue

                result = self.session.execute_command(user_input)
                self.display_results(result)

            except KeyboardInterrupt:
                print("\nUse 'EXIT' to quit")
            except EOFError:
                print("\nGoodbye!")
                break

    def show_help(self) -> None:
        """Show available commands."""
        help_text = """
Available Commands:

- CREATE TABLE table_name (col1 type1, col2 type2, ...)
  Creates a new table with specified columns
  Example: CREATE TABLE users (name str, age int)

- DROP TABLE table_name
  Deletes a table and all its data

- LIST TABLES
  Shows all existing tables

- INSERT INTO table_name VALUES (val1, val2, ...)
  Inserts a new row into the table
  Example: INSERT INTO users VALUES ("John", 25)

- SELECT * FROM table_name [WHERE condition]
  Selects all rows from table
  Example: SELECT * FROM users WHERE age > 20

- SELECT col1, col2 FROM table_name [WHERE condition]
  Selects specific columns from table
  Example: SELECT name, age FROM users

- UPDATE table_name SET col1=val1, col2=val2 [WHERE condition]
  Updates rows in table
  Example: UPDATE users SET age=26 WHERE name="John"

- DELETE FROM table_name [WHERE condition]
  Deletes rows from table
  Example: DELETE FROM users WHERE age < 18

Supported data types: int, str, float, bool
        """
        print(help_text)


def main():
    cli = DatabaseCLI()
    cli.run()


if __name__ == "__main__":
    main()
