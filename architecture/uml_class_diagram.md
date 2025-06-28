# UML Klassendiagramm

Das UML‑Diagramm bildet die zentralen Klassen des Projekts ab. Es zeigt, wie die
GUI über `MainWindow` mit der `MarketFacade` kommuniziert und welche Generatoren
für die Dateiausgabe verantwortlich sind.

```mermaid
classDiagram
    class Main {
        +main()
    }
    class MainWindow
    class MarketObserver
    class MarketFacade
    class MarketConfigHandler
    class PdfDisplayConfig
    class DataManager
    class BaseData
    class BasicDBConnector
    class AdvancedDBManager
    class MySQLInterface
    class FileGenerator
    class PriceListGenerator
    class SellerDataGenerator
    class StatisticDataGenerator
    class ReceiveInfoPdfGenerator
    class FleatMarket
    class SellerDataClass
    class MainNumberDataClass

    Main --> MarketFacade
    Main --> MainWindow
    MainWindow --> MarketObserver
    MarketObserver --> MarketFacade
    MarketFacade --> DataManager
    MarketFacade --> FileGenerator
    MarketFacade --> FleatMarket
    MarketFacade --> MarketConfigHandler
    MarketFacade --> PdfDisplayConfig
    DataManager --|> BaseData
    DataManager --> SellerDataClass
    DataManager --> MainNumberDataClass
    MarketFacade --> AdvancedDBManager
    AdvancedDBManager --|> BasicDBConnector
    BasicDBConnector --> MySQLInterface
    FileGenerator --> PriceListGenerator
    FileGenerator --> SellerDataGenerator
    FileGenerator --> StatisticDataGenerator
    FileGenerator --> ReceiveInfoPdfGenerator
```
