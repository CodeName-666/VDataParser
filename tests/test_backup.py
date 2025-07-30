import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))

import pytest
pytest.importorskip('PySide6')

from data.data_manager import DataManager

DATASET = Path(__file__).parent / 'test_dataset.json'


def test_backup_creation(tmp_path):
    dm = DataManager(str(DATASET))
    target = tmp_path / 'market.json'
    dm.save(str(target))
    assert target.is_file()
    dm.save(str(target))
    backup1 = tmp_path / 'market.json_1.backup'
    assert backup1.is_file()
    dm.save(str(target))
    backup2 = tmp_path / 'market.json_2.backup'
    assert backup2.is_file()
