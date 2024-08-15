from objects import FleatMarket
from .data_generator import DataGenerator
from typing import List, Tuple
from log import logger


class StatisticDataGenerator(DataGenerator):

    FILE_SUFFIX = 'dat'

    def __init__(self, fleat_market_data: FleatMarket, path: str = '', file_name: str = 'versand') -> None:
        DataGenerator.__init__(self, path, file_name)
        self.__fleat_market_data: FleatMarket = fleat_market_data
        self.__output_data: List[str] = []
    
    def __create_entry(self, main_number:int) -> str:
        return f'{main_number},"-"\n'
    
    def __write(self):
        if self.__output_data:
            with open(self.path / f'{self.file_name}.{self.FILE_SUFFIX}', 'w') as file:
                file.writelines(self.__output_data)

    def generate(self):
        valid_cnt = 0 
        invalid_cnt = 0
        logger.info("Generiere Statistic Daten:\n" +
                    "========================")
        
        
        for _, main_number_data in enumerate(self.__fleat_market_data.get_main_number_data_list()):
            main_number =  main_number_data.get_main_number()
          
            entry = self.__create_entry(main_number)
            self.__output_data.append(entry)
            valid_cnt +=1
        else: 
            invalid_cnt +=1
            
        self.__write()
        logger.info("   >> Daten erstellt:")
    
