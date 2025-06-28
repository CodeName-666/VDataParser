from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from version import get_version


def test_version_format():
    version = get_version()
    assert isinstance(version, str)
    parts = version.split(".")
    assert len(parts) == 3
    assert all(part.isdigit() for part in parts)

