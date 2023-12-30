from pathlib import Path


class DataGenerator:

    def __init__(self, path: str, file_name: str) -> None:
        self.__file_name: str = file_name
        self.__path: Path = Path(path)
       
    
    @property
    def file_name(self) -> str:
        return self.__file_name
        
    @file_name.setter
    def file_name(self, file_name:str):
        self.__file_name = file_name

    @property
    def path(self) -> Path:
        return self.__path

    @path.setter
    def path(self, path: str):
        self.__path = Path(path)

    
