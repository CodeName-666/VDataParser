#PySide6 imports
from PySide6.QtCore import Qt, Slot
from PySide6.QtWidgets import QMainWindow,  QMessageBox, QFileDialog, QDialog, QLabel, QLineEdit
from PySide6.QtCore import QTimer


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
from data import MarketFacade
from .status_bar import StatusBar




class MainWindow(QMainWindow):
    
    def __init__(self, parent=None, flags=Qt.WindowFlags()):
        """Create a new application window.

        Parameters
        ----------
        parent:
            Optional Qt parent widget.
        flags:
            Window flags used during initialisation.
        """
        super().__init__(parent, flags)
        self.ui = MainWindowUi()
        self.stack = StackWidget()
        self.main_menu = MainMenu(self.stack)
        self.market_view = Market(self.stack)
        #self.pdf_display = PdfDisplay(self.stack)
        self.output_window = OutputWindow()
        self.market_facade = MarketFacade()
        self.status_bar = StatusBar(self)

        
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
        self.setStatusBar(self.status_bar)
        self.stack.addWidget(self.main_menu)
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
        self.main_menu.on_open_export_button_clicked.connect(self.open_local_market_export)
        self.main_menu.on_open_market_button_clicked.connect(self.open_market_view)
        
        self.ui.action_create_pdf.triggered.connect(self.start_pdf_generation)
        self.ui.action_generate_data.triggered.connect(self.start_data_generation)
        self.ui.action_generate_add.triggered.connect(self.start_all_generation)
        self.ui.action_save_project.triggered.connect(self.save_project)
        self.ui.action_save_project_as.triggered.connect(self.save_project_as)
        
        self.market_facade.status_info.connect(self.status_bar.handle_status)
        self.market_view.status_info.connect(self.status_bar.handle_status)
        
        #self.ui.action_tool.triggered.connect(self.open_about_ui)

        #self.ui.actionCreate_PDF.triggered.connect(self.open_pdf_display)
        #self.ui.action_Export_Data.triggered.connect(self.open_local_market_export)
        #self.ui.action_open_export.triggered.connect(self.open_market_view)
        #self.ui.action_open_file.triggered.connect(self.open_file_dialog)

    def open_view(self, view_name: str):
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


    @Slot()
    def open_local_market_export(self):
        """
        Switches the currently displayed view in the stack to the data view.
        """
        local_json = self.open_file_dialog()
        self.market_facade.load_local_market_export(self.market_view, local_json)
        self.open_view("Market")

            
    @Slot()  
    def open_market_view(self):
        """
        Switches the currently displayed view in the stack to the market view.
        """
        ret = False
        dialog = MarketLoaderDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            market_loader_info = dialog.get_result()
            if market_loader_info["mode"] == "json":
                ret = self.market_facade.load_local_market_porject(self.market_view,market_loader_info["path"])
            elif market_loader_info["mode"] == "mysql":
                ret = self.market_facade.load_online_market(self.market_view, market_loader_info)
            else:
                #QMessageBox.critical(self, "Error", "Invalid market loader mode selected.")
                return
            #self.market_view.set_data(market_data)
            if ret:
                self.open_view("Market")
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
        self.ui.tool_project.setVisible(False)
        self.ui.toolBar.setVisible(False)

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
                self.ui.tool_project.setVisible(True)
                self.ui.toolBar.setVisible(True)

            case _:
                pass

    def open_file_dialog(self):
        """
        Opens a file dialog to select a JSON file.

        Returns
        -------
        str | None
            The chosen file path or ``None`` if the dialog was cancelled.
        """
        file_name, _ = QFileDialog.getOpenFileName(self, "Open JSON File", "", "JSON Files (*.json)")
        if file_name:
            return file_name
        else:            
            QMessageBox.critical(self, "Error", f"Failed to load JSON file: {e}")
            return None

    @Slot()
    def save_project(self):
        """Save current project."""
        if self.market_facade.is_project(self.market_view):
            project_dir = self.market_facade.get_project_dir(self.market_view)
            if project_dir:
                self.market_facade.save_project(self.market_view, project_dir)
                return
        chosen_dir = QFileDialog.getExistingDirectory(self, "Projekt speichern")
        if chosen_dir:
            self.market_facade.save_project(self.market_view, chosen_dir)

    @Slot()
    def save_project_as(self):
        """Save current project to a user chosen directory."""
        chosen_dir = QFileDialog.getExistingDirectory(self, "Projekt speichern unter")
        if chosen_dir:
            self.market_facade.save_project(self.market_view, chosen_dir)

    def open_about_ui(self):
        """
        Opens and displays the AboutUi dialog.
        """
        self.about_dialog =  QDialog()
        self.adout = AboutUi()
        self.adout.setupUi(self.about_dialog )
        self.about_dialog.exec()
   
    @Slot()
    def start_data_generation(self):
        """
        Starts the data generation process.
        This method is a placeholder for future implementation.
        """
        QMessageBox.information(self, "Info", "Data generation started. This feature is not yet implemented.")

    @Slot()
    def start_pdf_generation(self):
        """
        Starts the PDF generation process.
        This method is a placeholder for future implementation.
        """
        self.market_facade.create_pdf_data(self.market_view)
        QMessageBox.information(self, "Info", "PDF generation started. This feature is not yet implemented.")

    @Slot()
    def start_all_generation(self):
        """
        Starts the generation of all data and PDF files.
        This method is a placeholder for future implementation.
        """
        self.market_facade.create_all_data(self.market_view)
        QMessageBox.information(self, "Info", "All generation started. This feature is not yet implemented.")

    @Slot()
    def create_local_market_export(self):
        """
        Creates a local market export.
        This method is a placeholder for future implementation.
        """
        if not self.market_facade.is_project(self.market_view):
              # Datei-Dialog öffnen
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "Speicherort für PDF wählen",  # Titel
                "",                            # Standard-Pfad
                "PDF Dateien (*.pdf)"          # Filter
            )

            if not file_path:
                # Benutzer hat abgebrochen
                return                                
        self.market_facade.create_market_data(self.market_view)
        QMessageBox.information(self, "Info", "Local market export created. This feature is not yet implemented.")