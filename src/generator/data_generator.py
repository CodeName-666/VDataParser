# --- data_generator.py ---
from pathlib import Path
from typing import Optional

# Assume logger.py exists
try:
    from log import CustomLogger
except ImportError:
    CustomLogger = None  # type: ignore

# Assume progress_tracker.py exists
try:
    from src.display import ProgressTrackerAbstraction
except ImportError:
    ProgressTrackerAbstraction = None  # type: ignore

# Import the abstraction
try:
    # Assuming output_interface.py is accessible, adjust path if needed
    from src.display import OutputInterfaceAbstraction
except ImportError:
    OutputInterfaceAbstraction = None  # type: ignore


class DataGenerator:
    """
    A base class for data generators, with optional logging and user output interface support.

    Attributes:
    -----------
    file_name : str
        The name of the file to be generated (without suffix).
    path : Path
        The path where the file will be saved.
    logger : Optional[CustomLogger]
        An optional logger instance.
    output_interface : Optional[OutputInterfaceAbstraction]
        An optional interface for user-facing output.
    """

    FILE_SUFFIX = ''  # Subclasses should define this

    def __init__(self,
                 path: str,
                 file_name: str,
                 logger: Optional[CustomLogger] = None,
                 output_interface: Optional[OutputInterfaceAbstraction] = None  # Added
                 ) -> None:
        """
        Initializes the DataGenerator with path, file name, logger, and output interface.

        Parameters:
        -----------
        path : str
            The path where the file will be saved.
        file_name : str
            The name of the file to be generated (without suffix).
        logger : Optional[CustomLogger], optional
            A CustomLogger instance for logging.
        output_interface : Optional[OutputInterfaceAbstraction], optional
            An interface for user-facing output.
        """
        self.__file_name: str = file_name
        self.__path: Path = Path(path) if path else Path('.')
        self.logger = logger  # Store the logger instance
        self.output_interface = output_interface  # Store the output interface instance

    def _log(self, level: str, message: str, on_verbose: bool = False) -> None:
        """ Helper method for conditional logging ONLY. """
        if self.logger:
            log_method = getattr(self.logger, level.lower(), None)
            if log_method and callable(log_method):
                try:
                    if level.lower() in ["debug", "info", "warning", "error"]:
                        log_method(message, on_verbose=on_verbose)
                    else:
                        log_method(message)
                except Exception as e:
                    import sys
                    print(f"LOGGING FAILED ({level}): {message} | Error: {e}", file=sys.stderr)

    def _output(self, message: str) -> None:
        """ Helper method to write ONLY to the output interface. """
        if self.output_interface:
            try:
                self.output_interface.write_message(message)
            except Exception as e:
                # Log error if output fails? Or just print?
                self._log("ERROR", f"Failed to write message to output interface: {e}")
                # Or print to stderr as a last resort
                # import sys
                # print(f"OUTPUT INTERFACE FAILED: {message} | Error: {e}", file=sys.stderr)

    def _output_and_log(self, level: str, message: str, on_verbose: bool = False) -> None:
        """
        Helper method for sending messages to BOTH logger and output interface.
        Typically used for INFO, WARNING, ERROR level messages relevant to the user.
        """
        # Log first
        self._log(level, message, on_verbose)

        # Then output to user interface (usually only for non-debug levels)
        if level.upper() in ["INFO", "WARNING", "ERROR", "CRITICAL"]:
            self._output(message)  # Send the same message to the user output

    # --- Properties (file_name, path) remain the same ---
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
            # Use _output_and_log for user-visible errors if interface exists
            err_msg = "Dateiname wurde nicht gesetzt."
            self._output_and_log("ERROR", err_msg)
            raise ValueError(err_msg)
        if not self.FILE_SUFFIX:
            err_msg = f"FILE_SUFFIX nicht definiert für Klasse {self.__class__.__name__}"
            self._output_and_log("ERROR", err_msg)  # Log and output this critical error
            raise ValueError(err_msg)
        return self.path / f'{self.file_name}.{self.FILE_SUFFIX}'

    def generate(self, overall_tracker: Optional[ProgressTrackerAbstraction] = None) -> None:
        err_msg = "Die Methode 'generate' muss in der Unterklasse implementiert werden."
        self._output_and_log("ERROR", err_msg)  # This is a critical implementation error
        raise NotImplementedError(err_msg)

    def write(self, *args, **kwargs) -> None:
        pass  # Base implementation does nothing
