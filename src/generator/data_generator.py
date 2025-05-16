from pathlib import Path
from typing import Optional
from log import CustomLogger
from display import ProgressTrackerAbstraction
from display import OutputInterfaceAbstraction
from data import Base


class DataGenerator(Base):
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
