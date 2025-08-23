from pathlib import Path
import importlib.util
import sys


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

spec = importlib.util.spec_from_file_location(
    "json_handler", Path(__file__).resolve().parents[1] / "src" / "data" / "json_handler.py"
)
json_handler_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(json_handler_module)
JsonHandler = json_handler_module.JsonHandler

DATASET = Path(__file__).parent / "test_dataset.json"


def test_backup_creation_only_on_change(tmp_path):
    jh = JsonHandler(str(DATASET))
    target = tmp_path / "market.json"

    jh.save(str(target))
    assert target.is_file()
    backup1 = tmp_path / "market.json_1.backup"
    backup2 = tmp_path / "market.json_2.backup"

    # Saving identical data should not create a backup
    jh.save(str(target))
    assert not backup1.exists()

    # Modify data and ensure a backup is created
    jh.json_data[1]["name"] = "changed"
    jh.save(str(target))
    assert backup1.is_file()

    # Another change results in a second backup
    jh.json_data[1]["name"] = "changed_again"
    jh.save(str(target))
    assert backup2.is_file()

