# --- data_generator.py ---
from pathlib import Path
from typing import Optional
# Annahme: ProgressTracker existiert im selben Verzeichnis oder im PYTHONPATH
try:
    from .progress_tracker import ProgressTracker
except ImportError:
    # Fallback, falls die Datei einzeln ausgeführt wird (weniger wahrscheinlich)
    ProgressTracker = None

class DataGenerator:
    """
    A base class for data generators.

    Attributes:
    -----------
    __file_name : str
        The name of the file to be generated (without suffix).
    __path : Path
        The path where the file will be saved.
    """

    FILE_SUFFIX = '' # Standardmäßig kein Suffix, Unterklassen sollten dies definieren

    def __init__(self, path: str, file_name: str) -> None:
        """
        Initializes the DataGenerator with a path and file name.

        Parameters:
        -----------
        path : str
            The path where the file will be saved.
        file_name : str
            The name of the file to be generated (without suffix).
        """
        self.__file_name: str = file_name
        # Konvertiere leeren Pfad zu aktuellem Verzeichnis
        self.__path: Path = Path(path) if path else Path('.')

    @property
    def file_name(self) -> str:
        """
        Gets the file name (without suffix).
        """
        return self.__file_name

    @file_name.setter
    def file_name(self, file_name: str):
        """
        Sets the file name (without suffix).
        """
        self.__file_name = file_name

    @property
    def path(self) -> Path:
        """
        Gets the output path.
        """
        return self.__path

    @path.setter
    def path(self, path: str):
        """
        Sets the output path.
        """
        self.__path = Path(path) if path else Path('.')

    def get_full_path(self) -> Path:
        """
        Returns the full path including filename and suffix.
        """
        if not self.file_name:
             raise ValueError("Dateiname wurde nicht gesetzt.")
        if not self.FILE_SUFFIX:
             raise ValueError("FILE_SUFFIX wurde in der Unterklasse nicht definiert.")
        return self.path / f'{self.file_name}.{self.FILE_SUFFIX}'


    def generate(self, overall_tracker: Optional[ProgressTracker] = None) -> None:
         """
         Generates the data. Should be implemented by subclasses.
         If an overall_tracker is provided, it should call overall_tracker.increment() upon completion.
         """
         raise NotImplementedError("Die Methode 'generate' muss in der Unterklasse implementiert werden.")

    def write(self) -> None:
         """
         Writes the generated data. May not be needed if generate handles writing.
         Should be implemented by subclasses if needed.
         """
         # Kann leer bleiben, wenn generate das Schreiben übernimmt
         # Oder raise NotImplementedError, wenn explizites Schreiben erwartet wird
         pass