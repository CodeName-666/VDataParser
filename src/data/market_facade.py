
from .data_manager import DataManager
from .market_loader import MarketLoader
from .singelton_meta import SingletonMeta
from generator import FileGenerator



class MarketData:

    def __init__(self,market):
        self.market = market
        self.project_manager = MarketLoader()
        self.data_manager = DataManager()
        self.file_generator = None
        
    
    def load_
    



class MarketFacade(metaclass=SingletonMeta):
    """
    A facade for market operations, providing a simplified interface to interact with market data.
    """

    def __init__(self, market):
        super().__init__()
        self._market_list: MarketData = []
        

    def get_market_data(self, symbol):
        """
        Retrieve market data for a given symbol.

        :param symbol: The symbol for which to retrieve market data.
        :return: Market data for the specified symbol.
        """
        return self.market.get_data(symbol)
    
    def new_market(self, market) -> None:
        """
        Create a new market instance.

        :param market_name: Name of the new market.
        """
        self.market = self._market_list.append(market)
        self._market_list.append(MarketData(self.market))

    def load_online_market(self, json_path: str) -> None:
        """
        Load a project from a JSON file.

        :param json_path: Path to the JSON file containing project data.
        """
        
        pass

    def load_local_market(self, json_path: str) -> None:
        """
        Load local JSON data.

        :param json_path: Path to the local JSON file.
        """
        pass
    