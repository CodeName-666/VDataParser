
from .data_manager import DataManager
from .project_manager import ProjectLoader
from .singelton_meta import SingletonMeta
from generator import FileGenerator



class Project:

    def __init__(self,market):
        self.market = market
        self.project_manager = ProjectLoader()
        self.data_manager = DataManager()
        self.file_generator = FileGenerator()  
        



class MarketFacade(metaclass=SingletonMeta):
    """
    A facade for market operations, providing a simplified interface to interact with market data.
    """

    def __init__(self, market):
        super().__init__()
        self._project_list: Project = []
        

    def get_market_data(self, symbol):
        """
        Retrieve market data for a given symbol.

        :param symbol: The symbol for which to retrieve market data.
        :return: Market data for the specified symbol.
        """
        return self.market.get_data(symbol)
    

    def load_project(self, json_path: str) -> None:
        """
        Load a project from a JSON file.

        :param json_path: Path to the JSON file containing project data.
        """
        self.project_manager.load_project(json_path)