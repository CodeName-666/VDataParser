
from .data_manager import DataManager
from .market_loader import MarketHandler
from .singelton_meta import SingletonMeta
from generator import FileGenerator
from typing import List, Dict, Any, Union



class MarketObserver:

    def __init__(self,market):
        self.market = market
        self.market_handler = MarketHandler()
        self.data_manager = DataManager()
        self.file_generator = None
        
    
    def load_local(self, json_path: str) -> None:
        """
        Load local JSON data.

        :param json_path: Path to the local JSON file.
        """
        self.data_manager.load(json_path)
        self.market_handler.set_full_market_path(json_path)
        self.file_generator = FileGenerator(self.data_manager)

    def get_data(self):
        return self.data_manager
    



class MarketFacade(metaclass=SingletonMeta):
    """
    A facade for market operations, providing a simplified interface to interact with market data.
    """

    def __init__(self):
        super().__init__()
        self._market_list: List = []
        
    
    def new_market(self, market) -> None:
        """
        Create a new market instance.

        :param market_name: Name of the new market.
        """
        self.market = self._market_list.append(market)
        self._market_list.append(MarketObserver(self.market))

    def load_online_market(self,market, json_path: str) -> None:
        """
        Load a project from a JSON file.

        :param json_path: Path to the JSON file containing project data.
        """
        
        pass

    def load_local_market(self,market, json_path: str) -> None:
        """
        Load local JSON data.

        :param json_path: Path to the local JSON file.
        """
        
    def market_already_exists(self, market) -> bool:
        market = next(((mk, obs)[0] for mk, obs in self._market_list if mk == market), None)
        if market is not None:
            return True
        return False

    def get_observer(self, market):
        """
        Retrieve the observer for the specified market.

        :param market: The market instance to observe.
        :return: The observer instance for the market, or None if not found.
        """
        for mk, observer in self._market_list:
            if mk == market:
                return observer
        return None

    def create_observer(self, market):
        """
        Create an observer for the specified market.

        :param market: The market instance to observe.
        :return: An observer instance for the market.
        """
        observer = MarketObserver(market)
        if not self.market_already_exists(market):
            self._market_list.append((market, observer))
        return observer