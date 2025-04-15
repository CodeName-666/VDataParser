import importlib

from .common_interface import (
    DatabaseConnectionError,
    DatabaseQueryError,
    DatabaseOperations
    )


from .mysql_interface import MYSQL_AVAILABLE
from .sqlite_interface import SQLiteInterface
from .mysql_interface import MySQLInterface


# --- Import der spezifischen DB-Implementierungen ---
def import_db_connector(db_type: str):
    """
    Importiert den spezifischen DB-Connector basierend auf dem Typ.
    """
    try:
        module = importlib.import_module(f"src.backend.interface.{db_type}_interface")
        return getattr(module, f"{db_type.capitalize()}Connector")
    except ImportError as e:
        raise ImportError(f"Fehler beim Importieren des Moduls für '{db_type}': {e}") from e
    