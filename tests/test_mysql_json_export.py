import json
from datetime import datetime
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))

from backend.advance_db_connector import AdvancedDBManager
from backend.interface.common_interface import DatabaseOperations


class DummyOps(DatabaseOperations):
    def __init__(self):
        super().__init__({})

    def connect_db(self, database_override: str | None = None):
        return None

    def disconnect_db(self, conn):
        pass

    def execute_db_query(self, conn, query: str, params: tuple | None = None, fetch: str | None = None):
        pass

    def check_database_exists(self, db_name: str) -> bool:
        return True

    def create_db(self, new_db_name: str):
        pass

    def list_databases(self, prefix: str | None = None) -> list[str]:
        return []

    def get_placeholder_style(self) -> str:
        return "%s"

    def get_db_specific_error_types(self) -> tuple:
        return (Exception,)


class DummyCursor:
    def __init__(self, dictionary: bool = False):
        self.dictionary = dictionary
        self.query = ""

    def execute(self, query: str):
        self.query = query

    def fetchall(self):
        if "SHOW TABLES" in self.query:
            return [("example",)]
        if "SELECT * FROM example" in self.query and self.dictionary:
            return [{"id": 1, "created": datetime(2024, 1, 1, 12, 0, 0)}]
        return []

    def close(self):
        pass


class DummyConn:
    def cursor(self, dictionary: bool = False):
        return DummyCursor(dictionary=dictionary)



def test_export_handles_datetime(tmp_path: Path):
    manager = AdvancedDBManager(DummyOps())
    manager.conn = DummyConn()
    manager.db_type = "mysql"

    out_file = tmp_path / "out.json"
    manager.export_to_custom_json(str(out_file))

    content = json.loads(out_file.read_text(encoding="utf-8"))
    tables = [item for item in content if item.get("type") == "table"]
    assert tables[0]["data"][0]["created"] == "2024-01-01 12:00:00"
