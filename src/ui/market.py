from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel 
from PySide6.QtCore import Slot, Signal
from .base_ui import BaseUi
from .generated import MarketUi
from .market_settings import MarketSetting
from .data_view import DataView
from .user_info import UserInfo
from .pdf_display import PdfDisplay
from typing import Type, TypeVar
from data import DataManager
from data import PdfDisplayConfig



class Market(BaseUi):

    pdf_display_storage_path_changed = Signal(str) # Signal for storage path changes
    pdf_display_data_changed = Signal(object) # Signal for data changes, e.g., box updates
    status_info = Signal(str, str)  # Signal for status updates

    def __init__(self, parent=None):
        super().__init__(parent)
        self.data_manager_ref: DataManager = None  # Initialize DataManager as None
        self.ui = MarketUi()
        self.setup_ui()

    @Slot(DataManager)
    def set_market_data(self, data_manager: DataManager):
        self.data_manager_ref = data_manager
        self.market_setting.setup_views(self)
        self.data_view.setup_views(self)
        self.user_info.setup_views(self)

    def redirect_signals(self):
        """
        Redirects signals from the PdfDisplay widget to the Market widget.
        This allows the Market widget to handle PDF display events.
        """
        if self.pdf_display:
            self.pdf_display.storage_path_changed.connect(self.pdf_display_storage_path_changed)
            self.pdf_display.data_changed.connect(self.pdf_display_data_changed)
            self.pdf_display.status_info.connect(self.status_info)

    @Slot(object)
    def set_default_settings(self, settings: dict):
        """
        Sets the default settings for the market view.
        This method updates the MarketSetting widget with the provided settings.
        """
        if isinstance(self.market_setting, MarketSetting):
            self.market_setting.set_default_settings(settings)


    @Slot(PdfDisplayConfig)
    def set_pdf_config(self, pdf_config: PdfDisplayConfig):
        """
        Sets the PDF display configuration in the PdfDisplay widget.
        This method retrieves the PDF generation data from the DataManager
        and updates the PdfDisplay widget accordingly.
        """
        self.pdf_display.import_state(pdf_config)

    def setup_ui(self):
        self.ui.setupUi(self)
        self.market_setting = self.add_widget(self.ui.tab, MarketSetting)
        self.data_view = self.add_widget(self.ui.tab_2, DataView)
        self.user_info = self.add_widget(self.ui.tab_3, UserInfo)
        self.pdf_display = self.add_widget(self.ui.tab_4, PdfDisplay)
        self.redirect_signals()

    def get_user_data(self):
        """
        Retrieves user data from the DataManager.
        Returns:
            dict: A dictionary containing user data.
        """
        if not self.data_manager_ref:
            return {}
        return self.data_manager_ref.get_users_data()
    
    def get_aggregated_user_data(self):
        """
        Retrieves aggregated user data from the DataManager.
        Returns:
            dict: A dictionary containing aggregated user data.
        """
        if not self.data_manager_ref:
            return {}
        return self.data_manager_ref.get_aggregated_users_data()

    def get_aggregated_user(self):
        """
        Retrieves aggregated user data from the DataManager.
        Returns:
            dict: A dictionary containing aggregated user data.
        """
        if not self.data_manager_ref:
            return {}
        return self.data_manager_ref.get_aggregated_users()
    
    def get_seller(self):
        """
        Retrieves seller data from the DataManager.
        Returns:
            dict: A dictionary containing seller data.
        """
        if not self.data_manager_ref:
            return []
        return self.data_manager_ref.get_seller_as_list()
    
    def get_main_numbers(self):
        """
        Retrieves main numbers from the DataManager.
        Returns:
            dict: A dictionary containing main numbers.
        """
        if not self.data_manager_ref:
            return {}
        return self.data_manager_ref.get_main_number_tables()
    
    def get_settings(self):
        """
        Retrieves settings from the DataManager.
        Returns:
            dict: A dictionary containing settings.
        """
        if not self.data_manager_ref:
            return {}
        return self.data_manager_ref.get_settings()

            