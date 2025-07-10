from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))

import pytest
pytest.importorskip('PySide6')

from data.market_facade import MarketFacade
from data.market_facade import MarketObserver
from data.market_config_handler import MarketConfigHandler
from data.data_manager import DataManager
from data.pdf_display_config import PdfDisplayConfig


def _prepare_observer():
    dataset = Path(__file__).parent / 'test_dataset.json'
    dm = DataManager(str(dataset))
    pdf = Path(__file__).resolve().parents[1] / 'src' / 'resource' / 'default_data' / 'Abholung_Template.pdf'
    pdf_cfg = PdfDisplayConfig({'pdf_path': str(pdf.parent), 'pdf_name': pdf.name})
    mch = MarketConfigHandler()
    mch.set_market('', 'market.json')
    mch.set_pdf_coordinates_config('', 'pdf_display_config.json')
    obs = MarketObserver()
    obs.data_manager = dm
    obs.pdf_display_config_loader = pdf_cfg
    obs.market_config_handler = mch
    return obs


def test_save_project(tmp_path):
    obs = _prepare_observer()
    assert obs.save_project(str(tmp_path))
    assert (tmp_path / 'market.json').is_file()
    assert (tmp_path / 'pdf_display_config.json').is_file()
    assert (tmp_path / 'project.json').is_file()
    pdf = Path(__file__).resolve().parents[1] / 'src' / 'resource' / 'default_data' / 'Abholung_Template.pdf'
    assert (tmp_path / pdf.name).is_file()


def test_facade_save_project(tmp_path):
    facade = MarketFacade()
    market = object()
    observer = facade.create_observer(market)
    custom = _prepare_observer()
    # replace stored observer with prepared one
    index = next(i for i, (m, _) in enumerate(facade._market_list) if m == market)
    facade._market_list[index] = (market, custom)

    assert facade.save_project(market, str(tmp_path))
    assert (tmp_path / 'market.json').is_file()
    assert (tmp_path / 'pdf_display_config.json').is_file()
    assert (tmp_path / 'project.json').is_file()
    pdf = Path(__file__).resolve().parents[1] / 'src' / 'resource' / 'default_data' / 'Abholung_Template.pdf'
    assert (tmp_path / pdf.name).is_file()
