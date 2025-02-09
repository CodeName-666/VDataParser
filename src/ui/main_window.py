from PySide6.QtCore import Qt
from PySide6.QtWidgets import QMainWindow,  QStackedWidget
from .generated import MainWindowUi
from .main_menu import MainMenu
from .data_view import DataView
from .market import Market





class MainWindow(QMainWindow): 

    
    def __init__(self, parent=None, flags=Qt.WindowFlags()):  
        super().__init__(parent, flags)
        self.ui = MainWindowUi()
        
       
    def setup_ui(self):
        
        self.stack = QStackedWidget() 
        self.main_menu = MainMenu(self.stack) 
        self.data_view = DataView(self.stack)
        self.market_view = Market(self.stack)
        
        self.ui.setupUi(self)         
        self.stack.addWidget(self.main_menu)
        self.stack.addWidget(self.data_view)
        self.stack.addWidget(self.market_view)
        
        # Das QStackedWidget als zentrales Widget setzen
        self.setCentralWidget(self.stack)

    def setup_signals(self):