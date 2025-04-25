# --- receive_info_pdf_generator.py ---
import io
import time
from dataclasses import dataclass
from pathlib import Path
from typing import List, Tuple, Optional, Dict, Any

# External dependencies (ensure installed: pip install pypdf reportlab)
try:
    from pypdf import PdfReader, PdfWriter, PageObject
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter, landscape
    from reportlab.lib import colors
    from reportlab.lib.units import mm
except ImportError:
    # Provide dummy classes if libraries are missing
    PdfReader = PdfWriter = PageObject = object
    canvas = type('obj', (object,), {'Canvas': lambda *a, **k: None})
    letter = landscape = lambda x: (0,0)
    colors = type('obj', (object,), {'black': None})()
    mm = 1
    # Log error if logger is already available or print
    print("ERROR: pypdf or reportlab not found. PDF generation will fail.")


# Conditional import of CustomLogger
try:
    from log import CustomLogger
except ImportError:
    CustomLogger = None # type: ignore

# Assume objects and ProgressTracker/ConsoleProgressBar are available
try:
    from objects import FleatMarket, Seller # Adjust names
except ImportError:
    class FleatMarket: get_main_number_list=lambda self: []; get_seller_data=lambda i: Seller()
    class Seller: vorname="Dummy"; nachname="Dummy"
try:
    from .progress_tracker import ProgressTracker
except ImportError:
    ProgressTracker = None # type: ignore
try:
    from .console_progress_bar import ConsoleProgressBar
except ImportError:
    ConsoleProgressBar = None # type: ignore


from .data_generator import DataGenerator

@dataclass
class CoordinatesConfig:
    """ Configuration for text placement in the PDF overlay. """
    x1: float; y1: float; x2: float; y2: float; x3: float; y3: float
    font_size: int = 12

class ReceiveInfoPdfGenerator(DataGenerator):
    """ Generates PDF receive confirmations, using optional logging and progress bar. """

    # FILE_SUFFIX not strictly needed as output name is explicit

    def __init__(self,
                 fleat_market_data: FleatMarket,
                 path: str = '',
                 pdf_template_path_input: str = '',
                 pdf_template_path_output: str = 'abholbestaetigung.pdf',
                 coordinates: Optional[List[CoordinatesConfig]] = None,
                 logger: Optional[CustomLogger] = None) -> None:
        """ Initializes the PDF Generator with data, paths, coords, and logger. """
        # Use the output PDF name's stem for the base class file_name
        output_pdf_path_obj = Path(pdf_template_path_output)
        super().__init__(path, output_pdf_path_obj.stem, logger) # Pass logger
        self.__fleat_market_data = fleat_market_data
        self.template_pdf_path = Path(pdf_template_path_input) if pdf_template_path_input else None
        self.output_pdf_path = self.path / output_pdf_path_obj # Full output path
        # self.logger inherited

        # Default coordinates (example for A4 landscape, adjust to your template!)
        default_coords = [
            CoordinatesConfig(20*mm, -30*mm, 80*mm, -30*mm, 140*mm, -30*mm, 12),
            CoordinatesConfig(160*mm, -30*mm, 220*mm, -30*mm, 280*mm, -30*mm, 12),
            CoordinatesConfig(20*mm, -130*mm, 80*mm, -130*mm, 140*mm, -130*mm, 12),
            CoordinatesConfig(160*mm, -130*mm, 220*mm, -130*mm, 280*mm, -130*mm, 12),
        ]
        self.COORDINATES: List[CoordinatesConfig] = coordinates if coordinates is not None else default_coords
        self.entries_per_page = len(self.COORDINATES)
        if self.entries_per_page <= 0:
             self._log("ERROR", "Koordinatenliste darf nicht leer sein.")
             raise ValueError("Koordinatenliste darf nicht leer sein.")

    def _generate_seller_data(self) -> List[Tuple[str, str, str]]:
        """ Generates list of (Name, Number, Info) tuples for valid sellers. """
        data: List[Tuple[str, str, str]] = []
        valid_count, invalid_count = 0, 0
        try:
            all_main_numbers_data = self.__fleat_market_data.get_main_number_list()
        except AttributeError:
             self._log("ERROR", "FleatMarket Objekt hat keine Methode 'get_main_number_list'.")
             return []
        except Exception as e:
             self._log("ERROR", f"Fehler beim Abrufen der Hauptnummern-Daten für PDF: {e}")
             return []

        for index, main_number_data in enumerate(all_main_numbers_data):
            if not hasattr(main_number_data, 'is_valid') or not main_number_data.is_valid():
                invalid_count += 1; continue

            try:
                if not hasattr(main_number_data, 'get_main_number'):
                     self._log("WARNING", f"Hauptnummern-Datenobjekt Index {index} hat keine 'get_main_number'.")
                     invalid_count += 1; continue
                main_number = str(main_number_data.get_main_number())

                seller: Seller = self.__fleat_market_data.get_seller_data(index)
                if not all(hasattr(seller, attr) for attr in ['nachname', 'vorname']):
                    self._log("WARNING", f"Seller-Objekt Index {index} unvollständig.")
                    seller_name = "Unbekannt, Unbekannt"
                else:
                    seller_name = f'{seller.nachname}, {seller.vorname}' # Adjust format if needed

                additional_info = "" # Placeholder for third field
                data.append((seller_name, main_number, additional_info))
                valid_count += 1
            except IndexError:
                 self._log("ERROR", f"Kein Verkäufer für gültige Hauptnummer bei Index {index}.")
                 invalid_count += 1
            except AttributeError as e:
                 self._log("ERROR", f"Fehlendes Attribut/Methode bei PDF-Daten für Index {index}: {e}")
                 invalid_count += 1
            except Exception as e:
                self._log("ERROR", f"Fehler beim Generieren der PDF-Daten für Index {index}: {e}")
                invalid_count += 1

        self._log("INFO", f"PDF-Daten generiert: {valid_count} gültige, {invalid_count} ungültige/übersprungen.")
        return data

    def _get_template_bytes(self) -> Optional[bytes]:
        """ Loads the template PDF into memory bytes. """
        if not self.template_pdf_path or not self.template_pdf_path.is_file():
            self._log("ERROR", f"Template PDF '{self.template_pdf_path}' nicht gefunden oder nicht angegeben.")
            return None
        try:
            with open(self.template_pdf_path, "rb") as f:
                return f.read()
        except IOError as e:
            self._log("ERROR", f"Fehler beim Lesen der Template PDF '{self.template_pdf_path}': {e}")
            return None
        except Exception as e:
            self._log("ERROR", f"Unerwarteter Fehler beim Laden des Templates: {e}")
            return None

    def _create_overlay_page(self, group: List[Tuple[str, str, str]]) -> Optional[PageObject]:
        """ Creates an overlay PDF page using ReportLab. """
        if not group: return None
        packet = io.BytesIO()
        try:
            # Assume template is landscape or canvas size matches rotated template
            page_width, page_height = landscape(letter) # Adjust page size if needed
            can = canvas.Canvas(packet, pagesize=(page_width, page_height))
            can.setFillColor(colors.black)

            for idx, (field1, field2, field3) in enumerate(group):
                if idx >= len(self.COORDINATES):
                    self._log("WARNING", f"Mehr Daten ({idx+1}) als Koordinaten ({len(self.COORDINATES)}) definiert. Überspringe Rest.")
                    break
                config: CoordinatesConfig = self.COORDINATES[idx]
                try:
                    can.setFont("Helvetica-Bold", config.font_size) # Adjust font if needed
                except Exception as e:
                    self._log("ERROR", f"Fehler beim Setzen der Schriftart: {e}. Verwende Standard.")
                    can.setFont("Helvetica", 10)
                can.drawString(config.x1, config.y1, str(field1))
                can.drawString(config.x2, config.y2, str(field2))
                can.drawString(config.x3, config.y3, str(field3))

            can.save(); packet.seek(0)
            overlay_pdf = PdfReader(packet)
            return overlay_pdf.pages[0] if overlay_pdf.pages else None
        except Exception as e:
            self._log("ERROR", f"Fehler beim Erstellen der ReportLab Overlay-Seite: {e}")
            return None

    def _write_pdf(self, writer: PdfWriter) -> bool:
        """ Writes the final PDF content to the output file. """
        self._log("INFO", f"Versuche PDF zu schreiben nach: {self.output_pdf_path}")
        try:
            self.output_pdf_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.output_pdf_path, "wb") as output_file:
                writer.write(output_file)
            self._log("INFO", f"PDF erfolgreich geschrieben: {self.output_pdf_path.resolve()}")
            return True
        except PermissionError as e:
             self._log("ERROR", f"Keine Berechtigung zum Schreiben der PDF: {e}")
             return False
        except IOError as e:
            self._log("ERROR", f"E/A-Fehler beim Schreiben der PDF: {e}")
            return False
        except Exception as e:
            self._log("ERROR", f"Unerwarteter Fehler beim Schreiben der PDF: {e}")
            return False

    def _add_text_to_pdf_task(self, template_bytes: bytes, data: List[Tuple[str, str, str]], tracker: ProgressTracker) -> None:
        """ Task running in a thread to merge template and overlays. """
        writer = PdfWriter()
        total_entries = len(data)
        total_pages = (total_entries + self.entries_per_page - 1) // self.entries_per_page
        if total_pages == 0 and total_entries > 0: total_pages = 1

        if ProgressTracker is None: # Should not happen if check in generate() works
             self._log("ERROR", "ProgressTracker nicht verfügbar in PDF Task.")
             return
        tracker.reset(total=total_pages)
        self._log("INFO", f"Erstelle {total_pages} PDF-Seiten für {total_entries} Einträge...")

        for i in range(0, total_entries, self.entries_per_page):
            page_index = i // self.entries_per_page
            group = data[i : i + self.entries_per_page]
            try:
                reader = PdfReader(io.BytesIO(template_bytes))
                if not reader.pages: raise ValueError("Template PDF hat keine Seiten.")
                template_page = reader.pages[0] # Assume single page template
            except Exception as e:
                err_msg = f"Fehler beim Laden der Template-Seite {page_index + 1}: {e}"
                self._log("ERROR", err_msg)
                tracker.set_error(ValueError(err_msg)); return

            try:
                overlay_page = self._create_overlay_page(group)
                if overlay_page:
                    template_page.merge_page(overlay_page)
                else:
                     self._log("WARNING", f"Kein Overlay für Seite {page_index + 1} erstellt.")
                writer.add_page(template_page)
                tracker.increment()
            except Exception as e:
                err_msg = f"Fehler beim Erstellen/Mergen von Seite {page_index + 1}: {e}"
                self._log("ERROR", err_msg)
                tracker.set_error(RuntimeError(err_msg)); return

        if not tracker.has_error:
            if not self._write_pdf(writer):
                tracker.set_error(IOError(f"PDF Schreibfehler: {self.output_pdf_path}"))
        else:
             self._log("WARNING", "PDF wurde wegen vorheriger Fehler nicht geschrieben.")

    def generate(self, overall_tracker: Optional[ProgressTracker] = None):
        """ Main method to generate the PDF with progress display. """
        # Check if dependencies are available
        if ProgressTracker is None or ConsoleProgressBar is None:
             self._log("ERROR", "ProgressTracker/ConsoleProgressBar nicht importiert. PDF-Generierung übersprungen.")
             if overall_tracker: overall_tracker.increment(); overall_tracker.set_error(ImportError("Missing progress classes"))
             return
        if PdfReader is object: # Check if dummy class is used
             self._log("ERROR", "pypdf/reportlab nicht installiert. PDF-Generierung übersprungen.")
             if overall_tracker: overall_tracker.increment(); overall_tracker.set_error(ImportError("Missing PDF libraries"))
             return

        self._log("INFO", f"Starte Generierung der Abholbestätigung ({self.output_pdf_path.name}):\n"
                    "========================================")

        # 1. Template
        self._log("INFO", f">> Prüfe Template: {self.template_pdf_path}")
        template_bytes = self._get_template_bytes()
        if template_bytes is None:
            if overall_tracker and isinstance(overall_tracker, ProgressTracker):
                overall_tracker.set_error(FileNotFoundError(f"Template nicht gefunden: {self.template_pdf_path}"))
                overall_tracker.increment()
            return
        self._log("INFO", ">> Template erfolgreich geladen.")

        # 2. Data
        self._log("INFO", ">> Erstelle Verkäuferdaten für PDF...")
        seller_data = self._generate_seller_data()
        if not seller_data:
            self._log("WARNING", ">> Keine gültigen Verkäuferdaten für PDF. Generierung abgebrochen.")
            if overall_tracker and isinstance(overall_tracker, ProgressTracker):
                overall_tracker.increment() # Mark as done (nothing to do)
            return
        self._log("INFO", f">> {len(seller_data)} Einträge für PDF vorbereitet.")

        # 3. Progress and Task Setup
        pdf_tracker = ProgressTracker()
        pdf_progress_bar = ConsoleProgressBar(length=50, description="PDF Erstellung")
        self._log("INFO", ">> Starte PDF-Erzeugung im Hintergrund...")

        # 4. Run task with progress bar
        error: Optional[Exception] = pdf_progress_bar.run_with_progress(
            target=self._add_text_to_pdf_task,
            args=(template_bytes, seller_data, pdf_tracker),
            tracker=pdf_tracker
        )

        # 5. Evaluate and update overall tracker
        if error:
            # Error message is already printed by ConsoleProgressBar.complete
            self._log("ERROR", f"Fehler bei PDF-Erstellung: {error}") # Log it formally too
            if overall_tracker and isinstance(overall_tracker, ProgressTracker):
                overall_tracker.set_error(error)
        else:
            # Success message printed by ConsoleProgressBar.complete
            self._log("INFO", f"Abholbestätigungen scheinbar erfolgreich erstellt: {self.output_pdf_path.resolve()}")

        if overall_tracker and isinstance(overall_tracker, ProgressTracker):
            overall_tracker.increment()
        elif overall_tracker:
             self._log("WARNING", "overall_tracker wurde übergeben, ist aber kein ProgressTracker.")

    def write(self) -> None:
        """ Not used directly; generate() handles the process. """
        pass