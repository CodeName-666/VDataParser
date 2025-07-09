import json
import copy
from dataclasses import asdict
from PySide6.QtCore import QDate, QDateTime, Slot
from PySide6.QtWidgets import QFileDialog, QMessageBox
from objects import SettingsContentDataClass
from data import DataManager
from .persistent_base_ui import PersistentBaseUi
from .generated import MarketSettingUi




class MarketSetting(PersistentBaseUi):
    """Widget providing access to market configuration values."""


    def __init__(self, parent=None):
        """Create widgets and connect signals.

        Parameters
        ----------
        parent:
            Optional parent widget.
        """
        super().__init__(parent)
        self.ui = MarketSettingUi()
        self.market = None
        self.ui.setupUi(self)
        self.connect_signals()

    def connect_signals(self) -> None:
        """Hook up UI signal handlers."""
        self.ui.buttonSave.clicked.connect(self.save_state)
        self.ui.buttonRestore.clicked.connect(self.restore_state)
        self.ui.spinMaxStammnummer.valueChanged.connect(self._config_changed)
        self.ui.spinMaxArtikel.valueChanged.connect(self._config_changed)
        self.ui.dateTimeEditFlohmarktCountDown.dateTimeChanged.connect(self._config_changed)
        self.ui.spinFlohmarktNummer.valueChanged.connect(self._config_changed)
        self.ui.spinPwLength.valueChanged.connect(self._config_changed)
        self.ui.lineEditTabellePrefix.textChanged.connect(self._config_changed)
        self.ui.lineEditTabelleVerkaeufer.textChanged.connect(self._config_changed)
        self.ui.spinMaxIdPerUser.valueChanged.connect(self._config_changed)
        self.ui.dateTimeEditFlohmarkt.dateChanged.connect(self._config_changed)
        self.ui.radioDisbaledFlohmarkt.clicked.connect(self._config_changed)
        self.ui.radioActiveFlohmarkt.clicked.connect(self._config_changed)

    def setup_views(self, market_widget):
        """Initialise the view for the given ``market_widget``.

        Parameters
        ----------
        market_widget:
            The parent :class:`Market` instance.
        """
        self.market = market_widget
        self.load_settings()

    def load_settings(self) -> None:
        """Load settings from the market widget and update the UI."""
        data_manager = self.market_widget().get_data_manager()
      
        self._apply_state_dataclass(data_manager.settings.data[0])
        self.set_config(data_manager)
        self._config_changed()

    # ------------------------------------------------------------------
    # Persistence helpers similar to PdfDisplay
    # ------------------------------------------------------------------
    def export_state(self):
        """Return the current UI state as dataclass."""
        data = copy.deepcopy(self.get_config())
        data.settings.data[0] = self._state_to_dataclass()
        return data

    def import_state(self, state: SettingsContentDataClass) -> None:
        """Apply the given state to the UI."""
        self._apply_state_dataclass(state)
        config = self.get_config()
        if config:
            config.settings.data[0] = state
            self._config_changed()

    def get_radio_button_status(self) -> str:
        if self.ui.radioActiveFlohmarkt.isChecked():
            return "ja"
        elif self.ui.radioDisbaledFlohmarkt.isChecked():
            return "nein"
        else:
            return "nein"

    def set_radio_button_status(self, status: str):
        if status == "ja":
            self.ui.radioActiveFlohmarkt.setChecked(True)
        else: 
            self.ui.radioDisbaledFlohmarkt.setChecked(True)

    def set_login_aktiv_status(self, status: str):
        if status == "ja":
            self.ui.checkBoxLoginDisable.setChecked(True)
        else:
            self.ui.checkBoxLoginDisable.setChecked(False)

    def get_login_aktiv_status(self):
        if self.ui.checkBoxLoginDisable.isChecked():
            return "ja"
        else:
            return "nein"

    def _state_to_dataclass(self) -> SettingsContentDataClass:
        return SettingsContentDataClass(
            max_stammnummern=str(self.ui.spinMaxStammnummer.value()),
            max_artikel=str(self.ui.spinMaxArtikel.value()),
            datum_counter=self.ui.dateTimeEditFlohmarktCountDown.dateTime().toString("yyyy-MM-dd HH:mm:ss"),
            flohmarkt_nr=str(self.ui.spinFlohmarktNummer.value()),
            psw_laenge=str(self.ui.spinPwLength.value()),
            tabellen_prefix=self.ui.lineEditTabellePrefix.text(),
            verkaufer_liste=self.ui.lineEditTabelleVerkaeufer.text(),
            max_user_ids=str(self.ui.spinMaxIdPerUser.value()),
            datum_flohmarkt=self.ui.dateTimeEditFlohmarkt.date().toString("yyyy-MM-dd"),
            flohmarkt_aktiv= str(self.get_radio_button_status()),
            login_aktiv= str(self.get_login_aktiv_status())
        )

    def _apply_state_dataclass(self, state: SettingsContentDataClass) -> None:
        self.ui.spinMaxStammnummer.setValue(int(str(state.max_stammnummern)) if str(state.max_stammnummern).isdigit() else 0)
        self.ui.spinMaxArtikel.setValue(int(str(state.max_artikel)) if str(state.max_artikel).isdigit() else 0)
        self.ui.dateTimeEditFlohmarktCountDown.setDateTime(QDateTime.fromString(state.datum_counter, "yyyy-MM-dd HH:mm:ss")        )
        self.ui.spinFlohmarktNummer.setValue(int(str(state.flohmarkt_nr)) if str(state.flohmarkt_nr).isdigit() else 0)
        self.ui.spinMaxIdPerUser.setValue(int(str(state.max_user_ids)) if str(state.max_user_ids).isdigit() else 0)
        self.ui.spinPwLength.setValue(int(str(state.psw_laenge)) if str(state.psw_laenge).isdigit() else 0)
        self.ui.lineEditTabellePrefix.setText(state.tabellen_prefix)
        self.ui.lineEditTabelleVerkaeufer.setText(state.verkaufer_liste)
        self.ui.dateTimeEditFlohmarkt.setDate(QDate.fromString(state.datum_flohmarkt, "yyyy-MM-dd"))
        self.set_login_aktiv_status(str(state.login_aktiv))
        self.set_radio_button_status(str(state.flohmarkt_aktiv))
    
    @Slot()
    def _config_changed(self) -> bool:
        
        if self._config is not None and self._config.get_data() is not None:
            ret = (self._state_to_dataclass() != self._config.settings.data[0])
            self.data_changed.emit(ret)
            return ret
        return False

    # --- Save/Load ----------------------------------------------------
    @Slot()
    def save_as_state(self) -> None:
        """Save settings to a new JSON file."""
        super().save_as_state()

    @Slot()
    def save_state(self) -> None:
        """Save settings using the current storage path."""
        super().save_state()

    @Slot()
    def restore_state(self) -> None:
        config = self.get_config()
        if config is not None:
            settings = config.settings.data[0]
            self.import_state(settings)
            self._config_changed()

    def market_widget(self):
        """Return the associated market widget."""
        return self.market
