import json
from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))

pytest.importorskip('PySide6')

from data.data_manager import DataManager

DATASET = Path(__file__).parent / 'test_dataset_empty.json'


def test_empty_seller_grouping():
    data = json.loads(DATASET.read_text())
    dm = DataManager(data)
    aggregated = dm.get_aggregated_users()
    assert '<LEER>' in aggregated
    empty_group = aggregated['<LEER>']
    assert '2' in empty_group['ids']
    stnr_names = [tbl.name for tbl in empty_group['stamms']]
    assert 'stnr2' in stnr_names

    # representation helpers
    agg_list = dm.get_aggregated_users_data()
    assert any(u["vorname"] == "<Leer>" for u in agg_list)
    assert agg_list[-1]["vorname"] == "<Leer>"
    flat_list = dm.get_users_data()
    assert any(u["id"] == "2" and u["vorname"] == "<Leer>" for u in flat_list)
    assert flat_list[-1]["vorname"] == "<Leer>"
