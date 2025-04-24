# --- data_generator.py ---
from pathlib import Path
from typing import Optional

# Conditional import of CustomLogger
try:
    # Assume logger.py is in the same directory or package
    from log import CustomLogger
except ImportError:
    CustomLogger = None # type: ignore # Allow CustomLogger to be None if import fails

# Conditional import of ProgressTracker
try:
    from .progress_tracker import ProgressTracker
except ImportError:
    ProgressTracker = None # type: ignore

class DataGenerator:
    """
    A base class for data generators, now with optional logging support.

    Attributes:
    -----------
    file_name : str
        The name of the file to be generated (without suffix).
    path : Path
        The path where the file will be saved.
    logger : Optional[CustomLogger]
        An optional logger instance.
    """

    FILE_SUFFIX = '' # Subclasses should define this

    def __init__(self, path: str, file_name: str, logger: Optional[CustomLogger] = None) -> None:
        """
        Initializes the DataGenerator with path, file name, and optional logger.

        Parameters:
        -----------
        path : str
            The path where the file will be saved.
        file_name : str
            The name of the file to be generated (without suffix).
        logger : Optional[CustomLogger], optional
            A CustomLogger instance for logging, defaults to None (no logging).
        """
        self.__file_name: str = file_name
        self.__path: Path = Path(path) if path else Path('.')
        self.logger = logger # Store the logger instance

    def _log(self, level: str, message: str, on_verbose: bool = False) -> None:
        """ Helper method for conditional logging. """
        if self.logger:
            # Get the appropriate logging method (info, warning, error, debug)
            log_method = getattr(self.logger, level.lower(), None)
            if log_method and callable(log_method):
                try:
                    # Call the logger's method, passing on_verbose if applicable
                    # Check if the logger method accepts on_verbose
                    # A simpler approach is to let the CustomLogger handle on_verbose internally
                    if level.lower() in ["debug", "info", "warning", "error"]:
                         # Use the specific methods of CustomLogger which handle on_verbose
                         log_method(message, on_verbose=on_verbose)
                    else:
                         # Fallback for potentially custom levels (though unlikely here)
                         log_method(message) # Assuming basic logging call
                except Exception as e:
                     # Fallback: If logging itself fails, print to stderr
                     import sys
                     print(f"LOGGING FAILED ({level}): {message} | Error: {e}", file=sys.stderr)
            # else: # Optional: Log a warning if an invalid level string is passed
            #    if self.logger: self.logger.warning(f"Invalid log level '{level}' used in _log")

    @property
    def file_name(self) -> str:
        return self.__file_name

    @file_name.setter
    def file_name(self, file_name: str):
        self.__file_name = file_name

    @property
    def path(self) -> Path:
        return self.__path

    @path.setter
    def path(self, path: str):
        self.__path = Path(path) if path else Path('.')

    def get_full_path(self) -> Path:
        if not self.file_name:
             raise ValueError("Dateiname wurde nicht gesetzt.")
        if not self.FILE_SUFFIX:
             # Attempt to log the error if logger exists
             self._log("ERROR", f"FILE_SUFFIX nicht definiert für Klasse {self.__class__.__name__}")
             raise ValueError(f"FILE_SUFFIX wurde in der Unterklasse {self.__class__.__name__} nicht definiert.")
        return self.path / f'{self.file_name}.{self.FILE_SUFFIX}'

    def generate(self, overall_tracker: Optional[ProgressTracker] = None) -> None:
         self._log("ERROR", "Die Methode 'generate' muss in der Unterklasse implementiert werden.")
         raise NotImplementedError("Die Methode 'generate' muss in der Unterklasse implementiert werden.")

    def write(self, *args, **kwargs) -> None: # Allow args/kwargs for flexibility
         # Base implementation does nothing, subclasses might override
         pass