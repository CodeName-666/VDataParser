"""Dialog to create a new market with name and initial settings.

This dialog lets the user enter a market name and adjust the same
settings exposed in the MarketSetting view. It returns a
`SettingsContentDataClass` and the chosen market name.
"""

from __future__ import annotations

from typing import Optional

from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QFormLayout,
    QLabel,
    QLineEdit,
    QDialogButtonBox,
    QWidget,
    QTabWidget,
)
from PySide6.QtWidgets import QMessageBox
from PySide6.QtGui import QIntValidator

from data import MarketConfigHandler
from objects import SettingsContentDataClass
from .market_settings import MarketSetting
from .generated.login_ui import Ui_LoginDialog


class NewMarketDialog(QDialog):
    """Collect a market name and settings for a new project."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Neuen Markt anlegen")

        self._name_edit = QLineEdit(self)
        self._name_edit.setPlaceholderText("z. B. Fruehjahrsflohmarkt_2026")

        # Reuse the MarketSetting widget to gather settings values.
        # We do NOT bind it to a Market widget; we just use its export/import
        # helpers to build a SettingsContentDataClass.
        self._settings_widget = MarketSetting(self)

        # Prepopulate with defaults from MarketConfigHandler
        try:
            defaults = MarketConfigHandler().get_market_settings()
        except Exception:
            defaults = SettingsContentDataClass()
        self._settings_widget.import_state(defaults)
        
        # Layout root
        body_layout = QVBoxLayout()

        # Title above the tabs
        title = QLabel("<h2>Markt-Konfiguration</h2>", self)
        body_layout.addWidget(title)

        # Market name directly under the title (outside the TabWidget)
        name_form = QFormLayout()
        name_form.addRow(QLabel("Marktname:"), self._name_edit)
        body_layout.addLayout(name_form)

        # Build tabs: Einstellungen (settings) and Server-Login
        self._tabs = QTabWidget(self)

        # Einstellungen tab content
        self._settings_tab = QWidget(self)
        settings_tab_layout = QVBoxLayout(self._settings_tab)
        settings_tab_layout.setContentsMargins(0, 0, 0, 0)
        # Hide the inner title label of the MarketSetting to avoid duplicate headings inside the tab
        try:
            if hasattr(self._settings_widget, 'ui') and hasattr(self._settings_widget.ui, 'titleLabel'):
                self._settings_widget.ui.titleLabel.setVisible(False)
        except Exception:
            pass
        settings_tab_layout.addWidget(self._settings_widget)
        self._tabs.addTab(self._settings_tab, "Einstellungen")

        # Server-Login tab content (wrap generated login UI)
        self._server_tab = QWidget(self)
        self._server_ui = Ui_LoginDialog()
        self._server_ui.setupUi(self._server_tab)
        # Optional: tweak button visibility from embedded login UI
        try:
            # Hide standalone login actions (we use dialog OK)
            if hasattr(self._server_ui, "pushButtonLogin"):
                self._server_ui.pushButtonLogin.setVisible(False)
            if hasattr(self._server_ui, "pushButton"):
                self._server_ui.pushButton.setVisible(False)
            # Defaults: host localhost, default MySQL port
            if hasattr(self._server_ui, "lineEditHost"):
                self._server_ui.lineEditHost.setText("localhost")
            if hasattr(self._server_ui, "lineEditPort"):
                self._server_ui.lineEditPort.setText("3306")
                try:
                    self._server_ui.lineEditPort.setValidator(QIntValidator(1, 65535, self))
                except Exception:
                    pass
            # Hide database label and input
            if hasattr(self._server_ui, "labelDatabase"):
                self._server_ui.labelDatabase.setVisible(False)
            if hasattr(self._server_ui, "lineEditDatabase"):
                self._server_ui.lineEditDatabase.setVisible(False)
        except Exception:
            pass
        self._server_tab_index = self._tabs.addTab(self._server_tab, "Server-Login")

        body_layout.addWidget(self._tabs)

        # Adjust embedded MarketSetting buttons: hide Save, keep Restore
        try:
            if hasattr(self._settings_widget.ui, "buttonSave"):
                self._settings_widget.ui.buttonSave.setVisible(False)
            if hasattr(self._settings_widget.ui, "buttonRestore"):
                self._settings_widget.ui.buttonRestore.setText("Zurücksetzen")
        except Exception:
            pass

        btns = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, parent=self)
        btns.accepted.connect(self._on_accept)
        btns.rejected.connect(self.reject)
        body_layout.addWidget(btns)
        # Rename OK to "Erstellen" and keep Cancel as-is
        try:
            ok_btn = btns.button(QDialogButtonBox.Ok)
            if ok_btn:
                ok_btn.setText("Erstellen")
        except Exception:
            pass

        self.setLayout(body_layout)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def market_name(self) -> str:
        """Return the entered market name (may be empty)."""
        return self._name_edit.text().strip()

    def settings(self) -> SettingsContentDataClass:
        """Return settings taken from the embedded settings widget."""
        state = self._settings_widget.export_state()
        if isinstance(state, SettingsContentDataClass):
            return state
        # Fallback – build a clean dataclass
        return SettingsContentDataClass()

    def server_info(self) -> dict:
        """Return server connection info from the Server-Login tab."""
        ui = self._server_ui
        def _text(widget_name: str) -> str:
            w = getattr(ui, widget_name, None)
            return w.text().strip() if w is not None else ""
        host = _text("lineEditHost")
        port = _text("lineEditPort")
        user = _text("lineEditUser")
        password = _text("lineEditPassword")
        database = _text("lineEditDatabase")
        # Normalize port to int when possible
        try:
            port_val = int(port) if port else 0
        except ValueError:
            port_val = 0
        return {
            "host": host,
            "port": port_val,
            "database": database,
            "user": user,
            "password": password,
        }

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------
    def _on_accept(self) -> None:
        # Basic validation: require some market name
        name = self.market_name()
        if not name:
            QMessageBox.warning(self, "Ungültige Eingabe", "Bitte einen Marktnamen eingeben.")
            self._name_edit.setFocus()
            return

        # Validate server info (host required, port numeric within range)
        ui = self._server_ui
        host = getattr(ui, "lineEditHost", None)
        portw = getattr(ui, "lineEditPort", None)
        host_val = host.text().strip() if host else ""
        port_val = portw.text().strip() if portw else ""

        if not host_val:
            QMessageBox.warning(self, "Ungültige Eingabe", "Bitte einen Server-Host angeben (z. B. localhost).")
            # Switch to server tab and focus
            try:
                self._tabs.setCurrentIndex(self._server_tab_index)
                if host:
                    host.setFocus()
            except Exception:
                pass
            return

        try:
            pval = int(port_val) if port_val else 0
        except ValueError:
            pval = 0
        if pval < 1 or pval > 65535:
            QMessageBox.warning(self, "Ungültige Eingabe", "Bitte einen gültigen Port (1–65535) angeben.")
            try:
                self._tabs.setCurrentIndex(self._server_tab_index)
                if portw:
                    portw.setFocus()
            except Exception:
                pass
            return

        self.accept()
