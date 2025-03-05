from objects import FleatMarket
from .data_generator import DataGenerator
from objects import Article
from typing import List

class PriceListGenerator(DataGenerator):
    """
    A class to generate price lists for a flea market.
    
    Attributes:
    -----------
    FILE_SUFFIX : str
        The suffix for the output file.
    __fleat_market_data : FleatMarket
        The flea market data to generate the price list from.
    __output_data : List[str]
        The list to store the generated price list entries.
    """

    FILE_SUFFIX = 'dat'

    def __init__(self, fleat_market_data: FleatMarket, path: str = '', file_name: str = '') -> None:
        """
        Initializes the PriceListGenerator with flea market data, path, and file name.
        
        Parameters:
        -----------
        fleat_market_data : FleatMarket
            The flea market data to generate the price list from.
        path : str, optional
            The path to save the generated file (default is '').
        file_name : str, optional
            The name of the generated file (default is '').
        """
        DataGenerator.__init__(self, path, file_name)
        self.__fleat_market_data = fleat_market_data
        self.__output_data: List[str] = []

    def __create_entry(self, main_number: str, article_number: str, price: str) -> str:
        """
        Creates a formatted entry for the price list.
        
        Parameters:
        -----------
        main_number : str
            The main number of the article.
        article_number : str
            The article number.
        price : str
            The price of the article.
        
        Returns:
        --------
        str
            The formatted entry for the price list.
        """
        if int(article_number) < 10: 
            article_number = f'0{article_number}'

        return f'{main_number}{article_number},{price}\n'
    
    def __write(self):
        """
        Writes the generated price list to a file.
        """
        if self.__output_data:
            with open(self.path / f'{self.file_name}.{self.FILE_SUFFIX}', 'w') as file:
                file.writelines(self.__output_data)

    def generate(self):
        """
        Generates the price list from the flea market data.
        """
        for main_number in self.__fleat_market_data.get_main_number_data_list():
            if main_number.is_valid():
                for article in main_number.article_list:
                    if article.is_valid():
                        m_n = main_number.get_main_number()
                        a_n = article.number()
                        a_p = article.price()
                        entry = self.__create_entry(m_n, a_n, a_p)
                        self.__output_data.append(entry)
        
        self.__write()

