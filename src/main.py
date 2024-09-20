import argparse
from data import *
from objects import FleatMarket
from generator import FileGenerator
from log import logger
import time
__major__ = 0
__minor__ = 4
__patch__ = 0

__version__ = f"{__major__}.{__minor__}.{__patch__}"


def Arguments(): 
    global __version__
    name = '%(prog)s'
    parser = argparse.ArgumentParser()
    
    parser.add_argument("-f", "--file",help="Path to JSON File", required=True)
    parser.add_argument("-p", "--path", help="Path to output folder", required=False, default='')
    parser.add_argument("-v", "--verbose", action='store_true', help="Enable detailed console output", required=False)
    parser.add_argument("-V", "--version", action='version', version=f"{name} {__version__}")
    parser.add_argument('-l', '--log-level', choices=['INFO', 'WARNING', 'DEBUG', 'ERROR'],
                                             default='INFO',
                                             help='Set the desired log level. Possible values: INFO, WARNING, DEBUG, ERROR. Default: INFO.',
                                             required= False
                                             )

    return parser.parse_args()



if __name__ == '__main__':

    args = Arguments()
    output_path = args.path

    verbose = args.verbose
    level = args.log_level
    
    logger.setup(level,verbose)
    if verbose:
       logger.info("Verbose Enabled")


    base_data: BaseData = BaseData(args.file, logger)
    base_data.verify_data()
    seller: List[SellerDataClass] = base_data.get_seller_list()
    main_numbers: List[MainNumberDataClass] = base_data.get_main_number_list()


    fleat_market = FleatMarket()
    fleat_market.set_seller_data(seller)
    fleat_market.set_main_number_data(main_numbers)
    
    file_generator = FileGenerator(fleat_market,output_path,'kundendaten','preise', 'Abholung_Template.pdf', 'Abholung.pdf')
    file_generator.generate()   