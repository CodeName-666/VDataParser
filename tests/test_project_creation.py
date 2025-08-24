import sys
from pathlib import Path
import types

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

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
    Yes = 0
    No = 1
    Question = 2

    def setIcon(self, *args, **kwargs):
        pass

    def setWindowTitle(self, *args, **kwargs):
        pass

    def setText(self, *args, **kwargs):
        pass

    def setStandardButtons(self, *args, **kwargs):
        pass

    def setDefaultButton(self, *args, **kwargs):
        pass

    def exec(self):
        return QMessageBox.No


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


def test_load_export_creates_project(tmp_path):
    export_src = Path(__file__).parent / "test_dataset.json"
    export = tmp_path / export_src.name
    export.write_text(export_src.read_text())

    facade = MarketFacade()
    market = DummyMarket()

    ret = facade.load_local_market_export(market, str(export))
    assert ret is True

    observer = facade.get_observer(market)
    assert observer is not None

    observer._ask_for_default_pdf_config = lambda: False
    ok, target = facade.create_project_from_export(
        market, str(export), str(tmp_path)
    )

    assert ok is True
    assert observer.project_exists()
    assert (
        observer.market_config_handler.get_full_market_path()
        == str(Path(tmp_path) / export.name)
    )

