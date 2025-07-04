import json
from dataclasses import asdict
from PySide6.QtCore import QDate, QDateTime, Slot
from PySide6.QtWidgets import QFileDialog, QMessageBox
from data.json_handler import JsonHandler
from objects import SettingsContentDataClass

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
        self._config = JsonHandler()
        self.ui.setupUi(self)
        self.connect_signals()

    def connect_signals(self) -> None:
        """Hook up UI signal handlers."""
        self.ui.buttonSave.clicked.connect(self.save_state)
        self.ui.buttonCancel.clicked.connect(self.restore_state)
        self.ui.spinMaxStammnummer.valueChanged.connect(self._config_changed)
        self.ui.spinMaxArtikel.valueChanged.connect(self._config_changed)
        self.ui.dateTimeEditFlohmarktCountDown.dateTimeChanged.connect(self._config_changed)
        self.ui.spinFlohmarktNummer.valueChanged.connect(self._config_changed)
        self.ui.spinPwLength.valueChanged.connect(self._config_changed)
        self.ui.lineEditTabellePrefix.textChanged.connect(self._config_changed)
        self.ui.lineEditTabelleVerkaeufer.textChanged.connect(self._config_changed)
        self.ui.spinMaxIdPerUser.valueChanged.connect(self._config_changed)
        self.ui.dateTimeEditFlohmarkt.dateChanged.connect(self._config_changed)

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
        settings = self.market_widget().get_settings()
      
        self._apply_state_dataclass(settings.data[0])
        self._config.json_data = asdict(settings.data[0])
        self._config_changed()

    # ------------------------------------------------------------------
    # Persistence helpers similar to PdfDisplay
    # ------------------------------------------------------------------
    def export_state(self) -> SettingsContentDataClass:
        """Return the current UI state as dataclass."""
        return self._state_to_dataclass()

    def import_state(self, state: SettingsContentDataClass) -> None:
        """Apply the given state to the UI."""
        self._apply_state_dataclass(state)
        self._config.json_data = asdict(state)
        self._config_changed()

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
        )

    def _apply_state_dataclass(self, state: SettingsContentDataClass) -> None:
        self.ui.spinMaxStammnummer.setValue(int(str(state.max_stammnummern)) if str(state.max_stammnummern).isdigit() else 0)
        self.ui.spinMaxArtikel.setValue(int(str(state.max_artikel)) if str(state.max_artikel).isdigit() else 0)
        self.ui.dateTimeEditFlohmarktCountDown.setDateTime(
            QDateTime.fromString(state.datum_counter, "yyyy-MM-dd HH:mm:ss")
        )
        self.ui.spinFlohmarktNummer.setValue(int(str(state.flohmarkt_nr)) if str(state.flohmarkt_nr).isdigit() else 0)
        self.ui.spinMaxIdPerUser.setValue(int(str(state.max_user_ids)) if str(state.max_user_ids).isdigit() else 0)
        self.ui.spinPwLength.setValue(int(str(state.psw_laenge)) if str(state.psw_laenge).isdigit() else 0)
        self.ui.lineEditTabellePrefix.setText(state.tabellen_prefix)
        self.ui.lineEditTabelleVerkaeufer.setText(state.verkaufer_liste)
        self.ui.dateTimeEditFlohmarkt.setDate(
            QDate.fromString(state.datum_flohmarkt, "yyyy-MM-dd")
        )

    def _config_changed(self) -> bool:
        if self._config.get_data() is not None:
            ret = asdict(self.export_state()) != self._config.get_data()
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
    def load_state(self) -> None:
        """Load settings from a JSON file."""
        file_name, _ = QFileDialog.getOpenFileName(self, "Einstellungen laden", "", "JSON (*.json)")
        if file_name:
            try:
                with open(file_name, "r", encoding="utf-8") as fh:
                    data = json.load(fh)
                state = SettingsContentDataClass(**data)
                self.import_state(state)
                self._config.json_data = data
                self._config.set_path_or_url(file_name)
                self.storage_path_changed.emit(file_name)
                self.status_info.emit("INFO", f"Einstellungen geladen: {file_name}")
                self._config_changed()
            except (IOError, json.JSONDecodeError) as e:
                QMessageBox.critical(self, "Fehler", f"Fehler beim Laden der Datei:\n{e}")

    @Slot()
    def restore_state(self) -> None:
        data = self._config.get_data()
        if data is not None:
            state = SettingsContentDataClass(**data)
            self.import_state(state)
            self._config_changed()

    def market_widget(self):
        """Return the associated market widget."""
        return self.market
