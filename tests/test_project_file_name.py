import sys
from pathlib import Path
import shutil
import types

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))

# Provide minimal PySide6 stubs for test environment
qtcore = types.ModuleType("PySide6.QtCore")
qtwidgets = types.ModuleType("PySide6.QtWidgets")


class QObject:  # pragma: no cover - simple stub
    pass


class Signal:  # pragma: no cover - simple stub
    def __init__(self, *args, **kwargs):
        pass

    def connect(self, *args, **kwargs):
        pass

    def emit(self, *args, **kwargs):
        pass


def Slot(*args, **kwargs):  # pragma: no cover - simple stub
    def decorator(func):
        return func
    return decorator


class QMessageBox:  # pragma: no cover - simple stub
    pass


qtcore.QObject = QObject
qtcore.Signal = Signal
qtcore.Slot = Slot
class QThread:  # pragma: no cover - simple stub
    def start(self):
        pass

    def quit(self):
        pass

    def wait(self):
        pass

qtcore.QThread = QThread
class QTimer:  # pragma: no cover - simple stub
    def start(self):
        pass

    def stop(self):
        pass

qtcore.QTimer = QTimer
qtwidgets.QMessageBox = QMessageBox

pyside6 = types.ModuleType("PySide6")
pyside6.QtCore = qtcore
pyside6.QtWidgets = qtwidgets

sys.modules.setdefault("PySide6", pyside6)
sys.modules.setdefault("PySide6.QtCore", qtcore)
sys.modules.setdefault("PySide6.QtWidgets", qtwidgets)

from data.market_facade import MarketFacade

class DummySignal:
    def connect(self, *args, **kwargs):
        pass

class DummyMarket:
    def __init__(self):
        self.pdf_display_storage_path_changed = DummySignal()
    def set_market_data(self, *args, **kwargs):
        pass
    def set_pdf_config(self, *args, **kwargs):
        pass


def test_project_file_matches_json(tmp_path):
    dataset = Path(__file__).parent / 'test_dataset.json'
    export = tmp_path / 'export_data.json'
    shutil.copy(dataset, export)

    facade = MarketFacade()
    market = DummyMarket()
    facade.create_observer(market)

    observer = facade.get_observer(market)
    observer._ask_for_default_pdf_config = lambda: False

    ret, target = facade.create_project_from_export(market, str(export), str(tmp_path))
    assert ret is True
    project_file = tmp_path / 'export_data.project'
    assert project_file.is_file()
