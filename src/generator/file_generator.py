from __future__ import annotations



from pathlib import Path
import time
from typing import List, Optional, Sequence, Tuple, Protocol
from log import CustomLogger  # type: ignore
from display import (
    OutputInterfaceAbstraction,                      # type: ignore
    ProgressTrackerAbstraction as _TrackerBase,      # type: ignore
)
from display.progress_bar.progress_bar_abstraction import (
    ProgressBarAbstraction as _BarBase,              # type: ignore
)

# Sub‑generators -----------------------------------------------------------
from data import Base
from .price_list_generator import PriceListGenerator
from .seller_data_generator import SellerDataGenerator
from .statistic_data_generator import StatisticDataGenerator
from .receive_info_pdf_generator import ReceiveInfoPdfGenerator

__all__ = ["FileGenerator"]


class FileGenerator(Base):  # noqa: D101 – detailed docs above
    # ------------------------------------------------------------------
    # Construction helpers
    # ------------------------------------------------------------------
    def __init__(
        self,
        fleat_market_data ,  # type: ignore[valid-type]
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
        
        Base.__init__(logger, output_interface)
        self._fm = fleat_market_data
        self._path = Path(output_path)
        self._path.mkdir(parents=True, exist_ok=True)

        self._tracker = progress_tracker
        self._bar = progress_bar

        # Log basic environment info
        self._log("debug", f"Output path: {self._path.resolve()}")

        # Instantiate sub‑generators ----------------------------------
        common = dict(fleat_market_data=fleat_market_data,path=str(self._path))

        self._tasks: List[Tuple[str, object]] = [
            ("Verkäuferdaten", SellerDataGenerator(**common, file_name=seller_file_name)),
            ("Preisliste",     PriceListGenerator(**common, file_name=price_list_file_name)),
            ("Statistik",      StatisticDataGenerator(**common, file_name=statistic_file_name)),
            ("Abholbestätigung", ReceiveInfoPdfGenerator(**common, pdf_template = pdf_template_path_input)),
        ]

        if self._tracker and hasattr(self._tracker, "reset"):
            #self._tracker.reset(total=len(self._tasks))  # type: ignore[misc]
            self._tracker.reset(total=6)  # type: ignore[misc]

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    # Logging + UI ------------------------------------------------------

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

        for name, task in self._tasks:
            self._output("INFO", f"→ {name} …")
            step_ok = True
            try:
                task.generate(overall_tracker=self._tracker)
            except Exception as err:  # pragma: no cover
                self._output("ERROR", f"Fehler in Schritt '{name}': {err}")
                step_ok = success = False
                if self._tracker and hasattr(self._tracker, "set_error"):
                    self._tracker.set_error(err)  # type: ignore[misc]
            finally:
                if self._tracker and hasattr(self._tracker, "increment"):
                    self._tracker.increment()  # type: ignore[misc]
                self._update_bar()
            self._output("INFO" if step_ok else "ERROR", f"← {name} {'ok' if step_ok else 'fehlgeschlagen'}")

        # Final wrap‑up --------------------------------------------------
        duration = time.time() - start
        if success:
            self._output("INFO", f"Alle Aufgaben abgeschlossen in {duration:.2f}s.")
            if self._bar:
                self._bar.complete(success=True)  # type: ignore[misc]
        else:
            self._output("ERROR", f"Generierung mit Fehlern beendet ({duration:.2f}s).")
            if self._bar:
                self._bar.complete(success=False)  # type: ignore[misc]
