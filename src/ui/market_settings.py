from .base_ui import BaseUi
from .generated import MarketSettingUi




class MarketSetting(BaseUi):

    def __init__(self, parent = None):
        super().__init__(parent)
        self.ui = MarketSettingUi()
        self.ui.setupUi(self)