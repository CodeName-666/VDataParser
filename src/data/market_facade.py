
from PySide6.QtCore import QObject, Slot
from .data_manager import DataManager
from .market_config_handler import MarketConfigHandler
from .singelton_meta import SingletonMeta
from .pdf_display_config import PdfDisplayConfig
from generator import FileGenerator
from objects import FleatMarket
from typing import List, Dict, Any, Union


class MarketObserver:

    def __init__(self, market = None, json_path: str = ""):
        """

        Initialize the MarketObserver with a JSON path.
        :param json_path: Path to the JSON file.
        """
        self.market_config_handler: MarketConfigHandler = MarketConfigHandler()
        self.data_manager: DataManager = DataManager()
        self.pdf_display_config_loader: PdfDisplayConfig = PdfDisplayConfig()
        self.file_generator: FileGenerator = None
        self.fm: FleatMarket = None
        self._data_ready = False
        self._project_exists = False


    def set_data_ready_satus(self, status: bool) -> None:
        """
        Set the data ready status.
        :param status: Boolean indicating if the data is ready.
        """
        self._data_ready = status
    
    def is_data_ready(self) -> bool:
        """
        Check if the data is ready.
        :return: True if the data is ready, False otherwise.
        """
        return self._data_ready

    def project_exists(self) -> bool:
        """
        Check if a project already exists.
        :return: True if a project exists, False otherwise.
        """
        return self._project_exists
    
    def set_project_exists(self, status: bool) -> None:
        """
        Set the project exists status.
        :param status: Boolean indicating if a project exists.
        """
        self._project_exists = status

    def load_local_market_project(self, json_path: str) -> bool:
        """
        Load a local market project from a JSON file.

        :param json_path: Path to the local JSON file.
        """
        ret = False
        if json_path:
            # Load the market configuration from the provided JSON path    
            ret = self.market_config_handler.load(json_path)
            if ret:
                self._project_exists = True
                market_json_path = self.market_config_handler.get_full_market_path()
                pdf_display_config = self.market_config_handler.get_full_pdf_coordinates_config_path()
                # Initialize the DataManager with the market JSON path
                ret = self.data_manager.load(market_json_path)
                if ret:
                    # Setup the FleatMarket with the loaded data
                    self.setup_data_generation()
                # Load the PDF display configuration
                self.pdf_display_config_loader.load(pdf_display_config)

        return ret

    def load_local_market_export(self, json_path: str) -> bool:
        """
        Load local JSON data.

        :param json_path: Path to the local JSON file.
        """
        ret = False
        if json_path:
            ret = self.data_manager.load(json_path)
            if ret:
                # Setup the FleatMarket with the loaded data
                self.setup_data_generation()

            self.market_config_handler.set_full_market_path(json_path)

            #self.file_generator = FileGenerator(self.data_manager)
        return ret

    @Slot()
    def setup_data_generation(self) -> None:
        
        self._data_ready = True
        self.fm: FleatMarket = FleatMarket()
        self.fm.load_sellers(self.data_manager.get_seller_as_list())
        self.fm.load_main_numbers(self.data_manager.get_main_number_as_list())
        self.file_generator = FileGenerator(self.fm)

    def get_data(self):
        return self.data_manager

    def get_pdf_data(self) -> Dict[str, Any]:
        """
        Retrieve data for PDF generation.

        :return: A dictionary containing data for PDF generation.
        """
        return self.market_config_handler.get_pdf_generation_data()

    def connect_signals(self, market) -> None:
        self.data_manager.data_loaded.connect(market.set_market_data)
        self.data_manager.data_loaded.connect(market.setup_data_generation)

        self.pdf_display_config_loader.data_loaded.connect(market.set_pdf_config)
        self.market_config_handler.default_signal_loaded.connect(market.set_default_settings)

    def generate_pdf_data(self) -> None:
        """
        Generate PDF data for the market.
        This method should be implemented to create the necessary PDF data.
        """
        if self._data_ready:
            self.file_generator.create_pdf_data(self.market_config_handler.get_pdf_generation_data())
        
        

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
        new_observer.connect_signals(market)
        ret = new_observer.load_local_market_project(json_path)
    
        return ret

    def load_local_market_export(self, market, json_path: str) -> bool:
        """
        Load local JSON data.

        :param json_path: Path to the local JSON file.
        """
        new_observer = self.create_observer(market)
        new_observer.connect_signals(market)
        return new_observer.load_local_market_export(json_path)

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
            self._market_list.append((market, observer))
        else:
            observer = self.get_observer(market)
        return observer

    @Slot(object)
    def create_pdf_data(self, market) ->None:
        """
        Create PDF data for the specified market.

        :param market: The market instance for which to create PDF data.
        """
        print("Not implemented yet")
        observer = self.get_observer(market)
        observer.generate_pdf_data()
    
    @Slot(object)
    def create_market_data(self, market) -> None:
        """
        Create market data for the specified market.

        :param market: The market instance for which to create data.
        """
        print("Not implemented yet")
        observer = self.get_observer(market)
        if observer:
            market.set_data(observer.get_data())
        else:
            raise ValueError("Market observer not found.") 
        

    @Slot(object)
    def create_all_data(self, market) -> None:
        """
        Create all data for the specified market.

        :param market: The market instance for which to create all data.
        """
        print("Not implemented yet")