from __future__ import annotations

"""PDF generator for receive confirmations."""

from pathlib import Path
from typing import List, Optional, Sequence, Tuple
import io

from log import CustomLogger

from display import (
    ProgressTrackerAbstraction,
    OutputInterfaceAbstraction,
    ConsoleProgressBar,
)

try:
    from display import ProgressBarAbstraction
except Exception:  # pragma: no cover - optional dependency
    ProgressBarAbstraction = None  # type: ignore

from pypdf import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
try:
    from reportlab.pdfbase import pdfmetrics
except Exception:  # pragma: no cover - optional dependency
    pdfmetrics = None  # type: ignore
from utils.font_utils import register_font

from reportlab.lib.units import mm
from reportlab.lib import colors
from .data_generator import DataGenerator
from objects import CoordinatesConfig
from display import BasicProgressTracker as ProgressTracker


# ---------------------------------------------------------------------------
# Main class
# ---------------------------------------------------------------------------
class ReceiveInfoPdfGenerator(DataGenerator):  # noqa: D101 – see module docstring
    """Generate PDFs with seller receive confirmations."""

    DEFAULT_COORDS = (
        [
            CoordinatesConfig(35 * mm, 173 * mm, 115 * mm, 173 * mm, 30 * mm, 150 * mm),
            CoordinatesConfig(
                178 * mm, 173 * mm, 258 * mm, 173 * mm, 173 * mm, 150 * mm
            ),
            CoordinatesConfig(35 * mm, 83 * mm, 115 * mm, 83 * mm, 30 * mm, 60 * mm),
            CoordinatesConfig(178 * mm, 83 * mm, 258 * mm, 83 * mm, 173 * mm, 60 * mm),
        ]
        if mm
        else []
    )  # empty if reportlab absent

    DEFAULT_DISPLAY_DPI = 150  # DPI used in PdfDisplay when coordinates were captured

    DEFAULT_FONT_NAME = "Helvetica-Bold"

    @staticmethod
    def _draw_centered(can, x: float, y: float, text: str, font_name: str, font_size: int) -> None:
        """Draw ``text`` centred at ``(x, y)`` using ``font_name`` and ``font_size``."""
        width = 0
        if pdfmetrics is not None:
            try:
                width = pdfmetrics.stringWidth(text, font_name, font_size)
            except Exception:
                width = 0
        can.drawString(x - width / 2, y, text)

    # ------------------------------------------------------------------
    @staticmethod
    def _from_display_coords(
        cfg: CoordinatesConfig,
        page_h: float,
        *,
        dpi: int = DEFAULT_DISPLAY_DPI,
    ) -> CoordinatesConfig:
        """Convert GUI coordinates (origin top-left, in ``dpi``) to PDF points."""

        scale = 72 / dpi
        return CoordinatesConfig(
            x1=cfg.x1 * scale,
            y1=page_h - cfg.y1 * scale,
            x2=cfg.x2 * scale,
            y2=page_h - cfg.y2 * scale,
            x3=cfg.x3 * scale,
            y3=page_h - cfg.y3 * scale,
            font_size=cfg.font_size,
        )

    # ------------------------------------------------------------------
    def __init__(
        self,
        fleat_market_data,
        *,
        path: str | Path = "",
        pdf_template: str | Path = "",
        output_name: str | Path = "abholbestaetigung.pdf",
        coordinates: Optional[List[CoordinatesConfig]] = None,
        display_dpi: int = DEFAULT_DISPLAY_DPI,
        pickup_date: str = "",
        font_name: str = DEFAULT_FONT_NAME,
        font_size: int = 12,
        logger: Optional[CustomLogger] = None,
        output_interface: Optional[OutputInterfaceAbstraction] = None,
    ):
        """Initialize the PDF generator."""

        opath = Path(output_name)
        super().__init__(path, opath.stem, logger, output_interface)

        self._fleat_market_data = fleat_market_data
        self._template_path = Path(pdf_template) if pdf_template else None
        self._coords: List[CoordinatesConfig] = coordinates or self.DEFAULT_COORDS
        self._display_dpi = display_dpi
        self._pickup_date = pickup_date
        self._font_name = font_name
        self._font_size = font_size
        register_font(self._font_name)
        if not self._coords:
            raise ValueError(
                "Es wurden keine Koordinaten definiert und ReportLab ist nicht verfügbar."
            )

        self._entries_per_page = len(self._coords)
        base_path = Path(path) if path else Path(".")
        try:
            self.path = path  # type: ignore[attr-defined]
        except Exception:
            self.path = base_path  # pragma: no cover - for stubbed base
        self._output_pdf = (base_path / opath).with_suffix(".pdf")

        # --------------------------------------------------------------
        # Expose constructor parameters via typed properties
        # --------------------------------------------------------------

    # ---------------------------- properties ----------------------------
    @property
    def template_path(self) -> Optional[Path]:
        """Path to the template PDF or ``None`` if not set."""
        return self._template_path

    @template_path.setter
    def template_path(self, value: str | Path | None) -> None:
        self._template_path = Path(value) if value else None

    @property
    def coordinates(self) -> List[CoordinatesConfig]:
        """List of coordinate configurations used for PDF generation."""
        return self._coords

    @coordinates.setter
    def coordinates(self, value: List[CoordinatesConfig]) -> None:
        if not value:
            raise ValueError("coordinates list cannot be empty")
        self._coords = value
        self._entries_per_page = len(self._coords)

    @property
    def display_dpi(self) -> int:
        """DPI at which coordinates were captured."""
        return self._display_dpi

    @display_dpi.setter
    def display_dpi(self, value: int) -> None:
        if value <= 0:
            raise ValueError("display_dpi must be positive")
        self._display_dpi = value

    @property
    def output_pdf(self) -> Path:
        """Full path of the generated PDF file."""
        return self._output_pdf

    @output_pdf.setter
    def output_pdf(self, value: str | Path) -> None:
        self._output_pdf = Path(value)

    @property
    def pickup_date(self) -> str:
        """Date string inserted into the PDF."""
        return self._pickup_date

    @pickup_date.setter
    def pickup_date(self, value: str) -> None:
        self._pickup_date = value

    @property
    def font_name(self) -> str:
        """Font name used for text rendering."""
        return self._font_name

    @font_name.setter
    def font_name(self, value: str) -> None:
        self._font_name = value
        register_font(value)

    @property
    def font_size(self) -> int:
        """Font size used for text rendering."""
        return self._font_size

    @font_size.setter
    def font_size(self, value: int) -> None:
        self._font_size = value

    # ------------------------------------------------------------------
    # Data collection helpers
    # ------------------------------------------------------------------
    def _seller_rows(self) -> List[Tuple[str, str, str]]:  # noqa: D401
        rows: list[Tuple[str, str, str]] = []
        for idx, main_number in enumerate(self._fleat_market_data.main_numbers()):
            if not getattr(main_number, "is_valid", lambda: False)():
                continue
            try:
                number = str(int(main_number.number()))
            except Exception:
                continue  # silently skip invalid numbers
            try:
                seller = self._fleat_market_data.seller_at(idx)
                name = f"{getattr(seller, 'nachname', 'Unbekannt')}, {getattr(seller, 'vorname', 'Unbekannt')}"
            except Exception:
                name = "Unbekannt, Unbekannt"
            date = self._pickup_date or "TEST DATUM"
            rows.append((name, number, date))
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
            self._output_and_log("ERROR", f"Fehler beim Lesen des Templates: {err}")
            return None

    def _overlay_page(self, rows: Sequence[Tuple[str, str, str]]):  # noqa: D401
        if canvas is None:
            return None  # reportlab missing

        template_bytes = self._template_bytes()
        if template_bytes is None:
            return None

        page = PdfReader(io.BytesIO(template_bytes)).pages[0]
        page_w = float(page.mediabox.width)
        page_h = float(page.mediabox.height)

        packet = io.BytesIO()
        can = canvas.Canvas(packet, pagesize=(page_w, page_h))
        register_font(self._font_name)

        # can.rotate(90)
        can.setFillColor(colors.black)  # type: ignore[arg-type]
        for idx, (f1, f2, f3) in enumerate(rows):
            raw_cfg = self._coords[idx]
            cfg = self._from_display_coords(raw_cfg, page_h, dpi=self._display_dpi)
            can.setFont(self._font_name, cfg.font_size)
            self._draw_centered(can, cfg.x1, cfg.y1, f1, self._font_name, cfg.font_size)
            self._draw_centered(can, cfg.x2, cfg.y2, f2, self._font_name, cfg.font_size)
            self._draw_centered(can, cfg.x3, cfg.y3, f3, self._font_name, cfg.font_size)

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
                "INFO", f"PDF geschrieben: {self._output_pdf.relative_to(Path.cwd())}"
            )
            return True
        except Exception as err:  # pragma: no cover
            self._output_and_log("ERROR", f"Fehler beim Schreiben der PDF: {err}")
            return False

    def _create_writer(
        self,
        rows: Sequence[Tuple[str, str, str]],
        template: bytes,
        tracker: ProgressTrackerAbstraction,
    ) -> PdfWriter:
        """Build a ``PdfWriter`` with all pages."""

        writer = PdfWriter()
        for i in range(0, len(rows), self._entries_per_page):
            grp = rows[i : i + self._entries_per_page]
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
        return writer

    def _task(
        self,
        rows: Sequence[Tuple[str, str, str]],
        template: bytes,
        tracker: ProgressTrackerAbstraction,
    ) -> None:
        """Generate pages and write them to disk."""

        writer = self._create_writer(rows, template, tracker)
        if not tracker.has_error:
            self._write_pdf(writer)

    # ------------------------------------------------------------------
    # Public orchestration
    # ------------------------------------------------------------------
    def generate(
        self,
        overall_tracker: Optional[ProgressTrackerAbstraction] = None,
        *,
        bar: Optional[ProgressBarAbstraction] = None,
    ) -> None:  # noqa: D401
        """Generate the PDF file."""
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
            self._output_and_log("INFO", "Keine gültigen Daten – nichts zu tun.")
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
        tracker = ProgressTracker()
        total_pages = (len(rows) + self._entries_per_page - 1) // self._entries_per_page
        if hasattr(tracker, "reset"):
            tracker.reset(total=total_pages)  # type: ignore[misc]

        if hasattr(self.output_interface, "set_secondary_tracker"):
            try:
                self.output_interface.set_secondary_tracker(tracker)
            except Exception:
                pass

        use_bar = bar or ConsoleProgressBar(length=50, description="PDF")

        # 2. Run with optional console bar ----------------------------------
        if use_bar:
            # type: ignore[arg-type]
            use_bar.run_with_progress(
                target=self._task,
                args=(rows, template, tracker),
                tracker=tracker,
            )
        else:
            self._task(rows, template, tracker)

        # 3. Final state -----------------------------------------------------
        if tracker.has_error:
            self._output_and_log("ERROR", "PDF‑Erstellung fehlgeschlagen – siehe Log.")
            if overall_tracker:
                # type: ignore[attr-defined]
                overall_tracker.set_error(RuntimeError("PDF error"))
        else:
            self._output_and_log("INFO", "PDF‑Erstellung abgeschlossen.")

        if overall_tracker:
            overall_tracker.increment()  # type: ignore[attr-defined]
