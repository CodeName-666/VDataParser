from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from .base_ui import BaseUi
from .generated import MarketUi
from .market_settings import MarketSetting
from .data_view import DataView
from .user_info import UserInfo



class Market(BaseUi):

    def __init__(self, parent = None):
        super().__init__(parent)
        self.ui = MarketUi()
        self.marktSettings: MarketSetting = None
        self.dataView: DataView = None
        self.userInfo: UserInfo = None

        self.marktSettingsLayout: QVBoxLayout = None
        self.dataViewLayout : QVBoxLayout = None
        self.userInfoLayout : QVBoxLayout = None

    def setupUi(self):
        self.ui.setupUi(self)

        self.marktSettingsLayout = self.ui.tab.layout()
        if self.marktSettingsLayout is None:
            self.marktSettingsLayout = QVBoxLayout(self.ui.tab)
            self.marktSettings = MarketSetting(self.marktSettingsLayout)
            self.marktSettingsLayout.addWidget(self.marktSettings)
            self.ui.tab.setLayout(self.marktSettingsLayout )
    
        self.dataViewLayout = self.ui.tab_2.layout()
        if self.dataViewLayout is None:
            self.dataViewLayout = QVBoxLayout(self.ui.tab_2)
            self.dataView = DataView(self.dataViewLayout)
            self.dataViewLayout.addWidget(self.dataView)
            self.ui.tab_2.setLayout(self.dataViewLayout )

        self.userInfoLayout = self.ui.tab_3.layout()
        if self.userInfoLayout is None:
            self.userInfoLayout = QVBoxLayout(self.ui.tab_3)
            self.userInfo = UserInfo(self.userInfoLayout)
            self.userInfoLayout.addWidget(self.userInfo)
            self.ui.tab_3.setLayout(self.userInfoLayout )
    
