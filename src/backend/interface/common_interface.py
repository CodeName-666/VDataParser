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
    """Abstract interface defining the required operations for a DB backend."""
    def __init__(self, params: dict):
        self.params = params

    @abc.abstractmethod
    def connect_db(self, database_override: str = None):
        """Connect to the database and return the connection object."""
        pass

    @abc.abstractmethod
    def disconnect_db(self, conn):
        """Close the provided connection."""
        pass

    @abc.abstractmethod
    def execute_db_query(self, conn, query: str, params: tuple = None, fetch: str = None):
        """Execute ``query`` on ``conn`` and optionally return results."""
        pass

    @abc.abstractmethod
    def check_database_exists(self, db_name: str) -> bool:
        """Return ``True`` if the database ``db_name`` exists."""
        pass

    @abc.abstractmethod
    def create_db(self, new_db_name: str):
        """Create a new database if it does not already exist."""
        pass

    @abc.abstractmethod
    def get_placeholder_style(self) -> str:
        """Return the placeholder style used by this DB (``"%s"`` or ``"?"``)."""
        pass

    @abc.abstractmethod
    def get_db_specific_error_types(self) -> tuple:
        """Return a tuple of DB specific exception classes."""
        pass
