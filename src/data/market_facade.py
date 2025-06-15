
from PySide6.QtCore import QObject, Slot
from .data_manager import DataManager
from .market_loader import MarketHandler
from .singelton_meta import SingletonMeta
from .pdf_display_config import PdfDisplayConfig
from generator import FileGenerator
from objects import FleatMarket
from typing import List, Dict, Any, Union


class MarketObserver:

    def __init__(self,market = None, json_path: str = ""):
        """

        Initialize the MarketObserver with a JSON path.
        :param json_path: Path to the JSON file.
        """
        self.market_handler: MarketHandler = MarketHandler()
        self.data_manager: DataManager = DataManager()
        self.pdf_display_config_loader: PdfDisplayConfig = PdfDisplayConfig()
        self.file_generator: FileGenerator = None
        self.fm: FleatMarket = None

        if market is not None and json_path:
            # If a market is provided, set up the observer with the market and JSON path
            self.setup_observer(market, json_path)
        

    def setup_observer(self,market, json_path: str) -> None:
        """
        Setup the data manager with the given JSON path.

        :param json_path: Path to the JSON file.
        """
        if json_path:
            self.connect_signals(market)
            market_path = self.market_handler.get_full_market_path()
            self.data_manager.load(market_path)

            pdf_display_config = self.market_handler.get_full_pdf_coordinates_config_path()
            self.pdf_display_config_loader.load(pdf_display_config)


            self.fm: FleatMarket = FleatMarket()
            self.fm.load_sellers(self.data_manager.get_seller_as_list())
            self.fm.load_main_numbers(
                self.data_manager.get_main_number_as_list())
            self.file_generator = FileGenerator(self.fm)

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
        self.data_manager.data_loaded.connect(market.set_market_data)
        self.pdf_display_config_loader.data_loaded.connect(
            market.set_pdf_config)


class MarketFacade(metaclass=SingletonMeta):
    """
    A facade for market operations, providing a simplified interface to interact with market data.
    """

    def __init__(self):
        super().__init__()
        self._market_list: List = []

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

        new_observer = self.create_observer(market, json_path)
        ret = new_observer.load_local_market_project(json_path)
    
        return ret

    def load_local_market_export(self, market, json_path: str) -> None:
        """
        Load local JSON data.

        :param json_path: Path to the local JSON file.
        """
        new_observer = self.create_observer(market)
        new_observer.load_local_market_export(json_path)

    def market_already_exists(self, market) -> bool:
        market = next(
            ((mk, obs)[0] for mk, obs in self._market_list if mk == market), None)
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

    def create_observer(self, market, json_path ="") -> MarketObserver:
        """
        Create an observer for the specified market.

        :param market: The market instance to observe.
        :return: An observer instance for the market.
        """

        if not self.market_already_exists(market):
            observer = MarketObserver()
            observer.setup_observer(market, json_path)
            self._market_list.append((market, observer))
        else:
            observer = self.get_observer(market)
        return observer
