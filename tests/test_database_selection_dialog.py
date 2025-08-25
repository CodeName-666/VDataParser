import sys
from pathlib import Path
import os
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
pytest.importorskip("PySide6")

from PySide6.QtWidgets import QApplication
from ui import database_selection_dialog as dlg_module


def test_accept_returns_selection():
    app = QApplication.instance() or QApplication([])  # noqa: F841 - keep reference
    dlg = dlg_module.DatabaseSelectionDialog(["db1", "db2"])  # pragma: no cover - simple dialog
    dlg.ui.databaseList.setCurrentRow(1)
    dlg.accept()
    assert dlg.get_selection() == "db2"


def test_cancel_returns_none():
    app = QApplication.instance() or QApplication([])  # noqa: F841 - keep reference
    dlg = dlg_module.DatabaseSelectionDialog(["db1"])
    dlg.ui.databaseList.setCurrentRow(0)
    dlg.reject()
    assert dlg.get_selection() is None
