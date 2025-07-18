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
from objects import CoordinatesConfig

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
        pdf_coordinates: Optional[List[CoordinatesConfig]] = None,
        logger: Optional[CustomLogger] = None,
        output_interface: Optional[OutputInterfaceAbstraction] = None,
        progress_tracker: Optional[_TrackerBase] = None,
        progress_bar: Optional[_BarBase] = None,
    ) -> None:
        
        # Housekeeping -------------------------------------------------
        Base.__init__(self, logger, output_interface)
        self._fm = fleat_market_data
        self._path = Path(output_path)
        self._tracker = progress_tracker
        self._bar = progress_bar

        # Parameter für spätere Initialisierung merken
        self._seller_file_name = seller_file_name
        self._price_list_file_name = price_list_file_name
        self._statistic_file_name = statistic_file_name
        self._pdf_template_path_input = pdf_template_path_input
        self._pdf_output_file_name = pdf_output_file_name
        self._pdf_coordinates = pdf_coordinates

        self._tasks: List[Tuple[str, object]] = []

    def _ensure_output_folder(self) -> None:
        """Erstellt den Output-Ordner falls nötig und loggt den Pfad."""
        self._path.mkdir(parents=True, exist_ok=True)
        self._log("debug", f"Output path: {self._path.resolve()}")

    def _build_tasks(self) -> List[Tuple[str, object]]:
        """Erzeuge die Liste aller Sub‑Generatoren."""
        common = dict(fleat_market_data=self._fm, path=str(self._path))
        return [
            ("Verkäuferdaten", SellerDataGenerator(**common, file_name=self._seller_file_name)),
            ("Preisliste", PriceListGenerator(**common, file_name=self._price_list_file_name)),
            ("Statistik", StatisticDataGenerator(**common, file_name=self._statistic_file_name)),
            (
                "Abholbestätigung",
                ReceiveInfoPdfGenerator(
                    **common,
                    pdf_template=self._pdf_template_path_input,
                    output_name=self._pdf_output_file_name,
                    coordinates=self._pdf_coordinates,
                ),
            ),
        ]

    def _init_tasks(self) -> None:
        """Initialisiert die Sub-Generatoren-Tasks."""
        self._tasks = self._build_tasks()
        if self._tracker and hasattr(self._tracker, "reset"):
            self._tracker.reset(total=len(self._tasks)*2)  # type: ignore[misc]

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

    def _run_tasks(self, tasks: List[Tuple[str, object]], headline: str) -> None:
        """Execute the given tasks with progress tracking."""
        self._ensure_output_folder()
        if self._tracker and hasattr(self._tracker, "reset"):
            self._tracker.reset(total=len(tasks) * 2)  # type: ignore[misc]

        self._output("INFO", headline)
        start = time.time()
        success = True

        for name, task in tasks:
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

        duration = time.time() - start
        if success:
            self._output("INFO", f"Alle Aufgaben abgeschlossen in {duration:.2f}s.")
            if self._bar:
                self._bar.complete(success=True)  # type: ignore[misc]
        else:
            self._output("ERROR", f"Generierung mit Fehlern beendet ({duration:.2f}s).")
            if self._bar:
                self._bar.complete(success=False)  # type: ignore[misc]

    # ------------------------------------------------------------------
    # Public entry point
    # ------------------------------------------------------------------
    def generate(self) -> None:  # noqa: D401
        self._init_tasks()
        self._run_tasks(self._tasks, "Starte Dateigenerierung …")

    def set_output_folder_path(self, path: str | Path) -> None:
        """Setzt den Pfad zum Output-Ordner."""
        self._path = Path(path)

    def get_output_folder_path(self) -> Path:
        """Gibt den Pfad zum Output-Ordner zurück."""
        return self._path

    # ------------------------------------------------------------------
    # Public helpers for partial generation
    # ------------------------------------------------------------------
    def _apply_pdf_settings(self, settings: Optional[dict]) -> None:
        """Update internal paths based on ``settings`` dictionary."""
        if not settings:
            return
        out = settings.get("output_path") or settings.get("pdf_path")
        if out:
            self._path = Path(out)
        template = settings.get("pdf_template") or settings.get("pdf_template_path_input")
        if template:
            self._pdf_template_path_input = template
        output = settings.get("pdf_output") or settings.get("pdf_output_file_name") or settings.get("pdf_name")
        if output:
            self._pdf_output_file_name = output
        coords = settings.get("coordinates") or settings.get("pdf_coordinates")
        if coords:
            self._pdf_coordinates = coords

    def create_pdf_data(self, settings: Optional[dict] = None) -> None:
        """Generate only the PDF based on ``settings``."""
        #self._apply_pdf_settings(settings)
        tasks = [self._build_tasks()[-1]]  # only PDF task
        self._run_tasks(tasks, "Starte PDF‑Generierung …")

    def create_seller_data(self) -> None:
        """Generate seller related data files (DAT)."""
        tasks = self._build_tasks()[:-1]
        self._run_tasks(tasks, "Starte Dateigenerierung …")

    def create_all(self, settings: Optional[dict] = None) -> None:
        """Generate all data and PDF files."""
        self._apply_pdf_settings(settings)
        tasks = self._build_tasks()
        self._run_tasks(tasks, "Starte Dateigenerierung …")
