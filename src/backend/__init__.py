"""Database backends and connector interfaces.

Exports common exceptions, the abstract DB API, availability flags, and
concrete SQLite/MySQL connectors.
"""

from .interface import (
    DatabaseConnectionError,
    DatabaseQueryError,
    DatabaseOperations,
    MYSQL_AVAILABLE,
)

from .interface import SQLiteInterface, MySQLInterface

__all__ = [
    "DatabaseConnectionError",
    "DatabaseQueryError",
    "DatabaseOperations",
    "MYSQL_AVAILABLE",
    "SQLiteInterface",
    "MySQLInterface",
]
