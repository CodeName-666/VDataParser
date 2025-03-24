from .base_ui import BaseUi
from .generated import UserInfoUi




class UserInfo(BaseUi):

    def __init__(self, parent = None):
        super().__init__(parent)
        self.ui = UserInfoUi()
        self.ui.setupUi(self)