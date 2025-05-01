# --- receive_info_pdf_generator.py ---
import io
import time
from dataclasses import dataclass
from pathlib import Path
from typing import List, Tuple, Optional, Dict, Any

from pypdf import PdfReader, PdfWriter, PageObject
# --- CORRECTED/ADDED ReportLab IMPORTS ---
from reportlab.pdfgen import canvas # The main canvas object for drawing
from reportlab.lib.pagesizes import letter, landscape # Standard page sizes and orientation
from reportlab.lib.units import mm # Measurement units like millimeters
from reportlab.lib import colors # Predefined colors

# External dependencies... (keep as they are)
# Conditional imports... (keep as they are)
try:
    from log import CustomLogger
except ImportError:
    CustomLogger = None
try:
    from objects import FleatMarket, Seller
except ImportError:
    class FleatMarket:
        def get_main_number_list(self): return []
        def get_seller_data(i): return Seller()

        class Seller:
            vorname = "Dummy"
            nachname = "Dummy"
try:
    from src.display import ProgressTrackerAbstraction
except ImportError:
    ProgressTrackerAbstraction = None
try:
    from src.display import ConsoleProgressBar
except ImportError:
    ConsoleProgressBar = None
try:
    from src.display import OutputInterfaceAbstraction  # Added
except ImportError:
    OutputInterfaceAbstraction = None  # Added

from .data_generator import DataGenerator


@dataclass
class CoordinatesConfig:
    # ... (keep as is) ...
    x1: float
    y1: float
    x2: float
    y2: float
    x3: float
    y3: float
    font_size: int = 12


class ReceiveInfoPdfGenerator(DataGenerator):
    """ Generates PDF receive confirmations, using optional logging, output interface, and progress bar. """

    # FILE_SUFFIX not strictly needed as output name is explicit

    def __init__(self,
                 fleat_market_data: FleatMarket,
                 path: str = '',
                 pdf_template_path_input: str = '',
                 pdf_template_path_output: str = 'abholbestaetigung.pdf',
                 coordinates: Optional[List[CoordinatesConfig]] = None,
                 logger: Optional[CustomLogger] = None,
                 output_interface: Optional[OutputInterfaceAbstraction] = None  # Added
                 ) -> None:
        """ Initializes the PDF Generator with data, paths, coords, logger, and output interface. """
        output_pdf_path_obj = Path(pdf_template_path_output)
        # Pass logger and output_interface to base class
        super().__init__(path, output_pdf_path_obj.stem, logger, output_interface)
        self.__fleat_market_data = fleat_market_data
        self.template_pdf_path = Path(pdf_template_path_input) if pdf_template_path_input else None
        self.output_pdf_path = self.path / output_pdf_path_obj  # Full output path
        # self.logger, self.output_interface inherited

        default_coords = [
            # ... (keep default_coords) ...
            CoordinatesConfig(20*mm, -30*mm, 80*mm, -30*mm, 140*mm, -30*mm, 12),
            CoordinatesConfig(160*mm, -30*mm, 220*mm, -30*mm, 280*mm, -30*mm, 12),
            CoordinatesConfig(20*mm, -130*mm, 80*mm, -130*mm, 140*mm, -130*mm, 12),
            CoordinatesConfig(160*mm, -130*mm, 220*mm, -130*mm, 280*mm, -130*mm, 12),
        ]
        self.COORDINATES: List[CoordinatesConfig] = coordinates if coordinates is not None else default_coords
        self.entries_per_page = len(self.COORDINATES)
        if self.entries_per_page <= 0:
            # Critical configuration error
            err_msg = "Koordinatenliste darf nicht leer sein."
            self._output_and_log("ERROR", err_msg)
            raise ValueError(err_msg)

    def _generate_seller_data(self) -> List[Tuple[str, str, str]]:
        """ Generates list of (Name, Number, Info) tuples for valid sellers. """
        data: List[Tuple[str, str, str]] = []
        valid_count, invalid_count = 0, 0
        try:
            all_main_numbers_data = self.__fleat_market_data.get_main_number_list()
        except AttributeError:
            # Critical error
            err_msg = "FleatMarket Objekt hat keine Methode 'get_main_number_list'."
            self._output_and_log("ERROR", err_msg)
            return []
        except Exception as e:
            err_msg = f"Fehler beim Abrufen der Hauptnummern-Daten für PDF: {e}"
            self._output_and_log("ERROR", err_msg)
            return []

        for index, main_number_data in enumerate(all_main_numbers_data):
            # Skipping invalid is normal, only log debug/info
            if not hasattr(main_number_data, 'is_valid') or not main_number_data.is_valid():
                invalid_count += 1
                # self._log("DEBUG", f"Überspringe ungültigen Haupteintrag Index {index} für PDF.")
                continue

            try:
                if not hasattr(main_number_data, 'get_main_number'):
                    # Data structure warning - potentially user relevant
                    self._output_and_log(
                        "WARNING", f"Hauptnummern-Datenobjekt Index {index} hat keine 'get_main_number'. Übersprungen.")
                    invalid_count += 1
                    continue
                main_number = str(main_number_data.get_main_number())

                seller: Seller = self.__fleat_market_data.get_seller_data(index)
                if not all(hasattr(seller, attr) for attr in ['nachname', 'vorname']):
                    # Missing seller info warning
                    self._output_and_log("WARNING", f"Seller-Objekt Index {index} unvollständig. Verwende 'Unbekannt'.")
                    seller_name = "Unbekannt, Unbekannt"
                else:
                    seller_name = f'{seller.nachname}, {seller.vorname}'  # Adjust format if needed

                additional_info = ""  # Placeholder for third field
                data.append((seller_name, main_number, additional_info))
                valid_count += 1
            except IndexError:
                # Error: Valid main number but no seller data
                self._output_and_log(
                    "ERROR", f"Kein Verkäufer für gültige Hauptnummer bei Index {index}. Übersprungen.")
                invalid_count += 1
            except AttributeError as e:
                # Error: Missing method/attribute during processing
                self._output_and_log(
                    "ERROR", f"Fehlendes Attribut/Methode bei PDF-Daten für Index {index}: {e}. Übersprungen.")
                invalid_count += 1
            except Exception as e:
                # General error during processing
                self._output_and_log(
                    "ERROR", f"Fehler beim Generieren der PDF-Daten für Index {index}: {e}. Übersprungen.")
                invalid_count += 1

        # Summary message
        self._output_and_log(
            "INFO", f"PDF-Daten generiert: {valid_count} gültige, {invalid_count} ungültige/übersprungen.")
        return data

    def _get_template_bytes(self) -> Optional[bytes]:
        """ Loads the template PDF into memory bytes. """
        if not self.template_pdf_path or not self.template_pdf_path.is_file():
            # Critical error: Template missing
            err_msg = f"Template PDF '{self.template_pdf_path}' nicht gefunden oder nicht angegeben."
            self._output_and_log("ERROR", err_msg)
            return None
        try:
            with open(self.template_pdf_path, "rb") as f:
                return f.read()
        except IOError as e:
            # Critical error: Cannot read template
            err_msg = f"Fehler beim Lesen der Template PDF '{self.template_pdf_path}': {e}"
            self._output_and_log("ERROR", err_msg)
            return None
        except Exception as e:
            err_msg = f"Unerwarteter Fehler beim Laden des Templates: {e}"
            self._output_and_log("ERROR", err_msg)
            return None

    def _create_overlay_page(self, group: List[Tuple[str, str, str]]) -> Optional[PageObject]:
        """ Creates an overlay PDF page using ReportLab. """
        if not group:
            return None
        packet = io.BytesIO()
        try:
            page_width, page_height = landscape(letter)
            can = canvas.Canvas(packet, pagesize=(page_width, page_height))
            can.setFillColor(colors.black)

            for idx, (field1, field2, field3) in enumerate(group):
                if idx >= len(self.COORDINATES):
                    # Warning: Data mismatch
                    self._output_and_log(
                        "WARNING", f"Mehr Daten ({idx+1}) als Koordinaten ({len(self.COORDINATES)}) definiert. Überspringe Rest.")
                    break
                config: CoordinatesConfig = self.COORDINATES[idx]
                try:
                    can.setFont("Helvetica-Bold", config.font_size)
                except Exception as e:
                    # Error setting font - might affect output appearance
                    self._output_and_log("ERROR", f"Fehler beim Setzen der Schriftart: {e}. Verwende Standard.")
                    can.setFont("Helvetica", 10)  # Fallback
                can.drawString(config.x1, config.y1, str(field1))
                can.drawString(config.x2, config.y2, str(field2))
                can.drawString(config.x3, config.y3, str(field3))

            can.save()
            packet.seek(0)
            overlay_pdf = PdfReader(packet)
            return overlay_pdf.pages[0] if overlay_pdf.pages else None
        except Exception as e:
            # Error during overlay creation
            self._output_and_log("ERROR", f"Fehler beim Erstellen der ReportLab Overlay-Seite: {e}")
            return None

    def _write_pdf(self, writer: PdfWriter) -> bool:
        """ Writes the final PDF content to the output file. """
        # Log internal step, user sees final message later or error now
        self._log("INFO", f"Versuche PDF zu schreiben nach: {self.output_pdf_path}")
        try:
            self.output_pdf_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.output_pdf_path, "wb") as output_file:
                writer.write(output_file)
            # Success message - user relevant
            self._output_and_log("INFO", f"PDF erfolgreich geschrieben: {self.output_pdf_path.resolve()}")
            return True
        except PermissionError as e:
            # Write errors are critical
            err_msg = f"Keine Berechtigung zum Schreiben der PDF: {e}"
            self._output_and_log("ERROR", err_msg)
            return False
        except IOError as e:
            err_msg = f"E/A-Fehler beim Schreiben der PDF: {e}"
            self._output_and_log("ERROR", err_msg)
            return False
        except Exception as e:
            err_msg = f"Unerwarteter Fehler beim Schreiben der PDF: {e}"
            self._output_and_log("ERROR", err_msg)
            return False

    def _add_text_to_pdf_task(self, template_bytes: bytes, data: List[Tuple[str, str, str]], tracker: ProgressTrackerAbstraction) -> None:
        """ Task running in a thread to merge template and overlays. """
        writer = PdfWriter()
        total_entries = len(data)
        total_pages = (total_entries + self.entries_per_page - 1) // self.entries_per_page
        if total_pages == 0 and total_entries > 0:
            total_pages = 1

        if ProgressTrackerAbstraction is None:
            err_msg = "ProgressTrackerInterface nicht verfügbar in PDF Task."
            self._output_and_log("ERROR", err_msg)  # Critical setup error
            return
        tracker.reset(total=total_pages)
        # Progress start message
        self._output_and_log("INFO", f"Erstelle {total_pages} PDF-Seiten für {total_entries} Einträge...")

        for i in range(0, total_entries, self.entries_per_page):
            page_index = i // self.entries_per_page
            group = data[i: i + self.entries_per_page]
            try:
                reader = PdfReader(io.BytesIO(template_bytes))
                if not reader.pages:
                    raise ValueError("Template PDF hat keine Seiten.")
                template_page = reader.pages[0]
            except Exception as e:
                # Error loading template page is critical for this step
                err_msg = f"Fehler beim Laden der Template-Seite {page_index + 1}: {e}"
                self._output_and_log("ERROR", err_msg)
                tracker.set_error(ValueError(err_msg))
                return

            try:
                overlay_page = self._create_overlay_page(group)
                if overlay_page:
                    template_page.merge_page(overlay_page)
                else:
                    # Warning if overlay failed but process continues
                    self._output_and_log(
                        "WARNING", f"Kein Overlay für Seite {page_index + 1} erstellt (möglicherweise wegen vorherigem Fehler).")
                writer.add_page(template_page)
                tracker.increment()
                self._log("DEBUG", f"PDF Seite {page_index + 1}/{total_pages} erstellt.")  # Debug log progress
            except Exception as e:
                # Error merging page is critical
                err_msg = f"Fehler beim Erstellen/Mergen von Seite {page_index + 1}: {e}"
                self._output_and_log("ERROR", err_msg)
                tracker.set_error(RuntimeError(err_msg))
                return

        if not tracker.has_error:
            if not self._write_pdf(writer):  # write_pdf handles its own output/log
                # Error already logged by _write_pdf, just set tracker state
                tracker.set_error(IOError(f"PDF Schreibfehler: {self.output_pdf_path}"))
        else:
            # Inform user why PDF wasn't written
            self._output_and_log("WARNING", "PDF wurde wegen vorheriger Fehler nicht geschrieben.")

    def generate(self, overall_tracker: Optional[ProgressTrackerAbstraction] = None):
        """ Main method to generate the PDF with progress display. """
        # Dependency check errors are critical
        if ProgressTrackerAbstraction is None or ConsoleProgressBar is None:
            err_msg = "ProgressTrackerInterface/ConsoleProgressBar nicht importiert. PDF-Generierung übersprungen."
            self._output_and_log("ERROR", err_msg)
            if overall_tracker:
                overall_tracker.increment()
                overall_tracker.set_error(ImportError("Missing progress classes"))
            return
        if PdfReader is object:
            err_msg = "pypdf/reportlab nicht installiert. PDF-Generierung übersprungen."
            self._output_and_log("ERROR", err_msg)
            if overall_tracker:
                overall_tracker.increment()
                overall_tracker.set_error(ImportError("Missing PDF libraries"))
            return

        # Main start message
        self._output_and_log("INFO", f"Starte Generierung der Abholbestätigung ({self.output_pdf_path.name}):\n"
                             "========================================")

        # 1. Template Check
        self._output(">> Prüfe Template: {self.template_pdf_path}")  # Use _output for steps
        template_bytes = self._get_template_bytes()  # Method handles its own output/log on error
        if template_bytes is None:
            # Error already logged, just update tracker and return
            if overall_tracker and isinstance(overall_tracker, ProgressTrackerAbstraction):
                overall_tracker.set_error(FileNotFoundError(f"Template nicht gefunden: {self.template_pdf_path}"))
                overall_tracker.increment()
            return
        self._output(">> Template erfolgreich geladen.")

        # 2. Data Generation
        self._output(">> Erstelle Verkäuferdaten für PDF...")  # Use _output for steps
        seller_data = self._generate_seller_data()  # Method handles its own output/log
        if not seller_data:
            # Warning/Info already logged, just update tracker and return
            # Inform user explicitly
            self._output(">> Keine gültigen Verkäuferdaten gefunden. PDF-Generierung abgebrochen.")
            if overall_tracker and isinstance(overall_tracker, ProgressTrackerAbstraction):
                overall_tracker.increment()  # Mark as done
            return
        self._output(f">> {len(seller_data)} Einträge für PDF vorbereitet.")

        # 3. Progress Setup
        pdf_tracker = ProgressTrackerAbstraction()
        # ConsoleProgressBar writes to console itself, no need to use _output for its messages
        pdf_progress_bar = ConsoleProgressBar(length=50, description="PDF Erstellung")
        self._output(">> Starte PDF-Erzeugung im Hintergrund...")  # Inform user

        # 4. Run Task - Progress bar handles its output
        error: Optional[Exception] = pdf_progress_bar.run_with_progress(
            target=self._add_text_to_pdf_task,
            args=(template_bytes, seller_data, pdf_tracker),
            tracker=pdf_tracker
        )

        # 5. Evaluate Result - ConsoleProgressBar shows status, add final summary via _output_and_log
        if error:
            # Error message is already printed by ConsoleProgressBar.complete
            # Log it formally too, and maybe provide a shorter user message if needed
            self._output_and_log("ERROR", f"Fehler bei PDF-Erstellung abgeschlossen: {error}")
            if overall_tracker and isinstance(overall_tracker, ProgressTrackerAbstraction):
                overall_tracker.set_error(error)
        else:
            # Success message already printed by ConsoleProgressBar.complete
            # Log formally and maybe provide final confirmation to user interface
            self._output_and_log(
                "INFO", f"Abholbestätigungen scheinbar erfolgreich erstellt: {self.output_pdf_path.resolve()}")

        # Update overall tracker - internal, only log maybe
        if overall_tracker and isinstance(overall_tracker, ProgressTrackerAbstraction):
            overall_tracker.increment()
            self._log("DEBUG", "Overall tracker incremented for ReceiveInfoPdfGenerator.")
        elif overall_tracker:
            # Warning about tracker type
            self._output_and_log("WARNING", "overall_tracker wurde übergeben, ist aber kein ProgressTrackerInterface.")

    def write(self) -> None:
        """ Not used directly; generate() handles the process. """
        pass
