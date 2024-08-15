from pathlib import Path
from objects import FleatMarket
from .price_list_generator import PriceListGenerator
from .seller_data_generator import SellerDataGenerator
from .statistic_data_generator import StatisticDataGenerator
from log import logger

class FileGenerator:

    def __init__(self, fleat_market_data: FleatMarket, output_path: str = '', seller_file_name: str = "", price_list_file_name: str = "" ) -> None:
        self.__seller_generator = SellerDataGenerator(fleat_market_data,output_path, seller_file_name)
        self.__price_list_generator = PriceListGenerator(fleat_market_data, output_path, price_list_file_name)
        self.__statistic_generator = StatisticDataGenerator(fleat_market_data, output_path)
        self.verify_output_path(Path(output_path))

    def generate(self):
        self.__seller_generator.generate()
        self.__price_list_generator.generate()
        self.__statistic_generator.generate()

        
        logger.info(">> Daten wurden erfolgreich erstellt: <<\n\n\n")

    def verify_output_path(self, path: Path):
        path.mkdir(parents=True, exist_ok=True)

    def set_seller_file_name(self): 
        pass

    def set_price_list_file_name(self):
        pass