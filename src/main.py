# --- START OF FILE main.py (Revised) ---

import argparse
import sys
from typing import List, Optional  # Import List if BaseData returns typed lists

# Conditional import for CustomLogger
try:
    from log import CustomLogger
except ImportError:
    CustomLogger = None  # type: ignore
    # Define a dummy logger function if CustomLogger is not available
    # to prevent errors if logging calls remain somewhere unexpectedly.

    class DummyLogger:
        def info(self, *args, **kwargs): pass
        def warning(self, *args, **kwargs): pass
        def error(self, *args, **kwargs): pass
        def debug(self, *args, **kwargs): pass
        def set_level(self, *args, **kwargs): pass
    print("WARNUNG: logger.py nicht gefunden, Logging ist stark eingeschränkt oder deaktiviert.")

# Assume these imports work and classes are defined correctly
# Adjust paths/names if your structure is different
from data import BaseData, SellerDataClass, MainNumberDataClass  # Assuming these exist
from objects import FleatMarket
from generator import FileGenerator
from PySide6.QtWidgets import QApplication
# Assuming ui.py defines MainWindow correctly
try:
    from ui import MainWindow
except ImportError:
    MainWindow = None  # type: ignore
    print("WARNUNG: ui.py oder MainWindow nicht gefunden. GUI-Modus nicht verfügbar.")
# from PySide6.QtCore import Qt # Qt not used directly here


__major__ = 0
__minor__ = 4
__patch__ = 1
__version__ = f"{__major__}.{__minor__}.{__patch__}"


def Arguments():
    """Parses command line arguments."""
    prog_name = '%(prog)s'
    parser = argparse.ArgumentParser(prog=prog_name)

    parser.add_argument("-f", "--file", help="Path to JSON Data File", required=True)
    parser.add_argument("-p", "--path", help="Path to output folder", required=False, default='')
    parser.add_argument("-v", "--verbose", action='store_true', help="Enable detailed (DEBUG level) console output", required=False)
    parser.add_argument("-V", "--version", action='version', version=f"{prog_name} {__version__}")
    parser.add_argument('-l', '--log-level', choices=['INFO', 'WARNING', 'DEBUG', 'ERROR'], default='INFO',
        help='Set the minimum log level. Overridden by --verbose (sets DEBUG). '
            'Default: INFO.',required=False)
    # Add arguments for other file names if needed, e.g., PDF template path
    parser.add_argument('--pdf-template', default='Abholung_Template.pdf', required=False, help='Path to the PDF template file for receive confirmations.')
    parser.add_argument('--pdf-output', default='Abholung.pdf', required=False, help='Filename for the generated PDF receive confirmations.')
    # Add arguments for other output filenames if customization is desired
    
    parser.add_argument('--seller-filename', default='kundendaten', help='Filename (no ext) for seller data.')
    parser.add_argument('--price-filename', default='preisliste', help='Filename (no ext) for price list.')
    parser.add_argument('--stats-filename', default='versand', help='Filename (no ext) for statistics.')

    return parser.parse_args()


def run_cli():
    """Runs the application in Command Line Interface mode."""
    args = Arguments()
    output_path = args.path

    # Determine final log level (verbose overrides --log-level to DEBUG)
    log_level = 'DEBUG' if args.verbose else args.log_level
    verbose_mode = args.verbose

    # --- Instantiate CustomLogger ---
    cli_logger: Optional[CustomLogger] = None
    if CustomLogger:
        cli_logger = CustomLogger(
            name="FleaMarketCLI",
            log_level=log_level,
            verbose_enabled=verbose_mode  # Pass verbose flag if CustomLogger uses it directly
            # Optionally add a file handler here if needed
            # handler=logging.FileHandler('cli_run.log')
        )
        cli_logger.info(
            f"--- Starting Flea Market Generator v{__version__} (CLI Mode) ---")
        cli_logger.info(f"Log Level set to: {log_level}")
        if verbose_mode:
            cli_logger.info("Verbose mode enabled.")  # Log using the instance
    else:
        # Use the dummy logger if CustomLogger is not available
        cli_logger = DummyLogger()  # type: ignore
        print("INFO: --- Starting Flea Market Generator (CLI Mode, Logging Disabled) ---")

    # --- Data Loading ---
    # Assuming BaseData is updated to accept the logger instance
    try:
        cli_logger.info(f"Loading data from: {args.file}")  # type: ignore
        base_data = BaseData(args.file, cli_logger)  # Pass logger instance
        base_data.verify_data()  # Assuming this method uses the logger internally
        seller: List[SellerDataClass] = base_data.get_seller_list()
        main_numbers: List[MainNumberDataClass] = base_data.get_main_number_list()
        # type: ignore
        cli_logger.info("Data loaded and verified successfully.")
    except FileNotFoundError:
        # type: ignore
        cli_logger.error(f"Error: Data file not found at '{args.file}'")
        sys.exit(1)  # Exit if data file is crucial
    except Exception as e:
        # type: ignore
        cli_logger.error(f"Error during data loading or verification: {e}")
        # Optionally log traceback if logger is configured for it
        sys.exit(1)

    # --- Data Assembly ---
    fleat_market = FleatMarket()
    # Consider adding logging within FleatMarket methods if useful
    fleat_market.set_seller_data(seller)
    fleat_market.set_main_number_data(main_numbers)
    cli_logger.info("Flea market data object assembled.")  # type: ignore

    # --- File Generation ---
    # type: ignore
    cli_logger.info(
        f"Starting file generation into: '{output_path or Path.cwd()}'")
    try:
        file_generator = FileGenerator(
            fleat_market_data=fleat_market,
            output_path=output_path,
            # Pass filenames from args
            seller_file_name=args.seller_filename,
            price_list_file_name=args.price_filename,
            statistic_file_name=args.stats_filename,
            pdf_template_path_input=args.pdf_template,
            pdf_output_file_name=args.pdf_output,
            logger=cli_logger  # Pass the same logger instance
        )
        file_generator.generate()  # This will use the logger internally
        # type: ignore
        cli_logger.info("--- File generation process completed. ---")
    except Exception as e:
        # type: ignore
        cli_logger.error(f"FATAL ERROR during file generation: {e}")
        # Optionally log traceback
        sys.exit(1)


def run_ui():
    """Runs the application in Graphical User Interface mode."""
    if MainWindow is None:
        print("ERROR: Cannot run UI because MainWindow could not be imported.")
        sys.exit(1)
    if CustomLogger:
        # Create a logger instance specifically for the UI, if needed
        ui_logger = CustomLogger(name="FleaMarketUI", log_level="INFO")
        ui_logger.info(
            f"--- Starting Flea Market Generator v{__version__} (GUI Mode) ---")
        # Pass ui_logger to MainWindow if it accepts/needs it:
        # win = MainWindow(logger=ui_logger)
    else:
        ui_logger = None  # type: ignore
        print("INFO: --- Starting Flea Market Generator (GUI Mode, Logging Disabled) ---")

    # High DPI settings (consider making them optional or configurable)
    # QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    # QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    app = QApplication(sys.argv)

    win = MainWindow()  # If MainWindow needs logger: win = MainWindow(logger=ui_logger)
    win.setup_ui()  # Assuming setup_ui doesn't require arguments
    win.show()
    sys.exit(app.exec())


def main():
    """Determines run mode (CLI or UI) based on arguments."""
    # Check if any arguments other than the script name itself are provided
    # A more robust check could specifically look for known CLI flags.
    if len(sys.argv) > 1:
        run_cli()
    else:
        run_ui()


if __name__ == '__main__':
    main()

# --- END OF FILE main.py (Revised) ---
