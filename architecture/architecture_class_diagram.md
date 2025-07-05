# Architektur Klassendiagramm

Dieses Diagramm skizziert die wichtigsten Klassen der Anwendung und ihr
Zusammenspiel. Über die Fassade `MarketFacade` werden Daten geladen,
Konfigurationsdateien eingelesen und verschiedene Generatoren angestoßen. Die
Daten selbst werden im `DataManager` verwaltet und in der Klasse `FleatMarket`
für die Ausgabe aufbereitet.

```mermaid
classDiagram
    class MarketFacade {
        +load_local_market_project()
        +load_local_market_export()
        +create_pdf_data()
        +create_market_data()
    }
    class MarketConfigHandler {
        +load()
    }
    class PdfDisplayConfig {
        +load()
    }
    class MarketObserver
    class DataManager {
        +load()
        +get_seller_as_list()
        +get_main_number_as_list()
    }
    class BasicDBConnector
    class AdvancedDBManager
    class MySQLInterface
    class FileGenerator {
        +generate()
    }
    class PriceListGenerator
    class SellerDataGenerator
    class StatisticDataGenerator
    class ReceiveInfoPdfGenerator
    class FleatMarket {
        +load_sellers()
        +load_main_numbers()
    }
    class MainWindow
    MarketFacade --> MarketConfigHandler : konfiguriert
    MarketFacade --> PdfDisplayConfig : PDF-Layout
    MarketFacade --> MarketObserver : informiert
    MarketFacade --> DataManager : verwendet
    MarketFacade --> FleatMarket : erstellt
    MarketFacade --> FileGenerator : nutzt
    FileGenerator --> PriceListGenerator
    FileGenerator --> SellerDataGenerator
    FileGenerator --> StatisticDataGenerator
    FileGenerator --> ReceiveInfoPdfGenerator
    FileGenerator --> FleatMarket : liest Daten
    DataManager --> SellerDataClass
    DataManager --> MainNumberDataClass
    MarketFacade --> AdvancedDBManager : nutzt DB
    AdvancedDBManager --|> BasicDBConnector
    BasicDBConnector --> MySQLInterface
    MainWindow --> MarketFacade : benutzt
```
