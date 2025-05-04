# --- START OF FILE main.py (Improved) ---
from __future__ import annotations

import sys
import logging
from pathlib import Path
from typing import List, Optional

from args import Arguments
from version import get_version

################################################################################
# Bootstrap utilities
################################################################################

def _bootstrap_logger(verbose: bool, level: str) -> logging.Logger:
    """
    Returns a ``logging.Logger`` instance.  If a custom implementation is
    available (``log.CustomLogger``) it will be preferred, otherwise stdlib
    logging is configured as a reasonable fallback.
    """
    try:
        from log import CustomLogger  # pylint: disable=import-error
        return CustomLogger(
            name="FleaMarket",
            log_level="DEBUG" if verbose else level,
            verbose_enabled=verbose,
            handler=logging.FileHandler("cli_logging", mode="w", encoding="utf‑8"),
        )
    except ImportError:
        # Fallback – configure stdlib logging once and return a dedicated logger
        logging.basicConfig(
            format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            level=logging.DEBUG if verbose else getattr(logging, level.upper(), logging.INFO),
            handlers=[logging.FileHandler("cli_logging", mode="w", encoding="utf‑8"), logging.StreamHandler(sys.stdout)],
        )
        return logging.getLogger("FleaMarket")


################################################################################
# Optional imports with graceful degradation
################################################################################

def _optional_import(name: str, attr: str | None = None):
    """
    Tries to import *name* (or *attr* from *name*) and returns ``None`` if it
    cannot be imported.
    """
    try:
        module = __import__(name, fromlist=[attr] if attr else [])
        return getattr(module, attr) if attr else module
    except ImportError as exc:
        logging.getLogger("FleaMarket").debug("Optional dependency '%s' missing: %s", name, exc)
        return None


# Data handling
BaseData               = _optional_import("data", "BaseData")
SellerDataClass        = _optional_import("data", "SellerDataClass")
MainNumberDataClass    = _optional_import("data", "MainNumberDataClass")

# Core logic & display
FleaMarket             = _optional_import("objects", "FleatMarket")  # noqa: N816 – keep external name
FileGenerator          = _optional_import("generator", "FileGenerator")
ProgressTrackerClass   = _optional_import("display", "BasicProgressTracker")
ConsoleProgressBar     = _optional_import("display", "ConsoleProgressBar")
OutputInterface        = _optional_import("display", "ConsoleOutput")

# Qt UI
QApplication           = _optional_import("PySide6.QtWidgets", "QApplication")
MainWindow             = _optional_import("src/ui", "MainWindow")

################################################################################
# CLI helpers
################################################################################


def _build_cli_infra(args: Arguments, logger: logging.Logger):
    """
    Returns fully initialised helper objects needed by ``run_cli``:
    ``(output_iface, tracker, progress_bar)``.
    """
    output_iface = OutputInterface() if OutputInterface else None

    tracker = ProgressTrackerClass() if ProgressTrackerClass else None

    progress_bar = (
        ConsoleProgressBar(
            length=60,
            description="Gesamtfortschritt",
            logger=logger,
        )
        if ConsoleProgressBar and tracker
        else None
    )

    return output_iface, tracker, progress_bar


################################################################################
# Modes
################################################################################


def run_cli() -> None:
    """Entry‑point for command‑line mode."""
    args = Arguments()

    logger = _bootstrap_logger(verbose=args.verbose, level=args.log_level)
    logger.info("Flea Market Generator v%s − CLI mode", get_version())

    if FileGenerator is None:
        logger.critical("Required module 'generator.FileGenerator' is not available.")
        sys.exit(1)

    if BaseData is None:
        logger.critical("Required data handling modules missing.")
        sys.exit(1)

    output_iface, tracker, progress_bar = _build_cli_infra(args, logger)

    # --------------------------------------------------------------------- data
    data_file = Path(args.file).expanduser()
    logger.info("Loading data: %s", data_file)

    try:
        base_data = BaseData(data_file, logger=logger)  # type: ignore[operator]
        base_data.verify_data()
        seller: List[SellerDataClass] = base_data.get_seller_list()       # type: ignore[assignment]
        main_numbers: List[MainNumberDataClass] = base_data.get_main_number_list()  # type: ignore[assignment]
    except FileNotFoundError:
        msg = f"Datendatei nicht gefunden: '{data_file}'"
        (output_iface or logger).error(msg)  # type: ignore[attr-defined]
        sys.exit(1)
    except Exception as exc:  # noqa: BLE001
        logger.error("Fehler beim Laden/Verifizieren der Daten: %s", exc)
        sys.exit(1)

    logger.info("Data verified successfully.")

    # ------------------------------------------------------------------ assemble
    flea_market = FleaMarket()  # type: ignore[call-arg]
    flea_market.set_seller_data(seller)
    flea_market.set_main_number_data(main_numbers)

    # ------------------------------------------------------------------- generate
    output_path = Path(args.path or Path.cwd()).expanduser()
    logger.info("Generating files into: %s", output_path)

    generator = FileGenerator(  # type: ignore[call-arg]
        fleat_market_data=flea_market,
        output_path=output_path,
        seller_file_name=args.seller_filename,
        price_list_file_name=args.price_filename,
        statistic_file_name=args.stats_filename,
        pdf_template_path_input=args.pdf_template,
        pdf_output_file_name=args.pdf_output,
        logger=logger,
        output_interface=output_iface,
        progress_tracker=tracker,
        progress_bar=progress_bar,
    )

    try:
        generator.generate()
    except Exception:  # noqa: BLE001
        logger.exception("Fataler Fehler während der Dateigenerierung")
        sys.exit(1)

    logger.info("Dateigenerierung erfolgreich abgeschlossen.")


def run_ui() -> None:
    """Entry‑point for GUI mode."""
    if QApplication is None or MainWindow is None:
        print("FEHLER: GUI‑Abhängigkeiten fehlen. Installieren Sie PySide6.")
        sys.exit(1)

    logger = _bootstrap_logger(verbose=False, level="INFO")
    logger.info("Flea Market Generator v%s − GUI mode", get_version())

    app = QApplication(sys.argv)
    win = MainWindow(logger=logger)
    win.setup_ui()
    win.show()
    sys.exit(app.exec())


################################################################################
# Main
################################################################################


def main() -> None:  # noqa: C901 – keep in single function for clarity
    """
    Dispatch either CLI or GUI execution.

    CLI mode is assumed if at least one known CLI argument is present.  The
    ``Arguments`` class is responsible for printing its own ``--help`` and
    ``--version`` output.
    """
    cli_flags = {
        "-f", "--file", "-p", "--path", "-v", "--verbose", "--seller-filename",
        "--price-filename", "--stats-filename", "--pdf-template",
        "--pdf-output", "-l", "--log-level",
    }

    if any(flag in sys.argv for flag in cli_flags):
        run_cli()
        return

    if "-h" in sys.argv or "--help" in sys.argv:
        Arguments()  # will print and exit
        return

    if "-V" in sys.argv or "--version" in sys.argv:
        print(get_version())
        return

    # Default to GUI
    if QApplication and MainWindow:
        run_ui()
    else:
        print("FEHLER: Keine GUI‑Unterstützung verfügbar und keine CLI‑Argumente erkannt.")
        print("Verwenden Sie '-h' für Hilfe.")
        sys.exit(1)


if __name__ == "__main__":
    main()
# --- END OF FILE main.py (Improved) ---
