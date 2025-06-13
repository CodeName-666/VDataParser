
from .data_manager import DataManager
from .market_loader import MarketHandler
from .singelton_meta import SingletonMeta
from .pdf_display_config_loader import PdfDisplayConfigLoader
from generator import FileGenerator
from typing import List, Dict, Any, Union



class MarketObserver:

    def __init__(self, json_path: str = ""):
        self.market_handler = MarketHandler(json_path)

        market_path = self.market_handler.get_full_market_path()
        self.data_manager = DataManager(market_path)

        pdf_display_config = self.market_handler.get_full_pdf_coordinates_config_path()
        self.pdf_display_config_loader = PdfDisplayConfigLoader(pdf_display_config)
        
        self.file_generator = None
        
    
    def load_local_market_project(self, json_path: str) -> bool:
        """
        Load a local market project from a JSON file.

        :param json_path: Path to the local JSON file.
        """
        self.market_handler.load(json_path)
        market_json_path = self.market_handler.get_full_market_path()

        return self.data_manager.load(market_json_path)


    def load_local_market_export(self, json_path: str) -> None:
        """
        Load local JSON data.

        :param json_path: Path to the local JSON file.
        """
        self.data_manager.load(json_path)
        self.market_handler.set_full_market_path(json_path)
        self.file_generator = FileGenerator(self.data_manager)
        

    def get_data(self):
        return self.data_manager
    
    def get_pdf_data(self) -> Dict[str, Any]:
        """
        Retrieve data for PDF generation.

        :return: A dictionary containing data for PDF generation.
        """
        return self.market_handler.get_pdf_generation_data()

    def connect_signals(self, market) -> None:	
        self.data_manager.data_loaded.connect(market.set_data)


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

    def load_online_market(self, market, json_path: str) -> None:
        """
        Load a project from a JSON file.

        :param json_path: Path to the JSON file containing project data.
        """
        
        pass
    
    def load_local_market_porject(self, market, json_path: str) -> bool:
        """
        Load a local market project from a JSON file.

        :param json_path: Path to the local JSON file.
        """

        new_observer = self.create_observer(market)
        new_observer.connect_signals(market)
        ret = new_observer.load_local_market_project(json_path)
        if ret:
            market.set_pdf_display_config(new_observer.get_pdf_data())
           
        return ret
        

    def load_local_market_export(self,market, json_path: str) -> None:
        """
        Load local JSON data.

        :param json_path: Path to the local JSON file.
        """
        new_observer = self.create_observer(market)
        new_observer.connect_signals(market)
        new_observer.load_local_market_export(json_path)
        
        
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

    def create_observer(self, market, json_path = "") -> MarketObserver:
        """
        Create an observer for the specified market.

        :param market: The market instance to observe.
        :return: An observer instance for the market.
        """
        
        if not self.market_already_exists(market):
            observer = MarketObserver(json_path)
            self._market_list.append((market, observer))
        else:
            observer = self.get_observer(market)
        return observer
