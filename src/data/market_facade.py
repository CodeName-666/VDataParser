
"""High level facade combining various market related components."""

from PySide6.QtCore import QObject, Slot, Signal
from .data_manager import DataManager
from .market_config_handler import MarketConfigHandler
from .singelton_meta import SingletonMeta
from .pdf_display_config import PdfDisplayConfig
from generator import FileGenerator
from objects import FleatMarket
from typing import List, Dict, Any, Union
import tempfile
import os
from backend import MySQLInterface
from backend.advance_db_connector import AdvancedDBManager


class MarketObserver(QObject):

    status_info = Signal(str, str)
    data_manager_loaded = Signal(object)
    pdf_display_config_loaded = Signal(object)

    def __init__(self, market = None, json_path: str = ""):
        """

        Initialize the MarketObserver with a JSON path.
        :param json_path: Path to the JSON file.
        """
        QObject.__init__(self)
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
                    if not self.data_manager.settings_available():
                        default_settings = self.market_config_handler.get_default_settings()
                        self.data_manager.set_default_settings(default_settings)
                        self.status_info.emit("WARNING", f"Keine Settings gefunden. Default Einstellungen wurden geladen.")
                    # Setup the FleatMarket with the loaded data
                    self.data_manager_loaded.emit(self.data_manager)
                    self.setup_data_generation()

                    self.status_info.emit("INFO", f"Projekt geladen: {json_path}")
                else:
                    self.status_info.emit("ERROR", "Daten konnten nicht geladen werden")
                # Load the PDF display configuration
                ret = self.pdf_display_config_loader.load(pdf_display_config)
                if ret:
                    self.pdf_display_config_loaded.emit(self.pdf_display_config_loader)

            else:
                self.status_info.emit("ERROR", "Projektkonfiguration konnte nicht geladen werden")

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
                self.data_manager_loaded.emit(self.data_manager)
                self.pdf_display_config_loaded.emit(self.pdf_display_config_loader) # Send empty config
                self.setup_data_generation()
                self.status_info.emit("INFO", f"Export geladen: {json_path}")
            else:
                self.status_info.emit("ERROR", "Export konnte nicht geladen werden")

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

    @Slot(str)
    def storage_path_changed(self,path: str):
        self.market_config_handler.set_full_pdf_coordinates_config_path(path)
        print("PAUSE")

    def get_data(self):
        return self.data_manager

    def get_pdf_data(self) -> Dict[str, Any]:
        """
        Retrieve data for PDF generation.

        :return: A dictionary containing data for PDF generation.
        """
        return self.market_config_handler.get_pdf_generation_data()

    def connect_signals(self, market) -> None:
        self.data_manager_loaded.connect(market.set_market_data)
        self.pdf_display_config_loaded.connect(market.set_pdf_config)
       
        market.pdf_display_storage_path_changed.connect(self.storage_path_changed)


    def generate_pdf_data(self) -> None:
        """
        Generate PDF data for the market.
        This method should be implemented to create the necessary PDF data.
        """
        if self._data_ready:
            self.file_generator.create_pdf_data(self.market_config_handler.get_pdf_generation_data())

    def generate_seller_data(self) -> None:
        """Generate seller related data files (DAT, statistics, etc.)."""
        if self._data_ready:
            self.file_generator.create_seller_data()

    def generate_all(self) -> None:
        """Generate all data and the PDF using stored settings."""
        if self._data_ready:
            self.file_generator.create_all(self.market_config_handler.get_pdf_generation_data())
        
        

class MarketFacade(QObject, metaclass=SingletonMeta):
    """
    A facade for market operations, providing a simplified interface to interact with market data.
    """

    status_info = Signal(str, str)

    def __init__(self):

        QObject.__init__(self)


        self._market_list: List = []

    def load_online_market(self, market, info: dict) -> bool:
        """Load market data from a MySQL database.

        Parameters
        ----------
        market:
            Target :class:`Market` view.
        info:
            Dictionary containing connection parameters (host, port, database,
            user and password).
        """

        host = info.get("host")
        port = info.get("port")
        database = info.get("database")
        user = info.get("user")
        password = info.get("password")

        tmp_path = None
        ret = False
        try:
            mysql_if = MySQLInterface(host=host, user=user, password=password,
                                      database=database, port=port)
            with AdvancedDBManager(mysql_if) as db:
                fd, tmp_path = tempfile.mkstemp(suffix=".json")
                os.close(fd)
                db.export_to_custom_json(tmp_path)

            new_observer = self.create_observer(market)
            new_observer.connect_signals(market)
            ret = new_observer.load_local_market_export(tmp_path)

            if ret:
                self.status_info.emit(
                    "INFO",
                    f"Online-Datenbank geladen: {database}@{host}:{port}"
                )
            else:
                self.status_info.emit("ERROR", "Daten konnten nicht geladen werden")
        except Exception as e:
            self.status_info.emit("ERROR", f"Fehler beim Laden der Datenbank: {e}")
            ret = False
        finally:
            if tmp_path and os.path.exists(tmp_path):
                try:
                    os.remove(tmp_path)
                except OSError:
                    pass
        return ret

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
            observer.status_info.connect(self.status_info)
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
        observer = self.get_observer(market)
        if not observer:
            self.status_info.emit("ERROR", "Kein Observer gefunden")
            return
        try:
            observer.generate_pdf_data()
            self.status_info.emit("INFO", "PDF Daten generiert")
        except Exception as err:  # pragma: no cover - runtime errors handled
            self.status_info.emit("ERROR", str(err))

    @Slot(object)
    def create_seller_data(self, market) -> None:
        """Create seller related data files for the specified market."""
        observer = self.get_observer(market)
        if not observer:
            self.status_info.emit("ERROR", "Kein Observer gefunden")
            return
        try:
            observer.generate_seller_data()
            self.status_info.emit("INFO", "Verkäuferdaten generiert")
        except Exception as err:  # pragma: no cover - runtime errors handled
            self.status_info.emit("ERROR", str(err))
    
    @Slot(object)
    def create_market_data(self, market) -> None:
        """
        Create market data for the specified market.

        :param market: The market instance for which to create data.
        """
        observer = self.get_observer(market)
        if not observer:
            self.status_info.emit("ERROR", "Market observer not found")
            return
        try:
            market.set_data(observer.get_data())
            self.status_info.emit("INFO", "Marktdaten generiert")
        except Exception as err:  # pragma: no cover - runtime errors handled
            self.status_info.emit("ERROR", str(err))
        

    @Slot(object)
    def create_all_data(self, market) -> None:
        """
        Create all data for the specified market.

        :param market: The market instance for which to create all data.
        """
        observer = self.get_observer(market)
        if not observer:
            self.status_info.emit("ERROR", "Kein Observer gefunden")
            return
        try:
            if observer.file_generator:
                observer.generate_all()
                self.status_info.emit("INFO", "Alle Daten erstellt")
            else:
                raise RuntimeError("FileGenerator nicht bereit")
        except Exception as err:  # pragma: no cover - runtime errors handled
            self.status_info.emit("ERROR", str(err))

    def is_project(self, market) -> bool:
        """
        Check if a project exists for the specified market.

        :param market: The market instance to check.
        :return: True if a project exists, False otherwise.
        """
        observer: MarketObserver = self.get_observer(market)
        if observer:
            return observer.project_exists()
        return False
