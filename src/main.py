import argparse
from data import *
from objects import FleatMarket
from generator import FileGenerator
from log import logger
import sys
from PySide6.QtWidgets import QApplication
from ui import MainWindow
from PySide6.QtCore import Qt




__major__ = 0
__minor__ = 4
__patch__ = 1

__version__ = f"{__major__}.{__minor__}.{__patch__}"


def Arguments():
    global __version__
    name = '%(prog)s'
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-f", "--file", help="Path to JSON File", required=True)
    parser.add_argument(
        "-p", "--path", help="Path to output folder", required=False, default='')
    parser.add_argument("-v", "--verbose", action='store_true',
                        help="Enable detailed console output", required=False)
    parser.add_argument("-V", "--version", action='version',
                        version=f"{name} {__version__}")
    parser.add_argument('-l', '--log-level', choices=['INFO', 'WARNING', 'DEBUG', 'ERROR'],
                        default='INFO',
                        help='Set the desired log level. Possible values: INFO, WARNING, DEBUG, ERROR. Default: INFO.',
                        required=False)
    return parser.parse_args()


def run_cli():
    args = Arguments()
    output_path = args.path

    verbose = args.verbose
    level = args.log_level

    logger.setup(level, verbose)
    if verbose:
        logger.info("Verbose Enabled")

    base_data: BaseData = BaseData(args.file, logger)
    base_data.verify_data()
    seller: List[SellerDataClass] = base_data.get_seller_list()
    main_numbers: List[MainNumberDataClass] = base_data.get_main_number_list()

    fleat_market = FleatMarket()
    fleat_market.set_seller_data(seller)
    fleat_market.set_main_number_data(main_numbers)

    file_generator = FileGenerator(
        fleat_market, output_path, 'kundendaten', 'preise', 'Abholung_Template.pdf', 'Abholung.pdf')
    file_generator.generate()


def run_ui():
    
    #QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    #QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    app = QApplication(sys.argv)
   
    win = MainWindow()
    win.setup_ui()
    win.show()
    sys.exit(app.exec())    


def main():
    # If arguments are provided, run the original command-line code
    if len(sys.argv) > 1:
        run_cli()        
    # If no arguments are provided, launch the PySide6 GUI
    else:
        run_ui()

if __name__ == '__main__':
    main()
