# --- START OF FILE main.py (Revised for Injected Progress) ---
import sys
import logging  # Standard logging for fallback
from typing import List, Optional
from pathlib import Path  # Import Path for clarity
from args import Arguments  # Import Arguments class for command line argument parsing
from version import get_version

# --- Conditional Imports ---
# Logger
try:
    from log import CustomLogger
except ImportError:
    CustomLogger = None  # type: ignore

    class DummyLogger:  # Basic fallback if logging is essential but lib missing
        def info(self, *args, **kwargs): print("INFO:", *args)
        def warning(self, *args, **kwargs): print("WARN:", *args)
        def error(self, *args, **kwargs): print("ERROR:", *args)
        # Usually ignore debug if no logger
        def debug(self, *args, **kwargs): pass
        def set_level(self, *args, **kwargs): pass
        def exception(self, *args, **kwargs): print("EXCEPTION:", *args)
    print("WARNUNG: log.py nicht gefunden, Logging ist stark eingeschränkt.")

# Data Handling (Assume these are correct)
try:
    from data import BaseData, SellerDataClass, MainNumberDataClass
except ImportError as e:
    print(f"FEHLER: Konnte Datenklassen nicht importieren: {e}")
    sys.exit(1)

# Core Logic & Display Components
try:
    from objects import FleatMarket
except ImportError:
    print("FEHLER: Konnte 'objects.FleatMarket' nicht importieren.")
    sys.exit(1)
try:
    from generator import FileGenerator
    # Import necessary interfaces and classes for CLI mode
    # Interface needed? Not directly here.
    from display import ProgressTrackerAbstraction
    # Implementation needed? Not directly here.
    from display import ProgressBarAbstraction
    from display import BasicProgressTracker
    from display import ConsoleProgressBar
    from display import OutputInterfaceAbstraction, ConsoleOutput  # Needed for CLI
except ImportError as e:
    print(
        f"FEHLER: Konnte Generator- oder Display-Komponenten nicht importieren: {e}")
    # Define dummies if parsing required, but exit is likely needed
    FileGenerator = None  # type: ignore
    ProgressTrackerAbstraction = None  # type: ignore
    # type: ignore # Was BasicProgressTracker? Renamed? Use the actual name.
    ProgressTracker = None
    ProgressBarAbstraction = None  # type: ignore
    ConsoleProgressBar = None  # type: ignore
    OutputInterfaceAbstraction = None  # type: ignore
    ConsoleOutput = None  # type: ignore
    print("FEHLER: Fortfahren nicht möglich aufgrund fehlender Kernkomponenten.")
    sys.exit(1)  # Exit if core components are missing

# UI Components
try:
    from PySide6.QtWidgets import QApplication
    from ui import MainWindow
    # Import Qt Progress Bar *only if needed here* or handled within MainWindow
    # from src.display.progress_bar.qt_progress_bar import QtProgressBar
except ImportError:
    QApplication = None  # type: ignore
    MainWindow = None  # type: ignore
    # QtProgressBar = None # type: ignore
    print("WARNUNG: PySide6 oder ui.py nicht gefunden. GUI-Modus nicht verfügbar.")


def run_cli():
    """Runs the application in Command Line Interface mode."""
    if FileGenerator is None:
        print(
            "FEHLER: FileGenerator konnte nicht geladen werden. CLI-Modus nicht verfügbar.")
        sys.exit(1)

    args = Arguments()
    output_path = args.path

    file_handler = logging.FileHandler('cli_logging', mode='w', encoding='utf-8')

    # --- Setup Logging ---
    log_level = 'DEBUG' if args.verbose else args.log_level
    verbose_mode = args.verbose
    # Use the imported type or fallback
    cli_logger: Optional[CustomLogger] = None
    if CustomLogger:
        cli_logger = CustomLogger(
            name="FleaMarketCLI",
            log_level=log_level,
            verbose_enabled=verbose_mode,
            handler=file_handler,  # Pass the file handler
        )
        cli_logger.info(
            f"--- Starting Flea Market Generator v{get_version()} (CLI Mode) ---")
        cli_logger.info(f"Log Level set to: {log_level}")
        if verbose_mode:
            cli_logger.info("Verbose mode enabled.")
    else:
        cli_logger = DummyLogger()  # Use dummy if CustomLogger failed
        cli_logger.info(
            f"--- Starting Flea Market Generator v{get_version()} (CLI Mode - Logging limited) ---")

    # --- Setup Output Interface (for user messages) ---
    output_iface: Optional[OutputInterfaceAbstraction] = None
    if ConsoleOutput:
        output_iface = ConsoleOutput()
    else:
        # Fallback to print if interface unavailable (Logger already warned)
        print("WARNUNG: ConsoleOutput nicht gefunden. Benutzermeldungen nur über Standard-Print/Logging.")

    # --- Setup Progress Tracking and Display (for CLI) ---
    cli_tracker: Optional[ProgressTrackerAbstraction] = None
    cli_progress_bar: Optional[ProgressBarAbstraction] = None

    if BasicProgressTracker:  # Check if the *concrete* tracker class was imported
        cli_tracker = BasicProgressTracker()  # Instantiate the tracker
        # No total needed here, FileGenerator will reset it
        if cli_logger:
            cli_logger.debug("Progress Tracker initialized.")
    else:
        if cli_logger:
            cli_logger.warning(
                "Progress Tracker implementation not found. Progress tracking disabled.")

    if ConsoleProgressBar and cli_tracker:  # Need tracker for the bar to be useful
        # Instantiate the console progress bar, potentially passing the logger
        cli_progress_bar = ConsoleProgressBar(
            length=60,  # Or get from config/args if needed
            description="Gesamtfortschritt",
            logger=cli_logger  # Pass logger to the bar itself if it uses it
        )
        if cli_logger:
            cli_logger.debug("Console Progress Bar initialized.")
    elif ConsoleProgressBar:
        if cli_logger:
            cli_logger.warning(
                "Console Progress Bar found, but no tracker. Progress bar disabled.")
    else:
        if cli_logger:
            cli_logger.warning(
                "Console Progress Bar implementation not found. Progress display disabled.")

    # --- Data Loading ---
    if cli_logger:
        cli_logger.info(f"Loading data from: {args.file}")
    try:
        # Pass logger to BaseData
        base_data = BaseData(args.file, logger=cli_logger)
        base_data.verify_data()
        seller: List[SellerDataClass] = base_data.get_seller_list()
        main_numbers: List[MainNumberDataClass] = base_data.get_main_number_list()
        if cli_logger:
            cli_logger.info("Data loaded and verified successfully.")
    except FileNotFoundError:
        err_msg = f"FEHLER: Datendatei nicht gefunden unter '{args.file}'"
        if cli_logger:
            cli_logger.error(err_msg)
        if output_iface:
            output_iface.write_message(err_msg)
        else:
            print(err_msg)
        sys.exit(1)
    except Exception as e:
        err_msg = f"FEHLER beim Laden oder Verifizieren der Daten: {e}"
        if cli_logger:
            cli_logger.exception(err_msg)
        if output_iface:
            output_iface.write_message(err_msg)
        else:
            print(err_msg)
        sys.exit(1)

    # --- Data Assembly ---
    fleat_market = FleatMarket()
    fleat_market.set_seller_data(seller)
    fleat_market.set_main_number_data(main_numbers)
    if cli_logger:
        cli_logger.info("Flea market data object assembled.")

    # --- File Generation ---
    start_msg = f"Starte Dateigenerierung nach: '{output_path or Path.cwd()}'"
    if cli_logger:
        cli_logger.info(start_msg)
    if output_iface:
        output_iface.write_message(start_msg)

    try:
        # Instantiate FileGenerator, injecting ALL dependencies
        file_generator = FileGenerator(
            fleat_market_data=fleat_market,
            output_path=output_path,
            seller_file_name=args.seller_filename,
            price_list_file_name=args.price_filename,
            statistic_file_name=args.stats_filename,
            pdf_template_path_input=args.pdf_template,
            pdf_output_file_name=args.pdf_output,
            logger=cli_logger,              # Pass the logger
            output_interface=output_iface,  # Pass the output interface
            # Pass the tracker instance (or None)
            progress_tracker=cli_tracker,
            # Pass the progress bar instance (or None)
            progress_bar=cli_progress_bar
        )

        # Call generate. FileGenerator now internally uses the provided
        # tracker and bar to display progress for its steps.
        file_generator.generate()

        # Final success message
        success_msg = "--- Dateigenerierung erfolgreich abgeschlossen. ---"
        # Check generator status? Maybe not needed if generate raises exceptions on failure
        # For now, assume completion means success if no exception occurred.
        # Final status is logged/output by FileGenerator itself.
        # if cli_logger: cli_logger.info(success_msg) # Redundant? FileGenerator logs completion.
        # if output_iface: output_iface.write_message(success_msg) # Redundant?

    except Exception as e:
        # Log fatal error with traceback
        err_msg = f"FATALER FEHLER während der Dateigenerierung: {e}"
        # FileGenerator should have logged/outputted step-specific errors.
        # This catches errors *outside* the generate loop or if generate itself fails catastrophically.
        if cli_logger:
            cli_logger.exception(err_msg)
        if output_iface:
            output_iface.write_message(err_msg)
        else:
            print(err_msg)
        sys.exit(1)


def run_ui():
    """Runs the application in Graphical User Interface mode."""
    if MainWindow is None or QApplication is None:
        print("FEHLER: Kann UI nicht starten, da MainWindow oder QApplication nicht importiert werden konnte.")
        sys.exit(1)

    # UI-specific logger (optional but good practice)
    ui_logger: Optional[CustomLogger] = None
    if CustomLogger:
        # Consider a different log file or configuration for the UI
        ui_logger = CustomLogger(name="FleaMarketUI", log_level="INFO")
        ui_logger.info(
            f"--- Starting Flea Market Generator v{get_version()} (GUI Mode) ---")
    else:
        print("INFO: --- Starting Flea Market Generator (GUI Mode, Logging Disabled) ---")

    app = QApplication(sys.argv)

    # --- IMPORTANT ---
    # The MainWindow class now needs to handle the creation of:
    # 1. Its own logger (or receive one).
    # 2. Its own output interface (e.g., writing to a QPlainTextEdit).
    # 3. Its own ProgressTracker instance.
    # 4. Its own ProgressBarAbstraction instance (e.g., QtProgressBar).
    # 5. It will then pass these instances when it creates its FileGenerator instance.
    # This logic moves *inside* the MainWindow class.
    # We might pass the logger here for consistency.
    # Adapt MainWindow constructor if needed
    win = MainWindow(logger=ui_logger)
    win.setup_ui()  # Assuming setup_ui or methods called from it handle instantiation
    win.show()
    sys.exit(app.exec())


def main():
    """Determines run mode (CLI or UI) based on arguments."""
    # Simple check: If any arguments beyond the script name exist, assume CLI.
    # Check for explicit CLI flags or help request.
    is_cli_mode = False
    if len(sys.argv) > 1:
        known_cli_args = ['-f', '--file', '-p', '--path', '-v', '--verbose',
                          '-V', '--version', '-l', '--log-level', '-h', '--help',
                          '--seller-filename', '--price-filename', '--stats-filename',
                          '--pdf-template', '--pdf-output']  # Add other CLI args
        # Check if *any* known CLI argument or -h/--help is present
        if any(arg in sys.argv for arg in known_cli_args):
            is_cli_mode = True

    # Special check for version argument to run CLI logic
    if '--version' in sys.argv or '-V' in sys.argv:
        print(f"Flea Market Generator Version: {get_version()}")
        sys.exit(0)  # Exit after showing version

    # Check for help argument (needs to be handled *before* full CLI run potentially)
    if '-h' in sys.argv or '--help' in sys.argv:
        # Assuming Arguments class handles printing help and exiting
        args = Arguments()  # This will print help and exit if -h is present
        # If Arguments doesn't exit, force exit here
        sys.exit(0)

    if is_cli_mode:
        run_cli()
    elif MainWindow is not None and QApplication is not None:  # Check if UI components loaded
        run_ui()
    else:
        print("FEHLER: CLI-Argumente nicht erkannt und UI-Komponenten nicht verfügbar.")
        print("Führen Sie das Skript mit '-h' für Hilfe zu CLI-Optionen aus oder stellen Sie sicher, dass PySide6 installiert ist.")
        sys.exit(1)


if __name__ == '__main__':
    main()

# --- END OF FILE main.py (Revised for Injected Progress) ---
