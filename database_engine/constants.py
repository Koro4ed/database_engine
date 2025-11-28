# File paths
DB_META_FILE = "db_meta.json"
DATA_DIR = "data"

# Table constants
ID_COLUMN = "id"
ID_TYPE = "int"
DEFAULT_COLUMNS = {ID_COLUMN: ID_TYPE}

# Data types
SUPPORTED_TYPES = {"int", "str", "float", "bool"}

# Messages
SUCCESS_MESSAGES = {
    "table_created": "Table created successfully",
    "table_dropped": "Table dropped successfully",
    "row_inserted": "Row inserted successfully",
    "rows_updated": " rows updated",
    "rows_deleted": " rows deleted",
}

ERROR_MESSAGES = {
    "table_exists": "Table already exists",
    "table_not_exists": "Table does not exist",
    "invalid_type": "Invalid data type",
    "invalid_syntax": "Invalid syntax",
}
