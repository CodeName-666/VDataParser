import sys
from pathlib import Path

import os
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
pytest.importorskip("PySide6")

from PySide6.QtWidgets import QApplication, QDialog, QMainWindow

from data.market_config_handler import MarketConfigHandler
from ui import main_window as mw_module
from ui import database_settings_dialog as dlg_module


class _Dialog(dlg_module.DatabaseSettingsDialog):
    def exec(self):  # pragma: no cover - simple override
        self._host_edit.setText("newhost")
        self._port_edit.setText("5432")
        self._name_edit.setText("newdb")
        self._user_edit.setText("newuser")
        self._password_edit.setText("secret")
        return QDialog.DialogCode.Accepted


def test_database_settings_applied(monkeypatch):
    app = QApplication.instance() or QApplication([])  # noqa: F841 - keep reference

    mch = MarketConfigHandler()
    mch.set_database("oldhost", "1111")
    mch.set_db_credentials("olddb", "olduser")

    monkeypatch.setattr(mw_module, "MarketConfigHandler", lambda: mch)
    monkeypatch.setattr(dlg_module, "MarketConfigHandler", lambda: mch)
    monkeypatch.setattr(mw_module, "DatabaseSettingsDialog", _Dialog)

    saved = {"called": False}

    def fake_save_project(self):
        saved["called"] = True

    monkeypatch.setattr(mw_module.MainWindow, "save_project", fake_save_project)

    def dummy_init(self):
        QMainWindow.__init__(self)

    monkeypatch.setattr(mw_module.MainWindow, "__init__", dummy_init)

    mw = mw_module.MainWindow()
    mw.open_database_settings_dialog()

    db = mch.get_database()
    assert db["url"] == "newhost"
    assert db["port"] == "5432"
    assert db["name"] == "newdb"
    assert db["user"] == "newuser"
    assert saved["called"]
