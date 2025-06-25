# Abhängigkeitsdiagramm

```mermaid
graph TD
    Main --> Args
    Main --> MarketFacade
    MarketFacade --> DataManager
    MarketFacade --> FileGenerator
    DataManager --> Objects
    FileGenerator --> Generators
    Generators --> PriceListGenerator
    Generators --> SellerDataGenerator
    Generators --> StatisticDataGenerator
    Generators --> ReceiveInfoPdfGenerator
    Main --> Display
    Display --> ProgressBar
    Display --> Output
```
