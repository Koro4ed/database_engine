# Database Engine

A simple file-based database engine with SQL-like syntax implemented in Python. This project provides a lightweight, file-based database system that supports basic SQL operations with a command-line interface.

## Features

### Database Operations
- **Table Management**: CREATE TABLE, DROP TABLE, LIST TABLES
- **CRUD Operations**: INSERT, SELECT, UPDATE, DELETE
- **Data Filtering**: WHERE clauses with comparison operators (=, !=, >, <, >=, <=)
- **Data Validation**: Automatic type checking and casting

### Supported Data Types
- `int` - Integer numbers
- `str` - Text strings (use quotes: "hello" or 'world')
- `float` - Floating point numbers  
- `bool` - Boolean values (true/false)

### Advanced Features
- Automatic ID column generation for all tables
- Command history and auto-suggestions
- Pretty table formatting for query results
- Execution time measurement
- Safe operations with confirmation prompts
- Comprehensive error handling

## Installation

### Prerequisites
- Python 3.8 or higher
- Poetry (dependency management)

### Step-by-Step Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/Koro4ed/database_engine.git
   cd database_engine
2. **make install**:
    This command will:
    Install Poetry if not present
    Set up the virtual environment
    Install all required dependencies

### Usage

**Starting the Database Engine**:
1. **Using Make (recommended)**:
bash
make project

2. **Using Poetry directly:**:
bash
poetry run project

### Available Commands

-- Create a new table
CREATE TABLE users (name str, age int, active bool)

-- List all tables
LIST TABLES

-- Delete a table
DROP TABLE users

-- Insert data
INSERT INTO users VALUES ("Alice", 25, true)
INSERT INTO users VALUES ("Bob", 30, false)

-- Query data
SELECT * FROM users
SELECT name, age FROM users WHERE age > 25
SELECT * FROM users WHERE active = true

-- Update data
UPDATE users SET age = 26 WHERE name = "Alice"
UPDATE users SET active = false WHERE age > 60

-- Delete data
DELETE FROM users WHERE active = false
DELETE FROM users  -- Delete all rows (requires confirmation)

EXIT  -- Exit the application
HELP  -- Show help message

### Project Structure

database_engine/
├── database_engine/          # Main package
│   ├── __init__.py          # Package initialization
│   ├── main.py              # CLI interface and user interaction
│   ├── engine.py            # Database session management
│   ├── core.py              # Core database operations
│   ├── parser.py            # SQL command parsing
│   ├── utils.py             # File operations and validation
│   ├── decorators.py        # Custom decorators
│   └── constants.py         # Constants and configuration
├── README.md                # This file
├── pyproject.toml           # Project dependencies and configuration
├── Makefile                 # Development commands
└── .gitignore              # Git ignore rules

### Code Quality

Run linter: make lint

Format code: make format

Build package: make build

Clean project: make clean

## Demo

Watch the full demo showing all features in action:
https://asciinema.org/a/afpn7J79DEkAESeJ5tLy2mN9W
