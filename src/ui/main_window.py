from PySide6.QtCore import Qt
from PySide6.QtWidgets import QMainWindow,  QStackedWidget
from .generated import MainWindowUi
from .main_menu import MainMenu
from .data_view import DataView





class MainWindow(QMainWindow): 

    
    def __init__(self, parent=None, flags=Qt.WindowFlags()):  
        super().__init__(parent, flags)
        self.ui = MainWindowUi()
        
       
    def setupUi(self):
        self.stack = QStackedWidget() 
        self.main_menu = MainMenu(self.stack) 
        self.data_view = DataView(self.stack)
        
        self.ui.setupUi(self)         
        self.stack.addWidget(self.main_menu)
        self.stack.addWidget(self.data_view)
        
        # Das QStackedWidget als zentrales Widget setzen
        self.setCentralWidget(self.stack)
