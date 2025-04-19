import importlib
import abc  # Abstract Base Classes



# --- Custom Exceptions ---
class DatabaseConnectionError(Exception):
    """Custom exception for database connection errors."""
    pass

class DatabaseQueryError(Exception):
    """Custom exception for query execution errors."""
    pass

# --- Abstract Database Operations Interface ---
class DatabaseOperations(abc.ABC):
    """
    Abstrakte Basisklasse (oder Interface via Duck Typing),
    die die erforderlichen Operationen für einen DB-Typ definiert.
    """
    def __init__(self, params: dict):
        self.params = params

    @abc.abstractmethod
    def connect_db(self, database_override: str = None):
        """Stellt die Verbindung her und gibt das Connection-Objekt zurück."""
        pass

    @abc.abstractmethod
    def disconnect_db(self, conn):
        """Trennt die gegebene Verbindung."""
        pass

    @abc.abstractmethod
    def execute_db_query(self, conn, query: str, params: tuple = None, fetch: str = None):
        """Führt eine Abfrage auf der gegebenen Verbindung aus."""
        pass

    @abc.abstractmethod
    def check_database_exists(self, db_name: str) -> bool:
        """Prüft, ob eine Datenbank existiert."""
        pass

    @abc.abstractmethod
    def create_db(self, new_db_name: str):
        """Erstellt eine neue Datenbank."""
        pass

    @abc.abstractmethod
    def get_placeholder_style(self) -> str:
        """Gibt den Platzhalterstil zurück ('%s' oder '?')."""
        pass

    @abc.abstractmethod
    def get_db_specific_error_types(self) -> tuple:
        """Gibt ein Tupel der spezifischen DB-Fehlerklassen zurück."""
        pass
