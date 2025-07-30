import sys
from pathlib import Path
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

pytest.importorskip("PySide6")

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

    import types, sys
    pyside6 = types.ModuleType('PySide6')
    qtcore = types.ModuleType('PySide6.QtCore')
    qtwidgets = types.ModuleType('PySide6.QtWidgets')
    class QObject: pass
    class Signal:
        def __init__(self, *a, **k):
            pass
    qtcore.QObject = QObject
    qtcore.Signal = Signal
    class QFileDialog:
        @staticmethod
        def getExistingDirectory(*a, **k):
            return str(tmp_path)
    qtwidgets.QFileDialog = QFileDialog
    pyside6.QtCore = qtcore
    pyside6.QtWidgets = qtwidgets
    sys.modules['PySide6'] = pyside6
    sys.modules['PySide6.QtCore'] = qtcore
    sys.modules['PySide6.QtWidgets'] = qtwidgets

    import data.market_facade as mf
    from data.market_facade import MarketFacade, MarketObserver
    original_get_dir = mf.QFileDialog.getExistingDirectory
    mf.QFileDialog.getExistingDirectory = staticmethod(lambda *a, **k: str(tmp_path))
    original_get_dir = mf.QFileDialog.getExistingDirectory
    mf.QFileDialog.getExistingDirectory = staticmethod(lambda *a, **k: str(tmp_path))
    facade = MarketFacade()
    market = DummyMarket()

    facade._ask_for_project_creation = lambda: True
    MarketObserver._ask_for_default_pdf_config = lambda self: False

    ret = facade.load_local_market_export(market, str(export))
    assert ret is True

    observer = facade.get_observer(market)
    assert observer is not None
    assert observer.project_exists()
    assert observer.market_config_handler.get_full_market_path() == str(Path(tmp_path) / export.name)
    mf.QFileDialog.getExistingDirectory = original_get_dir
    for mod in ['PySide6.QtWidgets', 'PySide6.QtCore', 'PySide6']:
        sys.modules.pop(mod, None)

