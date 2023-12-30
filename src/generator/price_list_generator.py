from objects import FleatMarket
from .data_generator import DataGenerator
from objects import Article
from typing import List

class PriceListGenerator(DataGenerator):
    
    FILE_SUFFIX = 'dat'

    def __init__(self, fleat_market_data: FleatMarket, path: str = '', file_name: str = '') -> None:
        DataGenerator.__init__(self,path, file_name)
        self.__fleat_market_data = fleat_market_data
        self.__output_data: List[str] = []


    def __create_entry(self, main_number: str, article_number: str, price: str) -> str:
        if int(article_number) < 10: 
            article_number = f'0{article_number}'

        return f'{main_number}{article_number},{price}\n'
    
    def __write(self):
        if self.__output_data:
            with open(self.path / f'{self.file_name}.{self.FILE_SUFFIX}', 'w') as file:
                file.writelines(self.__output_data)

    def generate(self):
        for main_number in self.__fleat_market_data.get_main_number_data_list():
            if main_number.is_valid():
                for article in main_number.article_list:
                    if article.is_valid():
                        m_n = main_number.get_main_number()
                        a_n = article.number()
                        a_p = article.price()
                        entry = self.__create_entry(m_n,a_n,a_p)
                        self.__output_data.append(entry)
        
        self.__write()

