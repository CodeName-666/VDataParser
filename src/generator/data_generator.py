from pathlib import Path

class DataGenerator:
    """
    A base class for data generators.
    
    Attributes:
    -----------
    __file_name : str
        The name of the file to be generated.
    __path : Path
        The path where the file will be saved.
    """

    def __init__(self, path: str, file_name: str) -> None:
        """
        Initializes the DataGenerator with a path and file name.
        
        Parameters:
        -----------
        path : str
            The path where the file will be saved.
        file_name : str
            The name of the file to be generated.
        """
        self.__file_name: str = file_name
        self.__path: Path = Path(path)
    
    @property
    def file_name(self) -> str:
        """
        Gets the file name.
        
        Returns:
        --------
        str
            The name of the file to be generated.
        """
        return self.__file_name
        
    @file_name.setter
    def file_name(self, file_name: str):
        """
        Sets the file name.
        
        Parameters:
        -----------
        file_name : str
            The name of the file to be generated.
        """
        self.__file_name = file_name

    @property
    def path(self) -> Path:
        """
        Gets the path.
        
        Returns:
        --------
        Path
            The path where the file will be saved.
        """
        return self.__path

    @path.setter
    def path(self, path: str):
        """
        Sets the path.
        
        Parameters:
        -----------
        path : str
            The path where the file will be saved.
        """
        self.__path = Path(path)


