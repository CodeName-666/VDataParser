from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel 
from PySide6.QtCore import Slot
from .base_ui import BaseUi
from .generated import MarketUi
from .market_settings import MarketSetting
from .data_view import DataView
from .user_info import UserInfo
from typing import Type, TypeVar
from data import DataManager



class Market(BaseUi):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.data_manager_ref: DataManager = None  # Initialize DataManager as None
        self.ui = MarketUi()
        self.setup_ui()

    @Slot(DataManager)
    def set_data(self, data_manager: DataManager):
        self.data_manager_ref = data_manager
        #self.market_setting.set_data(data_manager)
        self.data_view.setup_views()
        self.user_info.setup_views()

    def setup_ui(self):
        self.ui.setupUi(self)
        self.market_setting = self.add_widget(self.ui.tab, MarketSetting)
        self.data_view = self.add_widget(self.ui.tab_2, DataView)
        self.user_info = self.add_widget(self.ui.tab_3, UserInfo)

    def get_user_data(self):
        """
        Retrieves user data from the DataManager.
        Returns:
            dict: A dictionary containing user data.
        """
        if not self.data_manager_ref:
            return {}
        return self.data_manager_ref.get_users_data()
    
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
            return {}
        return self.data_manager_ref.get_seller_list()
    
    def get_main_numers(self):
        """
        Retrieves main numbers from the DataManager.
        Returns:
            dict: A dictionary containing main numbers.
        """
        if not self.data_manager_ref:
            return {}
        return self.data_manager_ref.get_main_number_tables()