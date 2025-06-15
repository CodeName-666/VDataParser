
from src.data import MarketConfigHandler


# -------------------- minimal ad‑hoc test ------------------------ #
if __name__ == "__main__":
    import json
    import tempfile

    user_json = {
        "database": {"url": "db.local", "port": "5432"},
        "market": {"market_path": "/var/market", "market_name": "Test"},
    }

    pm = MarketConfigHandler(user_json)
    print("Database before:", pm.get_database())
    pm.set_database("https://newdb", "6000")
    print("Database after: ", pm.get_database())

    with tempfile.NamedTemporaryFile("w+", suffix=".json", delete=False) as fp:
        pm.save_to(fp.name)
        print("Saved to", fp.name)
        print(json.dumps(pm.json_data, indent=2, ensure_ascii=False))