from objects import FleatMarket
from .data_generator import DataGenerator
from typing import List, Tuple
from log import logger
import time

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
        
        logger.info("Erstelle Verkäuferliste:" +
                    "      ========================")
        time.sleep(2)
        
        for index, main_number_data in enumerate(self.__fleat_market_data.get_main_number_data_list()):
            main_number =  main_number_data.get_main_number()
            first_name = self.__fleat_market_data.get_seller_data(index).vorname
            second_name = self.__fleat_market_data.get_seller_data(index).nachname
            logger.log_one_line("INFO",True)
            if main_number_data.is_valid():

                m_n = main_number_data.get_main_number()
                a_q = main_number_data.get_article_quantity()
                a_t = main_number_data.get_article_total()
                entry = self.__create_entry(m_n,a_q,a_t)
                self.__output_data.append(entry)
                valid_cnt +=1
                logger.info(f">> Erstelle Eintrag <<\n" +
                            f"      {first_name}, {second_name}:\n" + 
                            f"           >> Stammnummer: {main_number}\n" +
                            f"           >> Anzahl Artikel: {a_q}\n" + 
                            f"           >> Gesamt Summe: {a_t}€\n"+
                            f"           >> Status: OK <<\n\n")
            else: 
                invalid_cnt +=1
                m_n = main_number_data.get_main_number()
                a_q = main_number_data.get_article_quantity()
                a_t = main_number_data.get_article_total()

                a_q_f = " - Fehler" if a_q == 0 else ""
                a_t_f = " - Fehler" if a_t == 0 else ""
                logger.info(f">> Erstelle Eintrag <<\n" +
                            f"      {first_name}, {second_name}:\n" + 
                            f"           >> Stammnummer: {main_number}\n" +
                            f"           >> Anzahl Artikel: {a_q}{a_q_f}\n" + 
                            f"           >> Gesamt Summe: {a_t}€{a_t_f}\n"+
                            f"           >> Status: FEHLER <<\n\n")
            logger.log_one_line("INFO",False)
            time.sleep(0.2)
        
        time.sleep(1)
        self.__write()
        logger.info(f"Verkäufer liste erstellt: \n"+
                     "      ========================\n" +
                    f"          --> Anzahl Einträge: {valid_cnt}\n" + 
                    f"          --> Anzahl ungültiger Einträge: {invalid_cnt}\n\n")
        time.sleep(2)
    
