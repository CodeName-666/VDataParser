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
    export = Path(__file__).parent / "test_dataset.json"
    facade = MarketFacade()
    market = DummyMarket()

    ret = facade.load_local_market_export(market, str(export))
    assert ret is True

    observer = facade.get_observer(market)
    assert observer is not None
    assert observer.project_exists()
    assert observer.market_config_handler.get_full_market_path() == str(export)

