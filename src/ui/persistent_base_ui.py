"""Base class providing JSON persistence functionality for UI widgets."""

from dataclasses import asdict, is_dataclass
import json
from typing import Any

from PySide6.QtCore import Signal, Slot
from PySide6.QtWidgets import QFileDialog, QMessageBox

from data.json_handler import JsonHandler

from .base_ui import BaseUi


class PersistentBaseUi(BaseUi):
    """Base UI class with JSON persistence helpers."""

    storage_path_changed = Signal(str)
    status_info = Signal(str, str)
    data_changed = Signal(bool)

    _config: JsonHandler

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _update_config_from_state(self, state: Any) -> None:
        """Update :attr:`_config` with *state* which may be dataclass, dict or
        :class:`~data.json_handler.JsonHandler`."""
        if isinstance(state, JsonHandler):
            self._config.update_json_data(state)
        elif is_dataclass(state):
            self._config.json_data = asdict(state)
        else:
            self._config.json_data = state

    # ------------------------------------------------------------------
    # Expected to be provided by subclasses
    # ------------------------------------------------------------------
    def export_state(self) -> Any:
        raise NotImplementedError

    def import_state(self, state: Any) -> None:
        raise NotImplementedError

    def _config_changed(self) -> bool:
        raise NotImplementedError

    # ------------------------------------------------------------------
    # Persistence slots
    # ------------------------------------------------------------------
    @Slot()
    def save_as_state(self) -> None:
        file_name, _ = QFileDialog.getSaveFileName(self, "Konfiguration speichern", "", "JSON (*.json)")
        if file_name:
            try:
                self._update_config_from_state(self.export_state())
                self._config.save(file_name)
                self.storage_path_changed.emit(file_name)
                self.status_info.emit("INFO", f"Konfiguration gespeichert: {file_name}")
                self._config_changed()
            except (IOError, json.JSONDecodeError) as e:
                QMessageBox.critical(self, "Fehler", f"Fehler beim Speichern der Datei:\n{e}")

    @Slot()
    def save_state(self) -> None:
        path = self._config.get_storage_full_path()
        if path:
            try:
                self._update_config_from_state(self.export_state())
                self._config.save(path)
                if not self._config_changed():
                    self.status_info.emit("INFO", "Konfiguration gespeichert")
            except IOError as e:
                QMessageBox.critical(self, "Fehler", f"Fehler beim Speichern der Datei:\n{e}")
        else:
            self.save_as_state()

    @Slot()
    def restore_state(self) -> None:
        self.import_state(self._config)
        self._config_changed()

    @Slot()
    def load_state(self) -> None:
        file_name, _ = QFileDialog.getOpenFileName(self, "Konfiguration laden", "", "JSON (*.json)")
        if file_name:
            try:
                new_config = self._config.__class__(file_name)
                self.import_state(new_config)
                self._config = new_config
                self.storage_path_changed.emit(file_name)
                self.status_info.emit("INFO", f"Konfiguration geladen: {file_name}")
                self._config_changed()
            except (IOError, json.JSONDecodeError) as e:
                QMessageBox.critical(self, "Fehler", f"Fehler beim Laden der Datei:\n{e}")
