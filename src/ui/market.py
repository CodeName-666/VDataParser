from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from .base_ui import BaseUi
from .generated import MarketUi
from .market_settings import MarketSetting
from .data_view import DataView
from .user_info import UserInfo
from typing import Type, TypeVar
from data import DataManager

#T = TypeVar('T')


class Market(BaseUi):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = MarketUi()
        self.setup_ui()

    
    def set_data(self, data_manager: DataManager):
        self.data_manager = data_manager
        #self.market_setting.set_data(data_manager)
        self.data_view.set_data(data_manager)
        self.user_info.set_data(data_manager)

    def setup_ui(self):
        self.ui.setupUi(self)
        self.market_setting = self.add_widget(self.ui.tab, MarketSetting)
        self.data_view = self.add_widget(self.ui.tab_2, DataView)
        self.user_info = self.add_widget(self.ui.tab_3, UserInfo)
