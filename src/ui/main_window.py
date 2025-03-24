
#PySide6 imports
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QMainWindow,  QMessageBox, QFileDialog

#Local imports
from data import DataManager
from .stack_widget import StackWidget
from .generated import MainWindowUi
from .main_menu import MainMenu
from .data_view import DataView
from .market import Market





class MainWindow(QMainWindow): 
    """ MainWindow is a subclass of QMainWindow that serves as the application's primary window.
    It initializes and manages the user interface components, including a stack widget that
    handles multiple views (such as the main menu, data view, and market view), and the 
    associated toolbars.
    Attributes:
        ui (MainWindowUi): An instance that sets up the UI elements for the main window.
        stack (StackWidget): A widget that manages multiple view widgets allowing easy switching.
        main_menu (MainMenu): The primary menu view of the application.
        data_view (DataView): The view for displaying and interacting with data.
        market_view (Market): The view representing market information.
    Methods:
        __init__(parent=None, flags=Qt.WindowFlags()):
            Initializes the MainWindow, creating UI elements and setting up child views.
        setup_ui():
            Configures the main window's UI by setting up the layout, adding view widgets to the 
            stack, and initializing toolbar visibility and signal connections.
        setup_signals():
            Connects user interface signals (such as button clicks or menu actions) to their
            corresponding slots or methods (e.g., switching views, closing the window).
        open_view(view_name: str):
            Switches the current view within the stack to the one matching the provided view name.
            It iterates over the children in the stack, sets the proper index if the view name matches,
            hides all toolbars, and then shows the toolbars appropriate for that view.
        open_market_view():
            Switches the currently displayed view in the stack to the market view and makes the 
            export toolbar visible.
        open_new_market():
            A placeholder for functionality that would initiate creating a new market.
        open_load_market():
            A placeholder for functionality that would initiate loading a market.
        hide_all_toolbars():
            Hides all toolbars present in the UI, used typically before showing the toolbars relevant 
            to the current view.
        show_toolbars(view_name: str):
            Adjusts the visibility of toolbars based on the provided view name. For example, if 
            view_name is "DataView", the export toolbar is made visible.
    """
    
    def __init__(self, parent=None, flags=Qt.WindowFlags()):  
        super().__init__(parent, flags)
        self.ui = MainWindowUi()
        self.stack = StackWidget() 
        self.main_menu = MainMenu(self.stack) 
        self.data_view = DataView(self.stack)
        self.market_view = Market(self.stack)     
        


    def setup_ui(self):
        """
        Set up the user interface for the main window.
        This method initializes and configures the primary UI components:
        - It sets up the main menu, data view, and market view.
        - Each view is added to a QStackedWidget, which is then set as the central widget.
        - It hides all toolbars and connects the necessary signals for interactivity.
        Returns:
            None
        """
        
        self.ui.setupUi(self)   
        self.main_menu.setup_ui()
        self.data_view.setup_ui()
        self.market_view.setup_ui()
                
        self.stack.addWidget(self.main_menu)
        self.stack.addWidget(self.data_view)
        self.stack.addWidget(self.market_view)
        
        # Das QStackedWidget als zentrales Widget setzen
        self.setCentralWidget(self.stack)

        self.hide_all_toolbars()
        self.setup_signals()

    def setup_signals(self):
        """
        Sets up all the necessary signal connections for the main window UI.
        This method connects:
        - the 'on_exit_button_clicked' signal from the main menu to the window's close method,
        - the 'on_export_button_clicked' signal from the main menu to a lambda function that opens the "DataView",
        - the 'action_open_export' triggered signal from the UI actions to the 'open_market_view' method.
        """
        self.main_menu.on_exit_button_clicked.connect(self.close)
        self.main_menu.on_export_button_clicked.connect(self.open_data_view)
        #self.ui.action_open_export.triggered.connect(self.open_market_view)
        #self.ui.action_open_file.triggered.connect(self.open_file_dialog)

    def open_view(self, view_name:str):
        """
        Switches the current view in the stack to the specified view name.

        Args:
            view_name (str): The name of the view to switch to.

        This method iterates through the children of the stack and sets the current
        index to the view that matches the given view name. It also hides all toolbars
        and shows the toolbars associated with the specified view.
        """
        for idx, child in enumerate(self.stack.children()):
            if child.objectName() == view_name:
                self.stack.setCurrentIndex(idx)
                self.hide_all_toolbars()
                self.show_toolbars(view_name)
                break
    
    def open_data_view(self):
        """
        Switches the currently displayed view in the stack to the data view.
        """
        base_data = self.open_file_dialog()
        self.data_view.set_data(base_data)
        self.open_view("DataView")
       
        
    def open_market_view(self):
        """
        Switches the currently displayed view in the stack to the market view.
        """
        self.open_view("MarketView")


    def hide_all_toolbars(self):
        self.ui.tool_export.setVisible(False)

    def show_toolbars(self, view_name: str):
        """
        Adjusts the visibility of toolbars according to the provided view name.
        Args:
            view_name (str): A string representing the name of the current view. Recognized values include:
                - "MainMenuView": The main menu interface.
                - "DataView": The data viewing interface; enables the export toolbar.
                - "MarketView": The market view interface.
                - Any other string: No toolbar visibility changes are applied.
        Returns:
            None
        """
        match view_name:
            case "MainMenuView":
                pass
            case "DataView":
                self.ui.tool_export.setVisible(True)

            case "MarketView":
                pass 
            case _:
                pass

    def open_file_dialog(self):
        """
        Opens a file dialog to select a JSON file and loads its content.
        """
        file_name, _ = QFileDialog.getOpenFileName(self, "Open JSON File", "", "JSON Files (*.json)")
        if file_name:
            try:
                
                base_data = DataManager(file_name)
                base_data.verify_data()
                return base_data
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to load JSON file: {e}")
                return None
