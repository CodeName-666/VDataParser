import pytest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

pytest.importorskip("PySide6")

from PySide6.QtWidgets import QMainWindow  # noqa: E402
from ui.main_window import MainWindow  # noqa: E402


def test_main_window_inheritance():
    assert issubclass(MainWindow, QMainWindow)

