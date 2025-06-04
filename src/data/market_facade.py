
from .data_manager import DataManager
from .project_manager import ProjectManager
from generator import FileGenerator


class MarketFacade:
    """
    A facade for market operations, providing a simplified interface to interact with market data.
    """

    def __init__(self, market):
        self.project_manager = ProjectManager()
        self.data_manager = DataManager()
        self.file_generator = FileGenerator()   
        """
        Initialize the MarketFacade with a market instance.

        :param market: An instance of a market class that provides access to market data.
        """
        self.market = market

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