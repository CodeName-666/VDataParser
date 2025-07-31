import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pytest
pytest.importorskip('PySide6')

from src.data.data_manager import DataManager
from src.objects import SettingsContentDataClass

DATASET = Path(__file__).parent / 'test_dataset.json'


def test_settings_changes_logged():
    data = json.loads(DATASET.read_text())
    dm = DataManager(data)

    new_settings = SettingsContentDataClass(max_stammnummern='5', max_artikel='20')
    dm.set_new_settings(new_settings)

    log_targets = [entry['target'] for entry in dm.get_change_log()]
    assert 'settings:max_stammnummern' in log_targets
    assert 'settings:max_artikel' in log_targets
    assert len(log_targets) >= 2
