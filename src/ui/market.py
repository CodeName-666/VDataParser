from PySide6.QtCore import Slot, Signal
from PySide6.QtWidgets import QWidget

from .base_ui import BaseUi
from .generated import MarketUi
from .market_settings import MarketSetting
from .data_view import DataView
from .user_info import UserInfo
from .pdf_display import PdfDisplay
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

    def connect_signals(self) -> None:
        """Forward signals from the PDF display to this widget."""
        if self.pdf_display:
            self.pdf_display.storage_path_changed.connect(self.pdf_display_storage_path_changed)
            self.pdf_display.data_changed.connect(self.pdf_display_data_changed)
            self.pdf_display.status_info.connect(self.status_info)
            self.pdf_display.data_changed.connect(self.pdf_data_changed)

    @Slot(bool)
    def pdf_data_changed(self, status: bool):
        if status == True: 
            txt = f"{self.pdf_tab_txt} *"
        else: 
            txt = self.pdf_tab_txt
        self.ui.tabWidget.setTabText(self.ui.tabWidget.indexOf(self.ui.tab_4),txt)

    @Slot(object)
    def set_default_settings(self, settings: dict) -> None:
        """Apply default settings to the :class:`MarketSetting` widget.

        Parameters
        ----------
        settings:
            Dictionary containing default configuration values.
        """
        if isinstance(self.market_setting, MarketSetting):
            self.market_setting.set_default_settings(settings)

    @Slot(PdfDisplayConfig)
    def set_pdf_config(self, pdf_config: PdfDisplayConfig) -> None:
        """Pass PDF layout configuration to the PdfDisplay widget.

        Parameters
        ----------
        pdf_config:
            Persisted :class:`PdfDisplayConfig` instance.
        """
        self.pdf_display.import_state(pdf_config)

    def setup_ui(self) -> None:
        """Create and attach all sub widgets."""
        self.ui.setupUi(self)
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
