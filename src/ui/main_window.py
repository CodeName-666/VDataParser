from PySide6.QtCore import Qt
from PySide6.QtWidgets import QMainWindow,  QStackedWidget
from .stack_widget import StackWidget
from .generated import MainWindowUi
from .main_menu import MainMenu
from .data_view import DataView
from .market import Market





class MainWindow(QMainWindow): 

    
    def __init__(self, parent=None, flags=Qt.WindowFlags()):  
        super().__init__(parent, flags)
        self.ui = MainWindowUi()
        self.stack = StackWidget() 
        self.main_menu = MainMenu(self.stack) 
        self.data_view = DataView(self.stack)
        self.market_view = Market(self.stack)     


    def setup_ui(self):
        
        self.ui.setupUi(self)   
        self.main_menu.setup_ui()
        self.data_view.setup_ui()
        self.market_view.setup_ui()
                
        self.stack.addWidget(self.main_menu)
        self.stack.addWidget(self.data_view)
        self.stack.addWidget(self.market_view)
        
        # Das QStackedWidget als zentrales Widget setzen
        self.setCentralWidget(self.stack)

        self.hide_toolbars()
        self.setup_signals()

    def setup_signals(self):

        self.main_menu.on_exit_button_clicked.connect(self.close)
        self.main_menu.on_export_button_clicked.connect(self.open_market_view)
        self.ui.action_open_export.triggered.connect(self.open_market_view)

    def open_market_view(self):
        self.stack.setCurrentIndex(2)
        self.ui.tool_export.setVisible(True)
        
    def open_new_market(self):
        pass 

    def open_load_market(self):
        pass

    def hide_toolbars(self):
        self.ui.tool_export.setVisible(False)

    def show_toolbars(self, view_name: str):
        if view_name == "";