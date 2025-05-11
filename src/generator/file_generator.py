from __future__ import annotations

"""Refactored :class:`FileGenerator`.

Core ideas
~~~~~~~~~~
* **Slim orchestration** – the heavy lifting is done by the concrete generator
  classes; *FileGenerator* merely wires them together.
* **Optional‑dependency friendly** – works even if logger / UI / tracker / bar
  are absent.
* **Unified helpers** (``_log``/``_echo``) mirror the rest of the refactored
  codebase.
"""

from pathlib import Path
import time
from typing import List, Optional, Sequence, Tuple, Protocol

try:
    from log import CustomLogger  # type: ignore
except ImportError:  # pragma: no cover
    CustomLogger = None  # type: ignore

try:
    from src.display import (
        OutputInterfaceAbstraction,                      # type: ignore
        ProgressTrackerAbstraction as _TrackerBase,      # type: ignore
    )
    from src.display.progress_bar.progress_bar_abstraction import (
        ProgressBarAbstraction as _BarBase,              # type: ignore
    )
except ImportError:  # pragma: no cover
    OutputInterfaceAbstraction = _TrackerBase = _BarBase = None  # type: ignore

# ---------------------------------------------------------------------------
# Flea‑market data placeholder (duck‑typed) – only stored & forwarded.
# ---------------------------------------------------------------------------
class _HasFM:  # noqa: D101 – minimal Protocol substitute
    pass

# Sub‑generators -----------------------------------------------------------
from .price_list_generator import PriceListGenerator
from .seller_data_generator import SellerDataGenerator
from .statistic_data_generator import StatisticDataGenerator
from .receive_info_pdf_generator import ReceiveInfoPdfGenerator

__all__ = ["FileGenerator"]


class FileGenerator:  # noqa: D101 – detailed docs above
    # ------------------------------------------------------------------
    # Construction helpers
    # ------------------------------------------------------------------
    def __init__(
        self,
        fleat_market_data: _HasFM,
        *,
        output_path: str | Path = "output",
        seller_file_name: str = "kundendaten",
        price_list_file_name: str = "preisliste",
        statistic_file_name: str = "versand",
        pdf_template_path_input: str | Path = "template/template.pdf",
        pdf_output_file_name: str | Path = "Abholbestaetigungen.pdf",
        logger: Optional[CustomLogger] = None,
        output_interface: Optional[OutputInterfaceAbstraction] = None,
        progress_tracker: Optional[_TrackerBase] = None,
        progress_bar: Optional[_BarBase] = None,
    ) -> None:
        
        # Housekeeping -------------------------------------------------
        self._fm = fleat_market_data
        self._path = Path(output_path)
        self._path.mkdir(parents=True, exist_ok=True)

        self._logger = logger
        self._ui = output_interface
        self._tracker = progress_tracker
        self._bar = progress_bar

        # Log basic environment info
        self._log("debug", f"Output path: {self._path.resolve()}")

        # Instantiate sub‑generators ----------------------------------
        common = dict(
            fleat_market_data=fleat_market_data,
            path=str(self._path),
            logger=logger,
            output_interface=output_interface,
        )
        self._tasks: List[Tuple[str, object]] = [
            ("Verkäuferdaten", SellerDataGenerator(**common, file_name=seller_file_name)),
            ("Preisliste",     PriceListGenerator(**common, file_name=price_list_file_name)),
            ("Statistik",      StatisticDataGenerator(**common, file_name=statistic_file_name)),
            (
                "Abholbestätigung",
                ReceiveInfoPdfGenerator(
                    **common,
                    pdf_template_path_input=pdf_template_path_input,
                    pdf_template_path_output=pdf_output_file_name,
                ),
            ),
        ]

        if self._tracker and hasattr(self._tracker, "reset"):
            self._tracker.reset(total=len(self._tasks))  # type: ignore[misc]

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    # Logging + UI ------------------------------------------------------
    def _log(self, level: str, msg: str) -> None:  # noqa: D401
        if self._logger:
            fn = getattr(self._logger, level, None)
            if callable(fn):
                fn(msg)
            else:
                self._logger.info(msg)

    def _echo(self, msg: str) -> None:  # noqa: D401
        if self._ui:
            try:
                self._ui.write_message(msg)
            except Exception:  # pragma: no cover
                pass

    def _output(self, level: str, msg: str) -> None:  # noqa: D401
        self._log(level, msg)
        if level.upper() in {"INFO", "WARNING", "ERROR", "CRITICAL"}:
            self._echo(msg)

    # Progress bar helper ----------------------------------------------
    def _update_bar(self):  # noqa: D401
        if not (self._tracker and self._bar):
            return
        try:
            st = self._tracker.get_state()  # type: ignore[attr-defined]
            self._bar.update(
                st.get("percentage", 0), st.get("current"), st.get("total"), st.get("error")
            )
        except Exception:  # pragma: no cover
            pass

    # ------------------------------------------------------------------
    # Public entry point
    # ------------------------------------------------------------------
    def generate(self) -> None:  # noqa: D401
        self._output("INFO", "Starte Dateigenerierung …")
        start = time.time()
        success = True

        for name, gen in self._tasks:
            self._output("INFO", f"→ {name} …")
            step_ok = True
            try:
                gen.generate(overall_tracker=self._tracker)
            except Exception as err:  # pragma: no cover
                self._output("ERROR", f"Fehler in Schritt '{name}': {err}")
                step_ok = success = False
                if self._tracker and hasattr(self._tracker, "set_error"):
                    self._tracker.set_error(err)  # type: ignore[misc]
            finally:
                if self._tracker and hasattr(self._tracker, "increment"):
                    self._tracker.increment()  # type: ignore[misc]
                self._update_bar()
            self._output(
                "INFO" if step_ok else "ERROR",
                f"← {name} {'ok' if step_ok else 'fehlgeschlagen'}"
            )

        # Final wrap‑up --------------------------------------------------
        dur = time.time() - start
        if success:
            self._output("INFO", f"Alle Aufgaben abgeschlossen in {dur:.2f}s.")
            if self._bar:
                self._bar.complete(success=True)  # type: ignore[misc]
        else:
            self._output("ERROR", f"Generierung mit Fehlern beendet ({dur:.2f}s).")
            if self._bar:
                self._bar.complete(success=False)  # type: ignore[misc]
