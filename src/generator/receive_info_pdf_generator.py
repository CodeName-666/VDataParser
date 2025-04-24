# --- receive_info_pdf_generator.py ---
import io
# import json # json wurde nicht verwendet
import time # Wird nicht mehr direkt verwendet, könnte für Pausen rein
from dataclasses import dataclass
from pathlib import Path
from typing import List, Tuple, Optional, Dict, Any

# Externe Abhängigkeiten - sicherstellen, dass sie installiert sind!
try:
    from pypdf import PdfReader, PdfWriter, PageObject
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter, landscape # landscape ggf. nützlich
    from reportlab.lib import colors
    from reportlab.lib.units import mm # Für Maßeinheiten
except ImportError:
    print("FEHLER: Benötigte Bibliotheken 'pypdf' oder 'reportlab' nicht gefunden.")
    print("Bitte installieren Sie sie mit: pip install pypdf reportlab")
    # Dummy-Klassen, damit der Rest des Codes zumindest geladen werden kann
    class PdfReader: pass
    class PdfWriter: pass
    class PageObject: pass
    class canvas:
        class Canvas:
            def __init__(self, *args, **kwargs): pass
            def rotate(self, angle): pass
            def setFillColor(self, color): pass
            def setFont(self, name, size): pass
            def drawString(self, x, y, text): pass
            def save(self): pass
    letter = (0,0)
    colors = type('obj', (object,), {'black': None})()


# Annahme: Benötigte Objekte sind in 'objects.py' und Logger in 'log.py'
try:
    from objects import FleatMarket, Seller # Beispielnamen, anpassen!
    from log import logger # Beispielnamen, anpassen!
except ImportError:
    print("WARNUNG: Konnte 'objects' oder 'log' nicht importieren.")
    # Dummy-Implementierungen
    class FleatMarket:
        def get_main_number_data_list(self): return []
        def get_seller_data(self, index): raise IndexError
    class Seller:
        vorname = "Unbekannt"
        nachname = "Unbekannt"
    class Logger:
        def info(self, msg): print(f"INFO: {msg}")
        def warning(self, msg): print(f"WARN: {msg}")
        def error(self, msg): print(f"ERROR: {msg}")
        def debug(self, msg): print(f"DEBUG: {msg}")
    logger = Logger()

from .data_generator import DataGenerator
# Annahme: ProgressTracker und ConsoleProgressBar existieren
try:
    from .progress_tracker import ProgressTracker
    from .console_progress_bar import ConsoleProgressBar
except ImportError:
    ProgressTracker = None
    ConsoleProgressBar = None


@dataclass
class CoordinatesConfig:
    """
    Konfigurationsobjekt für die Positionierung eines Eintrags im PDF.
    Koordinaten sind typischerweise in PDF-Punkten (1/72 inch) von der unteren linken Ecke.
    ReportLab's drawString erwartet Koordinaten relativ zur unteren linken Ecke *nach* Rotation.
    Beispiel: x1, y1 für Feld 1 (z.B. Name); x2, y2 für Feld 2 (z.B. Nummer); x3, y3 für Feld 3 (z.B. Info)
    font_size: Schriftgröße in Punkten.
    """
    x1: float
    y1: float
    x2: float
    y2: float
    x3: float
    y3: float
    font_size: int = 12 # Standard-Schriftgröße

class ReceiveInfoPdfGenerator(DataGenerator):
    """
    Generiert PDF-Dokumente (Abholbestätigungen) basierend auf einem Template
    und fügt Verkäuferinformationen und Stammnummern an definierten Positionen ein.

    Nutzt pypdf zum Lesen/Schreiben des Templates und reportlab zum Erstellen der Overlays.
    Zeigt während der Erstellung einen Fortschrittsbalken an.
    """

    # FILE_SUFFIX wird hier nicht direkt benötigt, da der Output-Dateiname komplett übergeben wird.
    # FILE_SUFFIX = 'pdf' # Könnte man setzen, aber output_pdf ist maßgeblich.

    def __init__(self,
                 fleat_market_data: FleatMarket,
                 path: str = '', # Ausgabeverzeichnis
                 pdf_template_path_input: str = '', # Pfad zum Template
                 pdf_template_path_output: str = 'abholbestaetigung.pdf', # Name der Ausgabedatei
                 coordinates: Optional[List[CoordinatesConfig]] = None) -> None:
        """
        Initialisiert den PDF-Generator.

        Args:
            fleat_market_data (FleatMarket): Flohmarktdaten.
            path (str): Pfad, in dem die PDF gespeichert wird.
            pdf_template_path_input (str): Pfad zur Eingabe-PDF-Vorlage.
            pdf_template_path_output (str): Name der zu erstellenden Ausgabe-PDF (im 'path').
            coordinates (Optional[List[CoordinatesConfig]]): Liste von Koordinaten-Konfigurationen
                für die Einträge auf *einer* Seite. Wenn None, werden Standardwerte verwendet.
        """
        # Rufe DataGenerator.__init__ auf, obwohl file_name hier weniger relevant ist
        # Der eigentliche Output-Name ist pdf_template_path_output
        super().__init__(path, Path(pdf_template_path_output).stem) # Nutze Stamm des Output-Namens als Basis-Namen
        self.__fleat_market_data = fleat_market_data
        self.template_pdf_path = Path(pdf_template_path_input) if pdf_template_path_input else None
        self.output_pdf_path = self.path / pdf_template_path_output # Kombiniere Pfad und Dateiname


        # Standardkoordinaten (Beispiel für A4, 90 Grad gedreht, 4 Einträge pro Seite)
        # Diese müssen an das *tatsächliche* Template angepasst werden!
        # Koordinaten sind nach der Rotation (unten links ist Ursprung der gedrehten Seite)
        # Einheiten in mm umgerechnet in Punkte (1 mm = 2.8346 Punkte)
        default_coords = [
            # Eintrag 1 (z.B. oben links)
            CoordinatesConfig(x1=20*mm, y1=-30*mm, x2=80*mm, y2=-30*mm, x3=140*mm, y3=-30*mm, font_size=12),
             # Eintrag 2 (z.B. oben rechts)
            CoordinatesConfig(x1=160*mm, y1=-30*mm, x2=220*mm, y2=-30*mm, x3=280*mm, y3=-30*mm, font_size=12),
            # Eintrag 3 (z.B. unten links)
            CoordinatesConfig(x1=20*mm, y1=-130*mm, x2=80*mm, y2=-130*mm, x3=140*mm, y3=-130*mm, font_size=12),
            # Eintrag 4 (z.B. unten rechts)
            CoordinatesConfig(x1=160*mm, y1=-130*mm, x2=220*mm, y2=-130*mm, x3=280*mm, y3=-130*mm, font_size=12),
        ]
        self.COORDINATES: List[CoordinatesConfig] = coordinates if coordinates is not None else default_coords
        self.entries_per_page = len(self.COORDINATES)
        if self.entries_per_page <= 0:
             raise ValueError("Koordinatenliste darf nicht leer sein.")


    def _generate_seller_data(self) -> List[Tuple[str, str, str]]:
        """
        Generiert eine Liste von Tupeln (Feld1, Feld2, Feld3) basierend auf den Flohmarktdaten.
        Feld1: "Nachname, Vorname", Feld2: Stammnummer, Feld3: Leerstring (anpassbar).
        Nur gültige Einträge werden berücksichtigt.

        Returns:
            List[Tuple[str, str, str]]: Liste der Datensätze für die PDF.
        """
        data: List[Tuple[str, str, str]] = []
        valid_count = 0
        invalid_count = 0

        try:
            all_main_numbers_data = self.__fleat_market_data.get_main_number_data_list()
        except AttributeError:
             logger.error("FleatMarket Objekt hat keine Methode 'get_main_number_data_list'. PDF-Generierung nicht möglich.")
             return []
        except Exception as e:
             logger.error(f"Fehler beim Abrufen der Hauptnummern-Daten für PDF: {e}")
             return []

        for index, main_number_data in enumerate(all_main_numbers_data):
            # Prüfe Datenobjekt und Gültigkeit
            if not hasattr(main_number_data, 'is_valid') or not main_number_data.is_valid():
                invalid_count += 1
                continue # Nur gültige Hauptnummern verarbeiten

            # Hole notwendige Daten
            try:
                if not hasattr(main_number_data, 'get_main_number'):
                     logger.warning(f"Hauptnummern-Datenobjekt bei Index {index} hat keine 'get_main_number' Methode.")
                     invalid_count += 1
                     continue
                main_number = str(main_number_data.get_main_number())

                seller: Seller = self.__fleat_market_data.get_seller_data(index)
                if not all(hasattr(seller, attr) for attr in ['nachname', 'vorname']):
                    logger.warning(f"Seller-Objekt bei Index {index} unvollständig.")
                    # Entscheiden: Mit Standardwerten arbeiten oder überspringen?
                    seller_name = "Unbekannt, Unbekannt"
                else:
                    # Format: "Nachname, Vorname" - anpassbar
                    seller_name = f'{seller.nachname}, {seller.vorname}'

                # Zusatzinfo Feld (hier leer, kann aber gefüllt werden)
                additional_info = ""

                data.append((seller_name, main_number, additional_info))
                valid_count += 1

            except IndexError:
                 logger.error(f">> Fehler: Kein Verkäufer für gültige Hauptnummer bei Index {index} gefunden.")
                 invalid_count += 1
            except AttributeError as e:
                 logger.error(f"Fehlendes Attribut/Methode bei Verarbeitung für Index {index}: {e}")
                 invalid_count += 1
            except Exception as e:
                logger.error(f">> Fehler beim Generieren der PDF-Daten für Index {index}: {e}")
                invalid_count += 1

        logger.info(f"PDF-Daten generiert: {valid_count} gültige Einträge, {invalid_count} ungültige/übersprungene.")
        return data

    def _get_template_bytes(self) -> Optional[bytes]:
        """ Lädt die Template-PDF in den Speicher. """
        if not self.template_pdf_path or not self.template_pdf_path.is_file():
            logger.error(f"Template PDF '{self.template_pdf_path}' nicht gefunden oder nicht angegeben.")
            return None
        try:
            with open(self.template_pdf_path, "rb") as f:
                return f.read()
        except IOError as e:
            logger.error(f"Fehler beim Lesen der Template PDF '{self.template_pdf_path}': {e}")
            return None
        except Exception as e:
            logger.error(f"Unerwarteter Fehler beim Laden des Templates: {e}")
            return None


    def _create_overlay_page(self, group: List[Tuple[str, str, str]]) -> Optional[PageObject]:
        """
        Erstellt eine Overlay-Seite mit Textinformationen für eine Gruppe von Einträgen.
        Nutzt ReportLab, um Text an den in self.COORDINATES definierten Positionen zu zeichnen.
        Die Seite wird für das Mergen mit pypdf vorbereitet.
        """
        if not group:
            return None

        packet = io.BytesIO()
        # Annahme: Template ist A4 Querformat, Overlay wird entsprechend erstellt
        # passe pagesize an, falls nötig (z.B. pagesize=landscape(letter))
        try:
            # Wichtig: Die Seitengröße des Canvas muss zur *rotierten* Seitengröße des Templates passen!
            # Wenn das Template A4 Hochformat ist und um 90 Grad gedreht wird,
            # ist die Canvas-Größe landscape(a4). Wenn das Template bereits Querformat ist, ist es a4.
            # Hier nehmen wir an, das Template ist Hochformat und wird gedreht.
            page_width, page_height = landscape(letter) # Oder A4, etc.
            can = canvas.Canvas(packet, pagesize=(page_width, page_height))
            # Rotation ist NICHT mehr nötig, wenn Canvas bereits Querformat hat und die Koordinaten passen!
            # can.rotate(90) # Nur nötig wenn Canvas Hochformat wäre
            can.setFillColor(colors.black) # Standardfarbe

            for idx, (field1, field2, field3) in enumerate(group):
                if idx >= len(self.COORDINATES):
                    logger.warning(f"Mehr Daten in Gruppe als Koordinaten definiert ({idx+1} > {len(self.COORDINATES)}). Überspringe Rest.")
                    break

                config: CoordinatesConfig = self.COORDINATES[idx]
                try:
                    # Schriftart kann angepasst werden (muss aber verfügbar sein)
                    can.setFont("Helvetica-Bold", config.font_size)
                except Exception as e:
                    logger.error(f"Fehler beim Setzen der Schriftart/Größe: {e}. Verwende Standard.")
                    can.setFont("Helvetica", 10)

                # Zeichne die Strings an den konfigurierten Positionen
                # Koordinaten sind vom unteren linken Rand des (ggf. gedrehten) Canvas
                can.drawString(config.x1, config.y1, str(field1))
                can.drawString(config.x2, config.y2, str(field2))
                can.drawString(config.x3, config.y3, str(field3))

            can.save() # Schließt das PDF-Objekt im Buffer
            packet.seek(0)

            # Lese die gerade erstellte Seite mit pypdf ein
            overlay_pdf = PdfReader(packet)
            if overlay_pdf.pages:
                 return overlay_pdf.pages[0]
            else:
                 logger.error("Konnte Overlay-Seite nicht mit pypdf lesen.")
                 return None

        except Exception as e:
            logger.error(f"Fehler beim Erstellen der ReportLab Overlay-Seite: {e}")
            # raise # Fehler weitergeben oder None zurückgeben
            return None


    def _write_pdf(self, writer: PdfWriter) -> bool:
        """ Schreibt das erstellte PDF in die Ausgabedatei. """
        output_path = self.output_pdf_path
        logger.info(f"Versuche PDF zu schreiben nach: {output_path}")
        try:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, "wb") as output_file:
                writer.write(output_file)
            logger.info(f"PDF erfolgreich geschrieben: {output_path.resolve()}")
            return True
        except PermissionError as e:
             logger.error(f"FEHLER: Keine Berechtigung zum Schreiben der PDF: {e}")
             return False
        except IOError as e:
            logger.error(f"FEHLER beim Schreiben der PDF: {e}")
            return False
        except Exception as e:
            logger.error(f"Unerwarteter FEHLER beim Schreiben der PDF: {e}")
            return False


    def _add_text_to_pdf_task(self,
                              template_bytes: bytes,
                              data: List[Tuple[str, str, str]],
                              tracker: ProgressTracker) -> None:
        """
        Task zum Erstellen der PDF-Seiten durch Mergen von Template und Overlays.
        Aktualisiert den übergebenen Tracker. Läuft in einem separaten Thread.
        """
        writer = PdfWriter()
        total_entries: int = len(data)
        # Berechne Anzahl der Seiten basierend auf Einträgen pro Seite
        total_pages: int = (total_entries + self.entries_per_page - 1) // self.entries_per_page
        if total_pages == 0 and total_entries > 0 : total_pages = 1 # Mindestens eine Seite, wenn Daten vorhanden

        tracker.reset(total=total_pages) # Setze Gesamtanzahl der Seiten im Tracker

        logger.info(f"Erstelle {total_pages} PDF-Seiten für {total_entries} Einträge ({self.entries_per_page} pro Seite)...")

        for i in range(0, total_entries, self.entries_per_page):
            page_index = i // self.entries_per_page
            group = data[i : i + self.entries_per_page]

            try:
                # Lade das Template für jede Seite neu aus dem Buffer
                reader = PdfReader(io.BytesIO(template_bytes))
                if not reader.pages:
                     raise ValueError("Template PDF enthält keine Seiten.")
                template_page = reader.pages[0] # Annahme: Template hat nur eine Seite
                 # Optional: Kopieren, um Original nicht zu modifizieren (pypdf macht das oft intern)
                 # template_page = PageObject(template_page)

            except Exception as e:
                err_msg = f"Fehler beim Laden der Template-Seite {page_index + 1}: {e}"
                logger.error(err_msg)
                tracker.set_error(ValueError(err_msg))
                return # Beende Task bei Fehler

            try:
                # Erstelle Overlay für die aktuelle Gruppe
                overlay_page = self._create_overlay_page(group)

                if overlay_page:
                     # Merge Overlay auf Template-Seite
                     # Wichtig: Die Transformationen (z.B. Rotation) müssen übereinstimmen!
                     # Wenn das Template rotiert ist, muss das Overlay entweder auch rotiert
                     # oder die Koordinaten entsprechend angepasst sein.
                     template_page.merge_page(overlay_page) # merge_page fügt Inhalt hinzu
                else:
                     logger.warning(f"Konnte keine Overlay-Seite für Seite {page_index + 1} erstellen. Seite wird ohne Overlays hinzugefügt.")
                     # Optional: Fehler setzen? tracker.set_error(...)

                # Füge die modifizierte Seite zum Writer hinzu
                writer.add_page(template_page)
                tracker.increment() # Melde Fortschritt (eine Seite fertig)

            except Exception as e:
                err_msg = f"Fehler beim Erstellen/Mergen von Seite {page_index + 1}: {e}"
                logger.error(err_msg)
                tracker.set_error(RuntimeError(err_msg))
                return # Beende Task bei Fehler

        # Schreiben der PDF nach der Schleife, wenn keine Fehler aufgetreten sind
        if not tracker.has_error:
            if not self._write_pdf(writer):
                # Setze Fehler im Tracker, wenn Schreiben fehlschlägt
                tracker.set_error(IOError(f"Konnte PDF nicht nach {self.output_pdf_path} schreiben."))
        else:
             logger.warning("PDF wurde aufgrund vorheriger Fehler nicht geschrieben.")


    def generate(self, overall_tracker: Optional[ProgressTracker] = None):
        """
        Hauptmethode: Generiert Verkäuferdaten, lädt Template, startet die PDF-Erzeugung
        mit interner Fortschrittsanzeige und meldet Abschluss an den Gesamt-Tracker.
        """
        if ProgressTracker is None or ConsoleProgressBar is None:
             logger.error("ProgressTracker oder ConsoleProgressBar nicht verfügbar. PDF-Generierung übersprungen.")
             if overall_tracker: overall_tracker.increment() # Zähle als "erledigt"
             return

        logger.info(f"Starte Generierung der Abholbestätigung ({self.output_pdf_path.name}):\n"
                    "========================================")

        # 1. Template prüfen
        if not self.template_pdf_path:
             logger.error("Kein Pfad zur PDF-Vorlage angegeben.")
             if overall_tracker:
                 overall_tracker.set_error(FileNotFoundError("Kein Template-Pfad angegeben."))
                 overall_tracker.increment()
             return

        logger.info(f">> Prüfe Template: {self.template_pdf_path}")
        template_bytes: Optional[bytes] = self._get_template_bytes()
        if template_bytes is None:
            # Fehler wurde bereits in _get_template_bytes geloggt
            if overall_tracker:
                overall_tracker.set_error(FileNotFoundError(f"Template nicht gefunden/lesbar: {self.template_pdf_path}"))
                overall_tracker.increment()
            return
        logger.info(">> Template erfolgreich geladen.")

        # 2. Daten generieren
        logger.info(">> Erstelle Verkäuferdaten für PDF...")
        seller_data: List[Tuple[str, str, str]] = self._generate_seller_data()
        if not seller_data:
            logger.warning(">> Keine gültigen Verkäuferdaten für PDF gefunden. Generierung abgebrochen.")
            if overall_tracker:
                # Kein Fehler, aber auch nichts zu tun
                overall_tracker.increment()
            return
        logger.info(f">> {len(seller_data)} Einträge für PDF vorbereitet.")


        # 3. Internen Tracker und ProgressBar für DIESE Aufgabe erstellen
        pdf_tracker = ProgressTracker() # Wird von _add_text_to_pdf_task befüllt
        pdf_progress_bar = ConsoleProgressBar(length=50, description="PDF Erstellung")

        logger.info(">> Starte PDF-Erzeugung im Hintergrund (dies kann dauern)...")

        # 4. Starte die PDF-Erzeugung im Thread mit Fortschrittsanzeige
        error: Optional[Exception] = pdf_progress_bar.run_with_progress(
            target=self._add_text_to_pdf_task,
            args=(template_bytes, seller_data, pdf_tracker), # Tracker wird übergeben
            tracker=pdf_tracker # ProgressBar nutzt diesen Tracker zur Anzeige
        )

        # 5. Ergebnis auswerten und an Gesamt-Tracker melden
        if error:
            # Fehler wurde bereits von run_with_progress/complete geloggt
            print(f"\n>> FEHLER bei Erstellung der Abholbestätigungen: {error} <<\n")
            if overall_tracker:
                overall_tracker.set_error(error)
        else:
            # Erfolgsmeldung wurde bereits von run_with_progress/complete geloggt
            print(f"\n>> Abholbestätigungen scheinbar erfolgreich erstellt: {self.output_pdf_path.resolve()} <<\n")

         # Melde Abschluss dieser Aufgabe an den Gesamt-Tracker (auch bei Fehler!)
        if overall_tracker and isinstance(overall_tracker, ProgressTracker):
            overall_tracker.increment()
        elif overall_tracker:
             logger.warning("overall_tracker wurde übergeben, ist aber kein ProgressTracker.")


    def write(self) -> None:
        """ Wird nicht direkt verwendet, da generate() das Schreiben initiiert. """
        pass