import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

pytest.importorskip("PySide6")

from data.market_facade import MarketFacade, MarketObserver


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


def test_create_new_project_stores_db_credentials(tmp_path, monkeypatch):
    """Ensure database credentials (without password) are persisted."""
    facade = MarketFacade()
    market = DummyMarket()

    monkeypatch.setattr(MarketObserver, "_load_default_pdf_config", lambda self, path: None)
    monkeypatch.setattr(MarketObserver, "setup_data_generation", lambda self: None)

    server_info = {
        "host": "localhost",
        "port": 3306,
        "database": "mydb",
        "user": "dbuser",
        "password": "secret",
    }

    assert facade.create_new_project(market, str(tmp_path), "market.json", None, server_info)

    data = json.loads((tmp_path / "project.project").read_text())
    db = data.get("database", {})
    assert db["url"] == "localhost"
    assert db["port"] == "3306"
    assert db["name"] == "mydb"
    assert db["user"] == "dbuser"
    assert "password" not in db
