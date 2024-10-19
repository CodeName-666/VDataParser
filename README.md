# Python Project: Flea Market Data Generator

## Projektbeschreibung

Dieses Python-Projekt ist darauf ausgelegt, Verkaufsdaten und Artikellisten zu generieren, die in einem Flohmarkt- oder Verkaufsumfeld verwendet werden können. Es unterstützt die Verwaltung von Artikeln, Verkäufern und Preislisten. Das Projekt bietet Funktionen zum Laden von Daten aus JSON-Dateien und zur Generierung von Berichten oder Datenlisten in verschiedenen Formaten.

## Architektur

Das Projekt ist modular aufgebaut und besteht aus mehreren Komponenten:

- **main.py**: Der Einstiegspunkt des Programms. Dieser führt die verschiedenen Module und Generatoren zusammen.
- **data**: Beinhaltet alle Klassen und Funktionen, die für das Laden und Verarbeiten von Daten aus externen Dateien (z. B. JSON) notwendig sind.
  - `base_data.py`: Basisklasse für alle Datenmodelle.
  - `data_class_definition.py`: Definiert die Datenklassen für das Projekt.
  - `json_loader.py`: Lädt Daten aus JSON-Dateien.
- **generator**: Enthält verschiedene Generatoren zur Erstellung von Daten wie Artikellisten, Preislisten oder Verkäufern.
  - `data_generator.py`: Verantwortlich für die Generierung von Datenobjekten.
  - `file_generator.py`: Erzeugt Dateien basierend auf den generierten Daten.
  - `price_list_generator.py`: Erzeugt Preislisten für Artikel.
  - `seller_data_generator.py`: Generiert Verkäuferdaten.
- **log**: Loggt wichtige Ereignisse und Informationen, um die Nachverfolgbarkeit zu gewährleisten.
  - `logger.py`: Enthält die Logik zur Protokollierung.
- **objects**: Definiert die Hauptobjekte wie Artikel, Verkäufer und Flohmarkt, die in den Datenmodellen verwendet werden.
  - `article.py`: Modelliert einen Verkaufsartikel.
  - `fleat_market.py`: Modelliert einen Flohmarkt.
  - `main_number.py`: Beinhaltet die Logik für die Hauptnummernverwaltung.
  - `seller.py`: Modelliert einen Verkäufer.

## Implementierung

### Installation

Um das Projekt auszuführen, benötigen Sie Python 3.x und einige Abhängigkeiten, die in der Datei `requirements.txt` aufgelistet sein sollten. Wenn keine vorhanden ist, können Sie die Abhängigkeiten manuell installieren:

```bash
pip install -r requirements.txt

```

### Ausführung

Das Projekt kann über die main.py ausgeführt werden. Dies ist der zentrale Startpunkt für alle Datenoperationen und Generierungen.

```bash
python main.py

```