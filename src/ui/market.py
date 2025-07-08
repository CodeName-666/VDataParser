from PySide6.QtCore import Slot, Signal, QCoreApplication
from PySide6.QtWidgets import QWidget

from .base_ui import BaseUi
from .generated import MarketUi
from .market_settings import MarketSetting
from .data_view import DataView
from .user_info import UserInfo
from .pdf_display import PdfDisplay
from .market_statistics import MarketStatistics
from data import DataManager, PdfDisplayConfig


class Market(BaseUi):
    """Main widget bundling all market related sub views."""

    pdf_display_storage_path_changed = Signal(str)
    pdf_display_data_changed = Signal(bool)
    status_info = Signal(str, str)

    def __init__(self, parent=None):
        """Create the UI and sub widgets.

        Parameters
        ----------
        parent:
            Optional parent widget this widget will be attached to.
        """
        super().__init__(parent)
        self.data_manager_ref: DataManager | None = None
        self.pdf_tab_txt: str = ''
        self.safe_indiction_sign = ' *'
        self.prevoius_tab_index = -1
        self.ui = MarketUi()
        self.setup_ui()

    @Slot(DataManager)
    def set_market_data(self, data_manager: DataManager) -> None:
        """Initialise sub views with ``data_manager``.

        Parameters
        ----------
        data_manager:
            Instance providing access to parsed market data.
        """
        self.data_manager_ref = data_manager
        self.market_setting.setup_views(self)
        self.data_view.setup_views(self)
        self.user_info.setup_views(self)
        self.market_stats.setup_views(self)

    def connect_signals(self) -> None:

        self.ui.tabWidget.currentChanged.connect(self.tab_changed)
        """Forward signals from the PDF display to this widget."""
        
        self.pdf_display.storage_path_changed.connect(self.pdf_display_storage_path_changed)
        self.pdf_display.data_changed.connect(self.pdf_display_data_changed)
        self.pdf_display.status_info.connect(self.status_info)
        self.pdf_display.data_changed.connect(self.data_changed)

        self.market_setting.data_changed.connect(self.data_changed)


        

    @Slot(int)
    def tab_changed(self, index: int):
        if self.prevoius_tab_index != -1:
            old_idx = self.prevoius_tab_index
            if self.check_safe_indication(old_idx):
                ui_widget = self.ui.tabWidget.widget(old_idx).children()[1]
                self.ask_to_save(ui_widget)

            print(f"Old IDX: {old_idx}")
            self.prevoius_tab_index = index
        else:
            self.prevoius_tab_index = index
        
    def ask_to_save(self, widget):
        """Fragt den Nutzer, ob Änderungen gespeichert werden sollen und ruft Save oder restore auf."""
        from PySide6.QtWidgets import QMessageBox

        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Question)
        msg_box.setWindowTitle("Änderungen speichern?")
        msg_box.setText("Möchten Sie die Änderungen speichern?")
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg_box.setDefaultButton(QMessageBox.Yes)
        result = msg_box.exec()

        if result == QMessageBox.Yes:
            if hasattr(widget, "save_state"):
                widget.save_state()
        elif result == QMessageBox.No:
            if hasattr(widget, "restore_state"):
                widget.restore_state()
        
        # Bei Cancel oder Schließen passiert nichts_to_save(self, widget):


    def check_safe_indication(self, tab_idx: int):
        tab_widget_txt = self.ui.tabWidget.tabText(tab_idx)
        if tab_widget_txt.find(self.safe_indiction_sign) != -1:
            return True
        return False

    @Slot(bool)
    def data_changed(self, status: bool):
        sender_tab = self.sender().parent()
        txt = self.ui.tabWidget.tabText(self.ui.tabWidget.indexOf(sender_tab))

        if status == True: 
            if txt.find(self.safe_indiction_sign) == -1:
                txt = f"{txt}{self.safe_indiction_sign}"
        else: 
            if txt.find(self.safe_indiction_sign):
                txt = txt.replace(self.safe_indiction_sign,'')

        self.ui.tabWidget.setTabText(self.ui.tabWidget.indexOf(sender_tab),txt)

    @Slot(PdfDisplayConfig)
    def set_pdf_config(self, pdf_config: PdfDisplayConfig) -> None:
        """Pass PDF layout configuration to the PdfDisplay widget.

        Parameters
        ----------
        pdf_config:
            Persisted :class:`PdfDisplayConfig` instance.
        """
        self.pdf_display.import_state(pdf_config)


    def set_tab_names(self):
        self.ui.tabWidget.setTabText(self.ui.tabWidget.indexOf(self.ui.tab), QCoreApplication.translate("Market", u"Markt Einstellungen", None))
        self.ui.tabWidget.setTabText(self.ui.tabWidget.indexOf(self.ui.tab_3), QCoreApplication.translate("Market", u"Benutzerinformationen", None))
        self.ui.tabWidget.setTabText(self.ui.tabWidget.indexOf(self.ui.tab_2), QCoreApplication.translate("Market", u"Verkaufslisten", None))
        self.ui.tabWidget.setTabText(self.ui.tabWidget.indexOf(self.ui.tab_4), QCoreApplication.translate("Market", u"Abholbest\u00e4tigung", None))
        self.ui.tabWidget.setTabText(self.ui.tabWidget.indexOf(self.ui.tab_statistics), QCoreApplication.translate("Market", u"Statistik", None))

    def setup_ui(self) -> None:
        """Create and attach all sub widgets."""
        self.ui.setupUi(self)
        self.set_tab_names()
        self.market_stats = self.add_widget(self.ui.tab_statistics, MarketStatistics)
        self.market_setting = self.add_widget(self.ui.tab, MarketSetting)
        self.data_view = self.add_widget(self.ui.tab_2, DataView)
        self.user_info = self.add_widget(self.ui.tab_3, UserInfo)
        self.pdf_display = self.add_widget(self.ui.tab_4, PdfDisplay)
        
        
        self.pdf_tab_txt = self.ui.tabWidget.tabText(self.ui.tabWidget.indexOf(self.ui.tab_4))
        self.connect_signals()
        self.ui.tabWidget.setCurrentIndex(0)        

    def get_user_data(self):
        """Return seller data as simple dictionaries."""
        if not self.data_manager_ref:
            return {}
        return self.data_manager_ref.get_users_data()

    def get_aggregated_user_data(self):
        """Return aggregated seller data."""
        if not self.data_manager_ref:
            return {}
        return self.data_manager_ref.get_aggregated_users_data()

    def get_aggregated_user(self):
        """Return aggregated seller structures."""
        if not self.data_manager_ref:
            return {}
        return self.data_manager_ref.get_aggregated_users()

    def get_seller(self):
        """Return a list of seller objects."""
        if not self.data_manager_ref:
            return []
        return self.data_manager_ref.get_seller_as_list()

    def get_main_numbers(self):
        """Return the stnr tables from the data manager."""
        if not self.data_manager_ref:
            return {}
        return self.data_manager_ref.get_main_number_tables()

    def get_settings(self):
        """Return settings from the data manager."""
        if not self.data_manager_ref:
            return {}
        return self.data_manager_ref.get_settings()

    def get_data_manager(self):
        if not self.data_manager_ref:
            return {}
        return self.data_manager_ref