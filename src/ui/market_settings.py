import json
from dataclasses import asdict
from PySide6.QtCore import QDate, QDateTime, Signal, Slot
from PySide6.QtWidgets import QFileDialog, QMessageBox
from data.json_handler import JsonHandler
from objects import SettingsContentDataClass

from .base_ui import BaseUi
from .generated import MarketSettingUi


class MarketSetting(BaseUi):
    """Widget providing access to market configuration values."""

    storage_path_changed = Signal(str)
    status_info = Signal(str, str)

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
        self.default_settings = {}
        self._config = JsonHandler()
        self.ui.setupUi(self)
        self.connect_signals()

    def connect_signals(self) -> None:
        """Hook up UI signal handlers."""
        self.ui.buttonSave.clicked.connect(self.save)
        self.ui.buttonCancel.clicked.connect(self.restore)

    def set_default_settings(self, settings: SettingsContentDataClass | dict) -> None:
        """Store default configuration values.

        Parameters
        ----------
        settings:
            ``SettingsContentDataClass`` instance or a plain dictionary
            containing the default settings.
        """
        if isinstance(settings, dict):
            self.default_settings = SettingsContentDataClass(**settings)
        else:
            self.default_settings = settings

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

        if settings.is_all_empty():
            settings_obj = self.default_settings
        else:
            settings_obj = settings.data[0]

        self._apply_state_dataclass(settings_obj)

    # ------------------------------------------------------------------
    # Persistence helpers similar to PdfDisplay
    # ------------------------------------------------------------------
    def export_state(self) -> SettingsContentDataClass:
        """Return the current UI state as dataclass."""
        return self._state_to_dataclass()

    def import_state(self, state: SettingsContentDataClass) -> None:
        """Apply the given state to the UI."""
        self._apply_state_dataclass(state)

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

    # --- Save/Load ----------------------------------------------------
    @Slot()
    def save_as(self) -> None:
        """Save settings to a new JSON file."""
        file_name, _ = QFileDialog.getSaveFileName(self, "Einstellungen speichern", "", "JSON (*.json)")
        if file_name:
            try:
                data = asdict(self.export_state())
                with open(file_name, "w", encoding="utf-8") as fh:
                    json.dump(data, fh, indent=4, ensure_ascii=False)
                self._config.set_path_or_url(file_name)
                self._config.json_data = data
                self.storage_path_changed.emit(file_name)
                self.status_info.emit("INFO", f"Einstellungen gespeichert: {file_name}")
            except IOError as e:
                self.status_info.emit("ERROR", f"Fehler beim Speichern der Datei:\n{e}")
                QMessageBox.critical(self, "Fehler", f"Fehler beim Speichern der Datei:\n{e}")

    @Slot()
    def save(self) -> None:
        """Save settings using the current storage path."""
        path = self._config.get_storage_full_path()
        if path:
            try:
                self._config.json_data = asdict(self.export_state())
                self._config.save(path)
                self.status_info.emit("INFO", "Einstellungen gespeichert")
            except IOError as e:
                QMessageBox.critical(self, "Fehler", f"Fehler beim Speichern der Datei:\n{e}")
        else:
            self.save_as()

    @Slot()
    def restore(self) -> None:
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
            except (IOError, json.JSONDecodeError) as e:
                QMessageBox.critical(self, "Fehler", f"Fehler beim Laden der Datei:\n{e}")

    def market_widget(self):
        """Return the associated market widget."""
        return self.market
