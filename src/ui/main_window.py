#PySide6 imports
from PySide6.QtCore import Qt, Slot
from PySide6.QtWidgets import QMainWindow,  QMessageBox, QFileDialog, QDialog

#Local imports
from data import DataManager
from .stack_widget import StackWidget
from .generated import MainWindowUi
from .generated import AboutUi
from .generated import MarketLoaderUi

from .main_menu import MainMenu
from .market import Market
from .pdf_display import PdfDisplay
from .market_loader_dialog import MarketLoaderDialog
from .output_window import OutputWindow





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
        self.market_view = Market(self.stack)
        self.pdf_display = PdfDisplay(self.stack)
        self.output_window = OutputWindow()

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
        self.stack.addWidget(self.main_menu)
        self.stack.addWidget(self.market_view)
        self.stack.addWidget(self.pdf_display)
        
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
        self.main_menu.on_open_export_button_clicked.connect(self.open_local_export)
        self.main_menu.on_open_market_button_clicked.connect(self.open_market_view)

        self.pdf_display.exit_requested.connect(self.switch_to_last_view)
        
        self.ui.action_tool.triggered.connect(self.open_about_ui)

        self.ui.actionCreate_PDF.triggered.connect(self.open_pdf_display)
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
        for child in self.stack.children():
            if child.objectName() == view_name:
                idx = self.stack.indexOf(child)
                self.stack.backup_last_index()
                self.stack.setCurrentIndex(idx)
                self.show_toolbars(view_name)
                break
    
    def open_pdf_display(self):
        """
        Switches the currently displayed view in the stack to the PDF display view.
        """
        self.open_view("PdfDisplayView")

    def open_local_export(self):
        """
        Switches the currently displayed view in the stack to the data view.
        """
        base_data = self.open_file_dialog()
        self.market_view.set_data(base_data)
        self.open_view("Market")
       
        
    def open_market_view(self):
        """
        Switches the currently displayed view in the stack to the market view.
        """
        dialog = MarketLoaderDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            market_data = dialog.get_result()
            #self.market_view.set_data(market_data)
            #self.open_view("Market")
        else:
            QMessageBox.warning(self, "Warning", "No market data loaded. Please try again.")

    @Slot()
    def switch_to_last_view(self):
        """
        Switches the currently displayed view in the stack to the last view.
        It retrieves the last view's object name, reactivates the corresponding toolbars,
        and then restores the last view index.
        """
        last_index = self.stack.get_last_index()
        last_view = self.stack.widget(last_index)
        view_name = last_view.objectName()
        self.stack.restore_last_index()
        self.show_toolbars(view_name)

        
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
        self.hide_all_toolbars()
        match view_name:
            case "MainMenuView":
                pass

            case "Market":
                self.ui.tool_export.setVisible(True)
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
                #base_data.verify_data()
                return base_data
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to load JSON file: {e}")
                return None

    def open_about_ui(self):
        """
        Opens and displays the AboutUi dialog.
        """
        self.about_dialog =  QDialog()
        self.adout = AboutUi()
        self.adout.setupUi(self.about_dialog )
        self.about_dialog.exec()

