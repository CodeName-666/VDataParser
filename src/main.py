# --- START OF FILE main.py (Revised for Interfaces) ---
import sys
from typing import List, Optional
from pathlib import Path # Import Path for clarity
from args import Arguments # Import Arguments class for command line argument parsing
from version import get_version

# --- Conditional Imports ---
# Logger
try:
    from log import CustomLogger
except ImportError:
    CustomLogger = None  # type: ignore
    class DummyLogger: # Basic fallback if logging is essential but lib missing
        def info(self, *args, **kwargs): print("INFO:", *args)
        def warning(self, *args, **kwargs): print("WARN:", *args)
        def error(self, *args, **kwargs): print("ERROR:", *args)
        def debug(self, *args, **kwargs): pass # Usually ignore debug if no logger
        def set_level(self, *args, **kwargs): pass
        def exception(self, *args, **kwargs): print("EXCEPTION:", *args)
    print("WARNUNG: log.py nicht gefunden, Logging ist stark eingeschränkt.")

# Data Handling (Assume these are correct)
try:
    from data import BaseData, SellerDataClass, MainNumberDataClass
except ImportError as e:
     print(f"FEHLER: Konnte Datenklassen nicht importieren: {e}")
     # Define dummies if absolutely necessary for script parsing, but exit is better
     # class BaseData: ...
     sys.exit(1)

# Core Logic
try:
    from objects import FleatMarket
except ImportError:
    print("FEHLER: Konnte 'objects.FleatMarket' nicht importieren.")
    sys.exit(1)
try:
    from generator import FileGenerator
    # Import necessary interfaces and classes for CLI mode
    from display import ProgressTrackerAbstraction # Interface needed? Not directly here.
    from display import BasicProgressTracker # Implementation needed? Not directly here.
    from display import ConsoleProgressBar # Needed? No, FileGenerator handles it.
    from display import OutputInterfaceAbstraction, ConsoleOutput # Needed for CLI
except ImportError as e:
    print(f"FEHLER: Konnte Generator-Komponenten nicht importieren: {e}")
    # Define dummies if parsing required, but exit is likely needed
    FileGenerator = None # type: ignore
    OutputInterfaceAbstraction = None # type: ignore
    ConsoleOutput = None # type: ignore
    # ProgressTrackerInterface = None # type: ignore
    # BasicProgressTracker = None # type: ignore
    # ConsoleProgressBar = None # type: ignore

# UI Components
try:
    from PySide6.QtWidgets import QApplication
    from ui import MainWindow
except ImportError:
    QApplication = None # type: ignore
    MainWindow = None  # type: ignore
    print("WARNUNG: PySide6 oder ui.py nicht gefunden. GUI-Modus nicht verfügbar.")


def run_cli():
    """Runs the application in Command Line Interface mode."""
    if FileGenerator is None:
        print("FEHLER: FileGenerator konnte nicht geladen werden. CLI-Modus nicht verfügbar.")
        sys.exit(1)

    args = Arguments()
    output_path = args.path

    # --- Setup Logging ---
    log_level = 'DEBUG' if args.verbose else args.log_level
    verbose_mode = args.verbose
    cli_logger: Optional[CustomLogger] = None # Use the imported type or fallback
    if CustomLogger:
        cli_logger = CustomLogger(
            name="FleaMarketCLI",
            log_level=log_level,
            verbose_enabled=verbose_mode
            # file_handler=logging.FileHandler('cli.log') # Optional file logging
        )
    else:
        cli_logger = DummyLogger() # Use dummy if CustomLogger failed

    # --- Setup Output Interface (for user messages) ---
    output_iface: Optional[OutputInterfaceAbstraction] = None
    if ConsoleOutput:
        output_iface = ConsoleOutput()
        # Use output interface for initial user message
        output_iface.write_message(f"--- Starting Flea Market Generator v{get_version()} (CLI Mode) ---")
    else:
        # Fallback to print if interface unavailable
        print("INFO: --- Starting Flea Market Generator (CLI Mode, Output Interface Disabled) ---")
        print("WARNUNG: ConsoleOutput nicht gefunden. Benutzermeldungen nur über Standard-Print/Logging.")

    if cli_logger: # Log configuration details via logger
       cli_logger.info(f"Flea Market Generator v{get_version()} (CLI Mode)")
       cli_logger.info(f"Log Level set to: {log_level}")
       if verbose_mode: cli_logger.info("Verbose mode enabled.")

    # --- Data Loading ---
    if cli_logger: cli_logger.info(f"Loading data from: {args.file}")
    try:
        # Pass logger to BaseData (assuming it accepts it)
        base_data = BaseData(args.file, logger=cli_logger) # Pass logger instance
        base_data.verify_data() # Assuming this method uses the logger internally
        seller: List[SellerDataClass] = base_data.get_seller_list()
        main_numbers: List[MainNumberDataClass] = base_data.get_main_number_list()
        if cli_logger: cli_logger.info("Data loaded and verified successfully.")
    except FileNotFoundError:
        err_msg = f"Error: Data file not found at '{args.file}'"
        if cli_logger: cli_logger.error(err_msg)
        if output_iface: output_iface.write_message(err_msg)
        else: print(err_msg)
        sys.exit(1)
    except Exception as e:
        err_msg = f"Error during data loading or verification: {e}"
        if cli_logger: cli_logger.exception(err_msg) # Use exception for traceback
        if output_iface: output_iface.write_message(err_msg)
        else: print(err_msg)
        sys.exit(1)

    # --- Data Assembly ---
    fleat_market = FleatMarket()
    # Consider adding logging within FleatMarket methods if useful
    fleat_market.set_seller_data(seller)
    fleat_market.set_main_number_data(main_numbers)
    if cli_logger: cli_logger.info("Flea market data object assembled.")

    # --- File Generation ---
    start_msg = f"Starting file generation into: '{output_path or Path.cwd()}'"
    if cli_logger: cli_logger.info(start_msg)
    if output_iface: output_iface.write_message(start_msg)

    try:
        # Instantiate FileGenerator, passing both logger and output interface
        file_generator = FileGenerator(
            fleat_market_data=fleat_market,
            output_path=output_path,
            seller_file_name=args.seller_filename,
            price_list_file_name=args.price_filename,
            statistic_file_name=args.stats_filename,
            pdf_template_path_input=args.pdf_template,
            pdf_output_file_name=args.pdf_output,
            logger=cli_logger,           # Pass the logger instance
            output_interface=output_iface # Pass the output interface instance
        )
        # The generate method now uses its internal progress bar and the passed
        # logger/output_interface for its messages. No need for run_with_progress here.
        file_generator.generate()

        # Final success message
        success_msg = "--- File generation process completed successfully. ---"
        if cli_logger: cli_logger.info(success_msg)
        if output_iface: output_iface.write_message(success_msg)
        else: print(success_msg) # Fallback

    except Exception as e:
        # Log fatal error with traceback
        err_msg = f"FATAL ERROR during file generation process: {e}"
        if cli_logger: cli_logger.exception(err_msg) # Logger gets traceback
        # Show error to user via output interface or print
        if output_iface: output_iface.write_message(err_msg)
        else: print(err_msg) # Fallback print
        sys.exit(1)


def run_ui():
    """Runs the application in Graphical User Interface mode."""
    if MainWindow is None or QApplication is None:
        print("ERROR: Cannot run UI because MainWindow or QApplication could not be imported.")
        sys.exit(1)

    # UI-specific logger (optional)
    ui_logger: Optional[CustomLogger] = None
    if CustomLogger:
        ui_logger = CustomLogger(name="FleaMarketUI", log_level="INFO") # Separate logger for UI?
        ui_logger.info(f"--- Starting Flea Market Generator v{__version__} (GUI Mode) ---")
    else:
        print("INFO: --- Starting Flea Market Generator (GUI Mode, Logging Disabled) ---")

    # High DPI settings can remain if needed
    # QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    # QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    app = QApplication(sys.argv)

    # IMPORTANT: MainWindow needs to be adapted internally!
    # It will likely need to:
    # 1. Create its own instances of BaseData, FleatMarket, FileGenerator.
    # 2. Potentially create its own BasicProgressTracker or a Qt-specific one.
    # 3. Pass the tracker and logger/output (if MainWindow handles output) to FileGenerator.
    # 4. Connect signals from the tracker/generator (if implemented) to UI elements (like QProgressBar).
    # 5. The current main.py doesn't pass any data *to* the MainWindow constructor here.
    win = MainWindow() # Assuming MainWindow's __init__ doesn't need logger/data yet
                       # OR: Adapt MainWindow to accept logger: win = MainWindow(logger=ui_logger)
    win.setup_ui()
    win.show()
    sys.exit(app.exec())


def main():
    """Determines run mode (CLI or UI) based on arguments."""
    # Simple check: If any arguments beyond the script name exist, assume CLI.
    # A more robust check might look for specific required flags like '-f'.
    is_cli_mode = False
    if len(sys.argv) > 1:
        # Check if known CLI flags are present, e.g., '-f' or '--file'
        # This avoids accidentally triggering CLI mode for unrelated args Qt might add.
        known_cli_args = ['-f', '--file', '-p', '--path', '-v', '--verbose', '-V', '--version', '-l', '--log-level']
        if any(arg in sys.argv for arg in known_cli_args):
            is_cli_mode = True
        elif sys.argv[1] in ['-h', '--help']: # Handle help explicitly for CLI
             is_cli_mode = True

    if is_cli_mode:
        run_cli()
    else:
        run_ui()


if __name__ == '__main__':
    main()

# --- END OF FILE main.py (Revised for Interfaces) ---