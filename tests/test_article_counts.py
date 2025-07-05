import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))

import pytest
pytest.importorskip('PySide6')
from data.data_manager import DataManager

TEST_JSON = Path(__file__).parent / 'test_dataset.json'


def setup_module(module):
    if not TEST_JSON.exists():
        raise RuntimeError('missing dataset')


def test_article_status_counts():
    data = json.loads(TEST_JSON.read_text())
    dm = DataManager(data)
    assert dm.get_article_count('1') == 1
    assert dm.get_partial_article_count('1') == 2
    assert dm.get_open_article_count('1') == 1
