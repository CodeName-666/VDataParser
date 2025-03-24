from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from .base_ui import BaseUi
from .generated import MarketUi
from .market_settings import MarketSetting
from .data_view import DataView
from .user_info import UserInfo
from typing import Type, TypeVar

T = TypeVar('T')


class Market(BaseUi):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = MarketUi()
   

    def setup_ui(self):
        self.ui.setupUi(self)
        self.__add_widget_to_tab(self.ui.tab, MarketSetting)
        self.__add_widget_to_tab(self.ui.tab_2, DataView)
        self.__add_widget_to_tab(self.ui.tab_3, UserInfo)

    def __add_widget_to_tab(self, tab: QWidget, widgetClass):
        layout = tab.layout()
        if layout is None:
            layout = QVBoxLayout(tab)
            widget = widgetClass()
            layout.addWidget(widget)
            tab.setLayout(layout)
