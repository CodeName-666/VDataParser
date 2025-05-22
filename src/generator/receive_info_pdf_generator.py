from __future__ import annotations

from pathlib import Path
from dataclasses import dataclass
from typing import List, Optional, Sequence, Tuple, Protocol
import io

from log import CustomLogger  

from display import (
    ProgressTrackerAbstraction as _TrackerBase,  
    ConsoleProgressBar as _ConsoleBar,          
    OutputInterfaceAbstraction,                 
)

from pypdf import PdfReader, PdfWriter, PageObject  
from reportlab.pdfgen import canvas 
from reportlab.lib.pagesizes import letter, landscape 
from reportlab.lib.units import mm  
from reportlab.lib import colors  
from .data_generator import DataGenerator
from display import BasicProgressTracker as ProgressTracker

@dataclass
class CoordinatesConfig:
    x1: float
    y1: float
    x2: float
    y2: float
    x3: float
    y3: float
    font_size: int = 12


# ---------------------------------------------------------------------------
# Progress stub (if toolkit missing) ----------------------------------------
# ---------------------------------------------------------------------------
class _NoOpTracker:  # noqa: D101
    def __init__(self):
        self.has_error = False

    # noqa: D401 – tiny helper class
    def reset(self, total: int): ...  # pragma: no cover
    def increment(self): ...  # pragma: no cover

    def set_error(self, exc: Exception):
        self.has_error = True


# ---------------------------------------------------------------------------
# Main class
# ---------------------------------------------------------------------------
class ReceiveInfoPdfGenerator(DataGenerator):  # noqa: D101 – see module docstring
    DEFAULT_COORDS = [
        CoordinatesConfig(20 * mm, -30 * mm, 80 * mm, -30 * mm, 140 * mm, -30 * mm),
        CoordinatesConfig(160 * mm, -30 * mm, 220 * mm, -30 * mm, 280 * mm, -30 * mm),
        CoordinatesConfig(20 * mm, -130 * mm, 80 * mm, -130 * mm, 140 * mm, -130 * mm),
        CoordinatesConfig(160 * mm, -130 * mm, 220 * mm, -130 * mm, 280 * mm, -130 * mm),
    ] if mm else []  # empty if reportlab absent

    # ------------------------------------------------------------------
    def __init__(
        self,
        fleat_market_data,
        *,
        path: str | Path = "",
        pdf_template: str | Path = "",
        output_name: str | Path = "abholbestaetigung.pdf",
        coordinates: Optional[List[CoordinatesConfig]] = None,
        logger: Optional[CustomLogger] = None,
        output_interface: Optional[OutputInterfaceAbstraction] = None,
    ) -> None:
        opath = Path(output_name)
        super().__init__(path, opath.stem, logger, output_interface)

        self._fm = fleat_market_data
        self._template_path = Path(pdf_template) if pdf_template else None
        self._coords: List[CoordinatesConfig] = coordinates or self.DEFAULT_COORDS
        if not self._coords:
            raise ValueError(
                "Es wurden keine Koordinaten definiert und ReportLab ist nicht verfügbar.")

        self._entries_per_page = len(self._coords)
        self._output_pdf = (self.path / opath).with_suffix(".pdf")

    # ------------------------------------------------------------------
    # Data collection helpers
    # ------------------------------------------------------------------
    def _seller_rows(self) -> List[Tuple[str, str, str]]:  # noqa: D401
        rows: list[Tuple[str, str, str]] = []
        for idx, mn in enumerate(self._fm.main_numbers()):
            if not getattr(mn, "is_valid", lambda: False)():
                continue
            try:
                num = str(int(mn.number()))
            except Exception:
                continue  # silently skip invalid numbers
            try:
                seller = self._fm.seller_at(idx)
                name = f"{getattr(seller, 'nachname', 'Unbekannt')}, {getattr(seller, 'vorname', 'Unbekannt')}"
            except Exception:
                name = "Unbekannt, Unbekannt"
            rows.append((name, num, ""))
        return rows

    # ------------------------------------------------------------------
    # Template loading / overlay helpers
    # ------------------------------------------------------------------
    def _template_bytes(self) -> Optional[bytes]:  # noqa: D401
        if not self._template_path or not self._template_path.is_file():
            self._output_and_log("ERROR", "Template PDF nicht gefunden.")
            return None
        try:
            return self._template_path.read_bytes()
        except Exception as err:  # pragma: no cover
            self._output_and_log(
                "ERROR", f"Fehler beim Lesen des Templates: {err}")
            return None

    def _overlay_page(self, rows: Sequence[Tuple[str, str, str]]):  # noqa: D401
        if canvas is None:
            return None  # reportlab missing
        packet = io.BytesIO()
        page_w, page_h = landscape(letter)  # type: ignore[arg-type]
        can = canvas.Canvas(packet, pagesize=(
            page_w, page_h))  # type: ignore[arg-type]
        can.setFillColor(colors.black)  # type: ignore[arg-type]
        for idx, (f1, f2, f3) in enumerate(rows):
            cfg = self._coords[idx]
            can.setFont("Helvetica-Bold", cfg.font_size)
            can.drawString(cfg.x1, cfg.y1, f1)
            can.drawString(cfg.x2, cfg.y2, f2)
            can.drawString(cfg.x3, cfg.y3, f3)
        can.save()
        packet.seek(0)
        return PdfReader(packet).pages[0]  # type: ignore[return-value]

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------
    def _write_pdf(self, writer: "PdfWriter") -> bool:  # noqa: D401
        try:
            self._output_pdf.parent.mkdir(parents=True, exist_ok=True)
            with self._output_pdf.open("wb") as fh:
                writer.write(fh)
            self._output_and_log(
                "INFO", f"PDF geschrieben: {self._output_pdf.relative_to(Path.cwd())}")
            return True
        except Exception as err:  # pragma: no cover
            self._output_and_log(
                "ERROR", f"Fehler beim Schreiben der PDF: {err}")
            return False

    # ------------------------------------------------------------------
    # Public orchestration
    # ------------------------------------------------------------------
    def generate(self, overall_tracker: Optional[_TrackerBase] = None) -> None:  # noqa: D401
        # 0. Dependency check ------------------------------------------------
        if PdfReader is object or canvas is None:
            self._output_and_log("ERROR", "PDF‑Libraries fehlen – Abbruch.")
            if overall_tracker:
                overall_tracker.increment()  # type: ignore[attr-defined]
                # type: ignore[attr-defined]
                overall_tracker.set_error(ImportError("pypdf/reportlab fehlt"))
            return

        self._output_and_log("INFO", "Starte PDF‑Generierung …")
        rows = self._seller_rows()
        if not rows:
            self._output_and_log(
                "INFO", "Keine gültigen Daten – nichts zu tun.")
            if overall_tracker:
                overall_tracker.increment()  # type: ignore[attr-defined]
            return

        template = self._template_bytes()
        if template is None:
            if overall_tracker:
                overall_tracker.increment()
                # type: ignore[attr-defined]
                overall_tracker.set_error(FileNotFoundError())
            return

        # 1. Progress helper -------------------------------------------------
        #tracker = _NoOpTracker() if _TrackerBase is None else _TrackerBase()
        tracker = ProgressTracker()
        total_pages = (len(rows) + self._entries_per_page -
                       1) // self._entries_per_page
        if hasattr(tracker, "reset"):
            tracker.reset(total=total_pages)  # type: ignore[misc]

        bar = _ConsoleBar(
            length=50, description="PDF") if _ConsoleBar else None

        def _task():
            writer = PdfWriter()
            for i in range(0, len(rows), self._entries_per_page):
                grp = rows[i: i + self._entries_per_page]
                try:
                    base = PdfReader(io.BytesIO(template)).pages[0]
                    ovl = self._overlay_page(grp)
                    if ovl:
                        base.merge_page(ovl)
                    writer.add_page(base)
                    if hasattr(tracker, "increment"):
                        tracker.increment()  # type: ignore[misc]
                except Exception as err:  # pragma: no cover
                    tracker.set_error(err)
                    break
            if not tracker.has_error:
                self._write_pdf(writer)

        # 2. Run with optional console bar ----------------------------------
        if bar:
            # type: ignore[arg-type]
            bar.run_with_progress(target=_task, args=(), tracker=tracker)
        else:
            _task()

        # 3. Final state -----------------------------------------------------
        if tracker.has_error:
            self._output_and_log(
                "ERROR", "PDF‑Erstellung fehlgeschlagen – siehe Log.")
            if overall_tracker:
                # type: ignore[attr-defined]
                overall_tracker.set_error(RuntimeError("PDF error"))
        else:
            self._output_and_log("INFO", "PDF‑Erstellung abgeschlossen.")

        if overall_tracker:
            overall_tracker.increment()  # type: ignore[attr-defined]
