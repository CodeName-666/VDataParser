from objects import FleatMarket
from .data_generator import DataGenerator
from typing import List, Tuple
from log import logger


class SellerDataGenerator(DataGenerator):

    FILE_SUFFIX = 'dat'

    def __init__(self, fleat_market_data: FleatMarket, path: str = '', file_name: str = 'kundendaten') -> None:
        DataGenerator.__init__(self, path, file_name)
        self.__fleat_market_data: FleatMarket = fleat_market_data
        self.__output_data: List[str] = []
    
    def __create_entry(self, main_number:int, article_quantity:int, article_total_count:int) -> str:
        return f'"{main_number}","B",{article_quantity},{article_total_count}\n'
    
    def __write(self):
        if self.__output_data:
            with open(self.path / f'{self.file_name}.{self.FILE_SUFFIX}', 'w') as file:
                file.writelines(self.__output_data)

    def generate(self):
        valid_cnt = 0 
        invalid_cnt = 0
        logger.info("Generate seller data:")
        logger.info("")
        
        for index, main_number_data in enumerate(self.__fleat_market_data.get_main_number_data_list()):
            main_number =  main_number_data.get_main_number()
            first_name = self.__fleat_market_data.get_seller_data(index).vorname
            second_name = self.__fleat_market_data.get_seller_data(index).nachname
            logger.info(f"{index}: Generate Main Number: {main_number} - {first_name}, {second_name}")
            if main_number_data.is_valid():

                m_n = main_number_data.get_main_number()
                a_q = main_number_data.get_article_quantity()
                a_t = main_number_data.get_article_total()
                entry = self.__create_entry(m_n,a_q,a_t)
                self.__output_data.append(entry)
                valid_cnt +=1
            else: 
                invalid_cnt +=1
                logger.warning("--> Main number invalid")
        logger.info(f"Seller data generated: {valid_cnt}, Seller data skipped: {invalid_cnt}")
        self.__write()
    
