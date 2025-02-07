from .base_ui import BaseUi
from .generated import MarketUi




class Market(BaseUi):

    def __init__(self, parent = None):
        super().__init__(parent)
        self.ui = MarketUi()
        self.ui.setupUi(self)