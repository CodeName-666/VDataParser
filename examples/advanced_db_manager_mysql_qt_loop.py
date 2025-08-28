"""AdvancedDBManager MySQL + Qt-Eventloop Beispiel.

Dieses Beispiel startet eine Qt-Eventloop (QCoreApplication), verbindet den
AdvancedDBManager mit einem MySQL-Server und zeigt seine Signale (connecting,
connected, disconnected). Zusätzlich läuft ein periodischer Timer, der eine
leichte Abfrage ausführt. Nach einer konfigurierbaren Dauer beendet sich das
Programm wieder sauber.

Voraussetzungen:
- ``mysql-connector-python`` installiert und MySQL-Server erreichbar
- ``PySide6`` installiert (für QCoreApplication/QTimer)

Konfiguration via Umgebungsvariablen (mit Standardwerten):
- ``MYSQL_HOST`` (Standard: ``localhost``)
- ``MYSQL_PORT`` (Standard: ``3306``)
- ``MYSQL_USER`` (Standard: ``test``)
- ``MYSQL_PASSWORD`` (Standard: ``exec1234``)
- ``MYSQL_DB`` (Standard: ``advanced_db_manager_demo``)
- ``ADVANCED_DB_DROP_ON_EXIT`` (``1`` zum Droppen der Test-DB am Ende)

Optionale CLI-Argumente:
- ``--duration`` Sekunden bis zum automatischen Beenden (Standard: 30)
- ``--interval`` Intervall für Demo-Abfrage in Sekunden (Standard: 5)
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from PySide6.QtCore import QCoreApplication, QTimer

# Projektwurzel zum PYTHONPATH hinzufügen
sys.path.insert(0, Path(__file__).parent.parent.__str__())  # NOQA: E402

from src.backend.advance_db_connector import AdvancedDBManager  # NOQA: E402
from src.backend.basic_db_connector import BasicDBConnector  # NOQA: E402
from src.backend import (  # NOQA: E402
    MySQLInterface,
    DatabaseConnectionError,
    DatabaseQueryError,
    MYSQL_AVAILABLE,
)


def _read_config_from_env() -> dict:
    """Read MySQL connection parameters from environment variables."""
    return {
        "host": os.environ.get("MYSQL_HOST", "localhost"),
        "port": int(os.environ.get("MYSQL_PORT", "3306")),
        "user": os.environ.get("MYSQL_USER", "test"),
        "password": os.environ.get("MYSQL_PASSWORD", "exec1234"),
        "database": os.environ.get("MYSQL_DB", "advanced_db_manager_demo"),
    }


def _ensure_database(cfg: dict) -> bool:
    """Ensure that the configured database exists on the server."""
    server_cfg = {k: v for k, v in cfg.items() if k != "database"}
    server_op = MySQLInterface(**server_cfg)
    server_conn = BasicDBConnector(server_op)
    try:
        server_conn.create_database(cfg["database"])
        return True
    except (DatabaseConnectionError, DatabaseQueryError) as e:
        print(f"Fehler beim Erstellen/Prüfen der DB '{cfg['database']}': {e}")
        return False
    finally:
        server_conn.disconnect()


def main() -> None:
    if not MYSQL_AVAILABLE:
        print("MySQL-Beispiel übersprungen: mysql-connector-python nicht installiert/verfügbar.")
        return

    parser = argparse.ArgumentParser(description="AdvancedDBManager MySQL + Qt-Loop Demo")
    parser.add_argument("--duration", type=int, default=30, help="Sekunden bis zum automatischen Beenden")
    parser.add_argument("--interval", type=int, default=5, help="Intervall für Demo-Abfragen (Sekunden)")
    args = parser.parse_args()

    cfg = _read_config_from_env()
    if not _ensure_database(cfg):
        return

    # Qt-Eventloop
    app = QCoreApplication(sys.argv)

    # AdvancedDBManager initialisieren und Signale verbinden
    op = MySQLInterface(**cfg)
    manager = AdvancedDBManager(op)
    manager.connecting.connect(lambda: print("[Signal] Connecting…"))
    manager.connected.connect(lambda: print("[Signal] Connected."))
    manager.disconnected.connect(lambda: print("[Signal] Disconnected."))

    # Beim Programmende aufräumen (Disconnect und optional DB droppen)
    def _cleanup() -> None:
        try:
            manager.disconnect()
        except Exception as e:  # noqa: BLE001 – Beispielcode
            print(f"Warnung beim Disconnect: {e}")

        if os.environ.get("ADVANCED_DB_DROP_ON_EXIT") == "1":
            try:
                server_cfg = {k: v for k, v in cfg.items() if k != "database"}
                cleanup_op = MySQLInterface(**server_cfg)
                cleanup = BasicDBConnector(cleanup_op)
                if cleanup.database_exists(cfg["database"]):
                    cleanup.execute_query(f"DROP DATABASE IF EXISTS `{cfg['database']}`")
                    print(f"Test-Datenbank '{cfg['database']}' gelöscht.")
                cleanup.disconnect_from_db()
            except Exception as e:  # noqa: BLE001 – Beispielcode
                print(f"Aufräumen fehlgeschlagen: {e}")

    app.aboutToQuit.connect(_cleanup)

    # Verbindung aufbauen, sobald die Eventloop gestartet ist
    QTimer.singleShot(0, manager.connect_to_db)

    # Demo: Tabelle sicherstellen und periodische Abfrage ausführen
    def _ensure_table_and_tick() -> None:
        try:
            create_sql = (
                "CREATE TABLE IF NOT EXISTS personen ("
                " id INT AUTO_INCREMENT PRIMARY KEY,"
                " name VARCHAR(255) NOT NULL UNIQUE,"
                " alter_jahre INT)"
                " ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;"
            )
            manager.execute_query(create_sql)
        except (DatabaseConnectionError, DatabaseQueryError) as e:
            print(f"Fehler bei Tabellen-Setup: {e}")

    def _tick() -> None:
        try:
            # leichte Abfrage – funktioniert auch ohne Tabelle
            manager.execute_query("SELECT 1", fetch=None)
            print("[Tick] SELECT 1 ausgeführt")
        except (DatabaseConnectionError, DatabaseQueryError) as e:
            print(f"[Tick] Fehler: {e}")

    # Tabelle anlegen, wenn verbunden; dann periodischen Tick starten
    QTimer.singleShot(1000, _ensure_table_and_tick)
    ticker = QTimer()
    ticker.setInterval(max(1, args.interval) * 1000)
    ticker.timeout.connect(_tick)
    ticker.start()

    # Automatisch nach duration Sekunden beenden
    QTimer.singleShot(max(1, args.duration) * 1000, app.quit)

    print(
        f"Qt-Loop gestartet. Dauer: {args.duration}s, Intervall: {args.interval}s. "
        "Beende mit Ctrl+C oder warte auf Auto-Exit."
    )
    try:
        app.exec()
    except KeyboardInterrupt:
        print("Interrupted. Beende…")
        app.quit()


if __name__ == "__main__":
    main()

