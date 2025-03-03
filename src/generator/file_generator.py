from pathlib import Path
from objects import FleatMarket
from .price_list_generator import PriceListGenerator
from .seller_data_generator import SellerDataGenerator
from .statistic_data_generator import StatisticDataGenerator
from .receive_info_pdf_generator import ReceiveInfoPdfGenerator
from log import logger

class FileGenerator:
    """
    A class to generate various files for a flea market.
    
    Attributes:
    -----------
    __seller_generator : SellerDataGenerator
        The generator for seller data.
    __price_list_generator : PriceListGenerator
        The generator for price lists.
    __statistic_generator : StatisticDataGenerator
        The generator for statistics.
    __receive_info_pdf_generator : ReceiveInfoPdfGenerator
        The generator for receive info PDFs.
    """

    def __init__(self, fleat_market_data: FleatMarket, output_path: str = '', seller_file_name: str = "", price_list_file_name: str = "", pdf_template_path_input: str = '', pdf_template_path_output: str = '') -> None:
        """
        Initializes the FileGenerator with flea market data and various file paths and names.
        
        Parameters:
        -----------
        fleat_market_data : FleatMarket
            The flea market data to generate the files from.
        output_path : str, optional
            The path to save the generated files (default is '').
        seller_file_name : str, optional
            The name of the generated seller file (default is '').
        price_list_file_name : str, optional
            The name of the generated price list file (default is '').
        pdf_template_path_input : str, optional
            The input path for the PDF template (default is '').
        pdf_template_path_output : str, optional
            The output path for the generated PDF (default is '').
        """
        self.__seller_generator = SellerDataGenerator(fleat_market_data, output_path, seller_file_name)
        self.__price_list_generator = PriceListGenerator(fleat_market_data, output_path, price_list_file_name)
        self.__statistic_generator = StatisticDataGenerator(fleat_market_data, output_path)
        self.__receive_info_pdf_generator = ReceiveInfoPdfGenerator(fleat_market_data, output_path, pdf_template_path_input, pdf_template_path_output)
        self.verify_output_path(Path(output_path))

    def generate(self):
        """
        Generates all the necessary files for the flea market.
        """
        self.__seller_generator.generate()
        self.__price_list_generator.generate()
        self.__statistic_generator.generate()
        logger.info(">> Daten wurden erfolgreich erstellt: <<\n\n")
        self.__receive_info_pdf_generator.generate()

    def verify_output_path(self, path: Path):
        """
        Verifies and creates the output path if it does not exist.
        
        Parameters:
        -----------
        path : Path
            The path to verify and create.
        """
        path.mkdir(parents=True, exist_ok=True)

    def set_seller_file_name(self): 
        """
        Sets the seller file name.
        """
        pass

    def set_price_list_file_name(self):
        """
        Sets the price list file name.
        """
        pass