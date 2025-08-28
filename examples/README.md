# Examples Overview

Diese README beschreibt jedes Python‑Skript im Ordner `examples/` mit Zweck, Nutzung und Voraussetzungen.

Hinweis: Viele Skripte fügen den Projekt‑Root und/oder `src/` dem `PYTHONPATH` hinzu, damit die Modul‑Imports funktionieren. Starte sie daher idealerweise aus dem Projekt‑Root mit `python examples/<script>.py`.

---

## advanced_db_manager_mysql_example.py

Beschreibung:
- Demonstriert den `AdvancedDBManager` mit MySQL ohne Eventloop. Erstellt (falls nötig) eine Demo‑Datenbank, führt CRUD‑Operationen auf einer Tabelle `personen` aus und trennt die Verbindung wieder. Emittiert Verbindungs‑Signale (werden im Beispiel für Konsolen‑Ausgabe verbunden).

Voraussetzungen:
- `mysql-connector-python` installiert und MySQL‑Server erreichbar
- `PySide6` (für die Signals/Timer‑Basis des `AdvancedDBManager`)

Konfiguration (Umgebungsvariablen mit Defaults):
- `MYSQL_HOST` (Default: `localhost`)
- `MYSQL_PORT` (Default: `3306`)
- `MYSQL_USER` (Default: `test`)
- `MYSQL_PASSWORD` (Default: `exec1234`)
- `MYSQL_DB` (Default: `advanced_db_manager_demo`)
- `ADVANCED_DB_DROP_ON_EXIT=1` um die Demo‑Datenbank am Ende zu löschen

Nutzung:
- `python examples/advanced_db_manager_mysql_example.py`

---

## advanced_db_manager_mysql_qt_loop.py

Beschreibung:
- Wie oben, jedoch mit laufender Qt‑Eventloop (`QCoreApplication`). Zeigt die Signale `connecting`, `connected`, `disconnected`, führt eine periodische Demo‑Abfrage aus (Health‑Check sichtbar) und beendet nach konfigurierbarer Dauer automatisch.

Voraussetzungen:
- `mysql-connector-python` installiert und MySQL‑Server erreichbar
- `PySide6`

Konfiguration (Umgebungsvariablen):
- wie bei `advanced_db_manager_mysql_example.py`

Zusätzliche CLI‑Argumente:
- `--duration <sek>`: Sekunden bis zum Auto‑Exit (Default: 30)
- `--interval <sek>`: Intervall für die Demo‑Abfrage (Default: 5)

Nutzung:
- `python examples/advanced_db_manager_mysql_qt_loop.py --duration 45 --interval 5`

---

## basic_db_connector.py

Beschreibung:
- Zeigt die Nutzung des generischen `BasicDBConnector` mit zwei Backends: SQLite und MySQL. Enthält zwei Funktionen `sqlite_example()` und `mysql_example()` und führt standardmäßig das MySQL‑Beispiel aus (siehe `__main__`).

Voraussetzungen:
- Für SQLite: keine externen Pakete
- Für MySQL: `mysql-connector-python` und erreichbarer MySQL‑Server

Hinweise:
- Zum SQLite‑Beispiel: den Aufruf `sqlite_example()` im `__main__` entsperren/aktivieren.
- Das MySQL‑Beispiel legt eine Test‑Datenbank an und kann sie am Ende optional wieder löschen.

Nutzung:
- `python examples/basic_db_connector.py`

---

## article_example.py

Beschreibung:
- Demonstriert `Article` und `ArticleDataClass`: Initialisierung, Validierung, Update der Daten sowie optionales Logging via `CustomLogger`.

Voraussetzungen:
- Internes Modul `src.objects.Article`, `src.data.ArticleDataClass`, optional `src.log.logger.CustomLogger`

Hinweise:
- Falls beim Start ein `NameError: List` auftritt, bitte `from typing import List` ergänzen oder die Typannotationen der Listen entfernen (nur für die Demo relevant).

Nutzung:
- `python examples/article_example.py`

---

## fleat_market_example.py

Beschreibung:
- Demonstriert das `FleatMarket`‑Objekt: Laden/Setzen von Verkäufer‑ und Hauptnummern‑Daten, Zugriff auf Listen und Elemente per Index, optionales Logging mit `CustomLogger`.

Voraussetzungen:
- Interne Module `src.objects.FleatMarket`, `src.data.SellerDataClass`, `src.data.MainNumberDataClass`, optional `src.log.logger.CustomLogger`

Hinweise:
- Wie bei `article_example.py` ggf. `from typing import List` ergänzen, falls der Interpreter über die Annotation `List[...]` stolpert.

Nutzung:
- `python examples/fleat_market_example.py`

---

## logger_example.py

Beschreibung:
- Zwei Beispiele für `CustomLogger`:
  - `example_1()`: Konsolen‑Logging, One‑Line‑Logging, Verbose‑Schalter, Fehlerbehandlung bei ungültigen Typen
  - `example_2()`: Logging in Datei via übergebenem `logging.FileHandler` (z. B. `app_activity.log`)

Voraussetzungen:
- `src.log.logger.CustomLogger`

Nutzung:
- `python examples/logger_example.py` (passt ggf. die aktivierten Funktionsaufrufe am Ende an)

---

## markt_loader_dialog_example.py

Beschreibung:
- Startet einen Qt‑Dialog (`MarketLoaderDialog`) zum Auswählen/Laden von Markt‑Bezogenen Informationen und gibt das Ergebnis auf der Konsole aus.

Voraussetzungen:
- `PySide6` und die generierten UI‑Artefakte im Projekt (bei Änderungen an `.ui` bitte `python util/generate_qt_artefacts.py --all` ausführen)

Nutzung:
- `python examples/markt_loader_dialog_example.py`

---

## output_window_example.py

Beschreibung:
- Startet ein Ausgabefenster (`OutputWindow`) und triggert in einem Hintergrund‑Thread die PDF‑Generierung über `FileGenerator`. Fortschritt wird über `BasicProgressTracker` in der UI angezeigt. Liest Daten aus `tests/test_dataset.json`.

Voraussetzungen:
- `PySide6`
- Interne Module: `data.data_manager.DataManager`, `objects.FleatMarket`, `generator.file_generator.FileGenerator`, `display.BasicProgressTracker`, `ui.output_window.OutputWindow`

Nutzung:
- `python examples/output_window_example.py`

---

## pdf_display_example.py

Beschreibung:
- Startet eine PDF‑Anzeige/Editor‑UI (`PdfDisplay`) als Hauptfenster (oder alternativ als Widget in einem `QMainWindow`).

Voraussetzungen:
- `PySide6`

Nutzung:
- `python examples/pdf_display_example.py`

---

## project_manager_example.py

Beschreibung:
- Minimalbeispiel für `MarketConfigHandler`: Laden/Setzen von Konfigurationswerten und Speichern in eine temporäre JSON‑Datei.

Voraussetzungen:
- Internes Modul `src.data.MarketConfigHandler`

Nutzung:
- `python examples/project_manager_example.py`

---

## qt_progress_bar_example.py

Beschreibung:
- Zeigt den `QtProgressBar` mit `BasicProgressTracker`. Führt eine Beispiel‑Aufgabe aus und visualisiert den Fortschritt in einem Qt‑Dialog.

Voraussetzungen:
- `PySide6`

Nutzung:
- `python examples/qt_progress_bar_example.py`

---

## qt_progress_dialog_example.py

Beschreibung:
- Demonstriert die Verwendung des internen `_ProgressDialog` inkl. eigener Thread‑Aufgabe, die den Fortschritt per Signal aktualisiert und am Ende das Ergebnis signalisiert.

Voraussetzungen:
- `PySide6`

Nutzung:
- `python examples/qt_progress_dialog_example.py`

---

## output_interface_example.py

Beschreibung:
- Platzhalter für ein zukünftiges Beispiel zur generischen Output‑Schnittstelle. Derzeit ohne Implementierung.

Nutzung:
- (keine – Datei ist leer)
