# Abhängigkeitsdiagramm

Dieses Diagramm zeigt die groben Modulabhängigkeiten der Anwendung. Der Start
erfolgt über `main.py`, das wahlweise die Kommandozeile oder die Qt‑Oberfläche
aufbaut. Die Fassade `MarketFacade` kapselt Datenzugriff, Konfiguration und die
Erzeugung der Ausgabedateien.

```mermaid
graph TD
    Main --> Args
    Main --> MarketFacade
    Main --> UI
    UI --> MarketObserver
    MarketObserver --> MarketFacade
    MarketFacade --> DataManager
    MarketFacade --> FileGenerator
    MarketFacade --> MarketConfigHandler
    MarketFacade --> PdfDisplayConfig
    DataManager --> Objects
    MarketFacade --> Backend
    Backend --> MySQLInterface
    FileGenerator --> Generators
    Generators --> PriceListGenerator
    Generators --> SellerDataGenerator
    Generators --> StatisticDataGenerator
    Generators --> ReceiveInfoPdfGenerator
    Main --> Display
    Display --> ProgressBar
    Display --> Output
```
