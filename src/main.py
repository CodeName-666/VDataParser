from __future__ import annotations

from pathlib import Path
import sys
import logging
from typing import List, Tuple, Optional, Any

from args import Arguments
from version import get_version

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _optional(name: str, attr: str | None = None) -> Any | None:  # noqa: D401
    """Attempt ``import name`` (optionally ``from name import attr``)."""
    try:
        mod = __import__(name, fromlist=[attr] if attr else [])
        return getattr(mod, attr) if attr else mod
    except ImportError as err:  # pragma: no cover – optional dep
        logging.getLogger("FleaMarket").debug("Optionale Abhängigkeit fehlt: %s", err)
        return None


def _bootstrap_logger(verbose: bool, level: str) -> logging.Logger:  # noqa: D401
    try:
        CustomLogger = _optional("log", "CustomLogger")  # type: ignore[var‑annotated]
        if CustomLogger is not None:
            return CustomLogger(
                name="FleaMarket",
                level="DEBUG" if verbose else level,
                verbose=verbose,
                handler=logging.FileHandler("cli_logging", "w", "utf‑8"),
            )
    except Exception:  # pragma: no cover – fallback safety
        pass

    logging.basicConfig(
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        level=logging.DEBUG if verbose else getattr(logging, level.upper(), logging.INFO),
        handlers=[
            logging.FileHandler("cli_logging", "w", "utf‑8"),
            logging.StreamHandler(sys.stdout),
        ],
    )
    return logging.getLogger("FleaMarket")


# ---------------------------------------------------------------------------
# Dynamic imports (may be None)
# ---------------------------------------------------------------------------
BaseData = _optional("data", "BaseData")
SellerDataClass = _optional("data", "SellerDataClass")
MainNumberDataClass = _optional("data", "MainNumberDataClass")

FleatMarket = _optional("objects", "FleatMarket")
FileGenerator = _optional("generator", "FileGenerator")
ProgressTracker = _optional("display", "BasicProgressTracker")
ConsoleBar = _optional("display", "ConsoleProgressBar")
OutputIface = _optional("display", "ConsoleOutput")

QApplication = _optional("PySide6.QtWidgets", "QApplication")
MainWindow = _optional("ui", "MainWindow")


# ---------------------------------------------------------------------------
# Infrastructure builders
# ---------------------------------------------------------------------------

def _build_cli_infra(logger: logging.Logger):  # noqa: D401
    out = OutputIface() if OutputIface else None
    tracker = ProgressTracker() if ProgressTracker else None
    bar = ConsoleBar(  # type: ignore[call‑arg]
        length=60, description="Gesamtfortschritt", logger=logger
    ) if ConsoleBar and tracker else None
    return out, tracker, bar


# ---------------------------------------------------------------------------
# CLI Flow
# ---------------------------------------------------------------------------

def _run_cli(parsed: Arguments):  # noqa: D401
    logger = _bootstrap_logger(parsed.verbose, parsed.log_level)
    logger.info(f"Flea Market Generator v{get_version()} – CLI")

    if any(d is None for d in (FileGenerator, BaseData, FleatMarket)):
        logger.critical("Erforderliche Module fehlen – Installation prüfen.")
        sys.exit(1)

    out, tracker, bar = _build_cli_infra(logger)

    data_file = Path(parsed.file).expanduser()
    logger.info(f"Lade Daten …{data_file}")

    try:
        base = BaseData(data_file, logger=logger)  # type: ignore[arg‑type]
        base.verify_data()
        sellers: List[SellerDataClass] = base.get_seller_list()  # type: ignore[assignment]
        main_numbers: List[MainNumberDataClass] = base.get_main_number_list()  # type: ignore[assignment]
    except FileNotFoundError:
        (out or logger).error("Datendatei nicht gefunden: %s", data_file)  # type: ignore[attr‑defined]
        sys.exit(1)
    except Exception as err:
        logger.error(f"Fehler beim Laden der Daten: {err}")
        sys.exit(1)

    fm = FleatMarket(logger = logger, output_interface = out)  # type: ignore[call‑arg]
    fm.load_sellers(sellers)
    fm.load_main_numbers(main_numbers)

    gen = FileGenerator(  # type: ignore[call‑arg]
        fleat_market_data=fm,
        output_path=Path(parsed.path or Path.cwd()).expanduser(),
        seller_file_name=parsed.seller_filename,
        price_list_file_name=parsed.price_filename,
        statistic_file_name=parsed.stats_filename,
        pdf_template_path_input=parsed.pdf_template,
        pdf_output_file_name=parsed.pdf_output,
        logger=logger,
        output_interface=out,
        progress_tracker=tracker,
        progress_bar=bar,
    )

    try:
        gen.generate()
    except Exception:
        logger.exception("Fataler Fehler bei der Dateigenerierung")
        sys.exit(1)

    logger.info("Dateigenerierung abgeschlossen.")


# ---------------------------------------------------------------------------
# GUI Flow
# ---------------------------------------------------------------------------

def _run_gui():  # noqa: D401
    if not (QApplication and MainWindow):  # pragma: no cover – env without GUI
        print("GUI‑Abhängigkeiten fehlen. Bitte PySide6 installieren.")
        sys.exit(1)

    logger = _bootstrap_logger(verbose=False, level="INFO")
    logger.info("Flea Market Generator v%s – GUI", get_version())

    app = QApplication(sys.argv)
    win = MainWindow(logger=logger)  # type: ignore[call‑arg]
    win.setup_ui()
    win.show()
    sys.exit(app.exec())


# ---------------------------------------------------------------------------
# Entrypoint dispatcher
# ---------------------------------------------------------------------------

def main():  # noqa: D401
    """Decide between CLI and GUI based on argv."""
    try:
        parsed = Arguments()
    except SystemExit as exc:
        # *Arguments* exited due to -h / --help etc.
        if exc.code == 0:
            return
        # If a flag was present but parsing failed → re‑raise.
        raise
    else:
        # If at least one primary CLI arg (file/path) supplied → CLI mode.
        if parsed.file or parsed.path:
            _run_cli(parsed)
        else:
            _run_gui()


if __name__ == "__main__":
    main()
