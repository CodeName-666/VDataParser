import sys
from pathlib import Path
import shutil
import pytest

pytest.importorskip('PySide6')

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))

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
