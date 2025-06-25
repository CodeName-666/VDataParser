# VDataParser – Flohmarkt Daten und PDF Generator

## Projektüberblick

Dieses Repository enthält eine Python‑Anwendung zur Verwaltung und Aufbereitung von Flohmarkt‑Daten. Aus einer JSON‑Datei oder einer Datenbank werden Verkäufer, Artikellisten sowie weitere Informationen eingelesen und in verschiedene Ausgabeformate überführt. Neben klassischen `.dat`‑Dateien kann das Programm auch Abholbestätigungen als PDF erzeugen. Die Anwendung besitzt einen Kommandozeilenmodus und eine Qt‑basierte GUI.

## Installation

1. Python 3.10 oder neuer installieren.
2. Abhängigkeiten mittels `pip` einrichten:
   ```bash
   pip install -r src/requirements.txt
   ```
   Für die optionalen MySQL‑Funktionen muss zusätzlich `mysql-connector-python` vorhanden sein.

## Nutzung

Das Programm kann entweder als CLI oder über die GUI gestartet werden. Wird beim Aufruf ein JSON‑Pfad übergeben, startet automatisch der CLI‑Modus. Ohne Parameter öffnet sich die GUI.

### CLI
```bash
python -m src.main -f <path/to/data.json> [-p <out-dir>] [--pdf-template <template.pdf>]
```
Eine ausführliche Hilfe zu allen Optionen erhält man über `-h`.

### GUI
```bash
python -m src.main
```
In der grafischen Oberfläche lassen sich Projekte laden, Daten kontrollieren und alle Ausgabedateien erzeugen.

## Projektstruktur

- **src/main.py** – Einstiegspunkt, entscheidet je nach Argumenten zwischen CLI und GUI.
- **src/args.py** – Sammelt sämtliche Kommandozeilenparameter.
- **src/backend/** – Datenbankschicht mit einheitlicher Schnittstelle (`DatabaseOperations`). Implementierungen für SQLite und MySQL ermöglichen den Austausch der konkreten Technik (Strategy‑Pattern).
- **src/data/** – Laden und Aufbereiten der JSON‑ bzw. Projektdaten. Enthält u. a. `DataManager`, `MarketConfigHandler` und `PdfDisplayConfig`.
- **src/generator/** – Verschiedene Generatoren zum Erstellen von Dateien (Preislisten, Verkäufer‑ und Statistikdaten sowie PDFs). `FileGenerator` koordiniert alle Untergeneratoren.
- **src/objects/** – Domänenobjekte wie `Seller`, `Article` und `MainNumber` mitsamt zugehöriger Dataklassen.
- **src/display/** – Abstraktionen für Fortschrittsbalken und Ausgabekanäle (Konsole oder Qt Widgets).
- **src/ui/** – Qt‑Oberfläche.
- **src/log/** – Schlankes Logging‑System (`CustomLogger`).

## Architektur und wichtige Techniken

- **Singleton**: `SingletonMeta` garantiert einzelne Instanzen für Klassen wie `MarketFacade`. Dadurch existiert die Anwendung global nur einmal pro Markt‑Facade.
- **Facade**: `MarketFacade` kapselt komplexe Abläufe (Laden von Projekten, Erzeugen der Dateien) hinter einer vereinfachten Schnittstelle für die GUI.
- **Observer (Signal/Slot)**: In der GUI kommunizieren Klassen über Qt‑Signale (`data_loaded`, `status_info`). So werden Statusänderungen an die Oberfläche weitergereicht.
- **Strategy**: Für Datenbankzugriffe wird über `DatabaseOperations` eine gemeinsame Schnittstelle definiert. `SQLiteInterface` und `MySQLInterface` implementieren dieselben Methoden, sodass `BasicDBConnector` beide Varianten nutzen kann.
- **Dataclasses**: Datenstrukturen wie Artikel oder Verkäufer basieren auf Python‑`dataclasses` und erlauben eine einfache Serialisierung/Deserialisierung.
- **Progress‑Tracker**: Über abstrakte Tracker und Progressbars kann der Fortschritt sowohl in der Konsole als auch in der GUI angezeigt werden.

## Hinweise zum Einsatz

- Die JSON‑Struktur des Flohmarktes entspricht den Klassen in `src/objects/data_class_definition.py`. Beispiel‑ und Testdateien befinden sich im Repository (`test_db.json`, `test_project.json`).
- Pfade im Projekt (z. B. zu PDF‑Vorlagen) werden relativ zum Arbeitsverzeichnis aufgelöst. Stellen Sie sicher, dass Vorlagen vorhanden sind.
- Bei Verwendung von MySQL müssen Zugangsdaten in der Konfiguration hinterlegt sein.
- Fehler und Statusmeldungen werden je nach Modus auf der Konsole, in Logdateien oder innerhalb der GUI ausgegeben.

## Weiterführende Informationen

Die detaillierte API der einzelnen Module ist in den Quelltexten kommentiert. Für eigene Anpassungen können neue Generatoren oder Datenquellen über die vorhandenen Abstraktionen implementiert werden.
