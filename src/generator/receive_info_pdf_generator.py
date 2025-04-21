import io
import json
import threading
import time
from dataclasses import dataclass
from pathlib import Path
from typing import List, Tuple, Optional, Dict, Any

from pypdf import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors

from .data_generator import DataGenerator
from objects import FleatMarket, Seller
from log import logger
from .progress_bar import ProgressBar  # Erweitert um die Threading-/Progress-Logik

@dataclass
class CoordinatesConfig:
    """
    Konfigurationsobjekt für die Positionierung eines Eintrags im PDF.
    Es enthält drei x,y-Paare für drei Textfelder und einen Fontsize-Wert.
    """
    x1: int
    y1: int
    x2: int
    y2: int
    x3: int
    y3: int
    font_size: int

class ReceiveInfoPdfGenerator(DataGenerator):
    """
    Generiert PDF-Dokumente mit Verkäuferinformationen und Stammnummern für einen Flohmarkt.

    Die Positionierung der Texte erfolgt anhand von Koordinaten, die als Liste von
    `CoordinatesConfig`-Objekten übergeben werden. Für jeden Eintrag werden drei Textfelder
    erstellt (z.B. Name, Stammnummer, Zusatzinfo).
    """

    def __init__(self,
                 fleat_market_data: FleatMarket,
                 path: str = '',
                 pdf_template_path_input: str = '',
                 pdf_template_path_output: str = '',
                 coordinates: Optional[List[CoordinatesConfig]] = None) -> None:
        """
        Initialisiert den PDF-Generator.

        Args:
            fleat_market_data (FleatMarket): Flohmarktdaten.
            path (str): Pfad, in dem die PDF gespeichert wird.
            pdf_template_path_input (str): Pfad zur Eingabe-PDF-Vorlage.
            pdf_template_path_output (str): Pfad zur Ausgabe-PDF.
            coordinates (Optional[List[CoordinatesConfig]]): Liste von Koordinaten-Konfigurationen.
                Falls nicht übergeben, werden Default-Werte genutzt.
        """
        super().__init__(path, "")
        self.__fleat_market_data = fleat_market_data
        self.template_pdf = pdf_template_path_input
        self.output_pdf = pdf_template_path_output
        self.permission_error = False

        # Falls keine Koordinaten übergeben werden, werden Standardwerte als CoordinatesConfig-Objekte genutzt.
        self.COORDINATES: List[CoordinatesConfig] = coordinates if coordinates is not None else [
            CoordinatesConfig(100, -105, 310, -105, 520, -105, 15),
            CoordinatesConfig(507, -105, 712, -105, 917, -105, 15),
            CoordinatesConfig(100, -360, 310, -360, 520, -360, 15),
            CoordinatesConfig(507, -360, 712, -360, 917, -360, 15)
        ]

    def _generate_seller_data(self) -> List[Tuple[str, str, str]]:
        """
        Generiert eine Liste von Tupeln (Name, Stammnummer, Zusatzinfo) basierend auf den Flohmarktdaten.
        Die Zusatzinfo wird hier als leerer String eingesetzt.

        Returns:
            List[Tuple[str, str, str]]: Liste der Datensätze.
        """
        data: List[Tuple[str, str, str]] = []
        for index, main_number_data in enumerate(self.__fleat_market_data.get_main_number_data_list()):
            if main_number_data.is_valid():
                try:
                    main_number = main_number_data.get_main_number()
                    seller: Seller = self.__fleat_market_data.get_seller_data(index)
                    # Reihenfolge: "Nachname Vorname", Stammnummer, Zusatzinfo (leer)
                    data.append((f'{seller.nachname} {seller.vorname}', main_number, ""))
                except Exception as e:
                    logger.error(f">> Fehler beim Generieren der Daten für Index {index}: {str(e)}")
        return data

    def _get_template_bytes(self) -> bytes:
        """
        Lädt die Template-PDF in den Speicher, um wiederholte Dateizugriffe zu vermeiden.

        Returns:
            bytes: Der Inhalt der Template-PDF.
        Raises:
            FileNotFoundError: Falls die Template-PDF nicht gefunden wird.
        """
        template_path = Path(self.template_pdf)
        if not template_path.is_file():
            raise FileNotFoundError(f"Template PDF {self.template_pdf} nicht gefunden.")
        with open(template_path, "rb") as f:
            return f.read()

    def _create_overlay_page(self, group: List[Tuple[str, str, str]]) -> Any:
        """
        Erstellt eine Overlay-Seite mit den Textinformationen für eine Gruppe von Einträgen.
        Für jeden Eintrag werden drei Textfelder anhand der übergebenen Koordinaten positioniert.

        Args:
            group (List[Tuple[str, str, str]]): Liste der Datensätze für eine Seite (max. 4 Einträge).

        Returns:
            Any: Die erzeugte Overlay-Seite als PDF-Seite.
        """
        packet = io.BytesIO()
        can = canvas.Canvas(packet, pagesize=letter)
        can.rotate(90)
        can.setFillColor(colors.black)

        for idx, (field1, field2, field3) in enumerate(group):
            try:
                config: CoordinatesConfig = self.COORDINATES[idx]
            except IndexError:
                # Fallback-Werte, falls weniger Koordinaten definiert sind
                config = CoordinatesConfig(0, 0, 0, 0, 0, 0, 15)
            try:
                can.setFont("Helvetica-Bold", config.font_size)
            except Exception as e:
                logger.error(f">> Fehler beim Setzen der Schriftgröße: {str(e)}")
                can.setFont("Helvetica-Bold", 15)
            can.drawString(config.x1, config.y1, str(field1))
            can.drawString(config.x2, config.y2, str(field2))
            can.drawString(config.x3, config.y3, str(field3))
        can.save()
        packet.seek(0)
        try:
            new_pdf = PdfReader(packet)
            return new_pdf.pages[0]
        except Exception as e:
            logger.error(f">> Fehler beim Erstellen der Overlay-Seite: {str(e)}")
            raise

    def _write_pdf(self, writer: PdfWriter, output_pdf: str) -> bool:
        """
        Schreibt das erstellte PDF in die Ausgabedatei.

        Args:
            writer (PdfWriter): Der PDF-Writer mit den hinzugefügten Seiten.
            output_pdf (str): Der Name der Ausgabedatei.

        Returns:
            bool: True, wenn erfolgreich geschrieben, sonst False.
        """
        output_path = Path(self.path).joinpath(output_pdf)
        try:
            with open(output_path, "wb") as output_file:
                writer.write(output_file)
            return True
        except Exception as e:
            logger.error(f">> Fehler beim Schreiben der PDF: {str(e)}")
            return False

    def add_text_to_pdf(self,
                        template_bytes: bytes,
                        data: List[Tuple[str, str, str]],
                        output_pdf: str,
                        progress: Dict[str, Any]) -> None:
        """
        Erstellt neue PDF-Seiten, indem das Template geladen, mit Overlay-Informationen versehen
        und anschließend zusammengeführt wird.

        Args:
            template_bytes (bytes): Inhalt der Template-PDF.
            data (List[Tuple[str, str, str]]): Liste der Datensätze.
            output_pdf (str): Name der Ausgabedatei.
            progress (Dict[str, Any]): Dictionary zur Fortschrittsüberwachung.
        """
        writer = PdfWriter()
        total_entries: int = len(data)
        total_groups: int = (total_entries + 3) // 4  # 4 Einträge pro Seite

        for i in range(0, total_entries, 4):
            group = data[i:i+4]
            try:
                # Erstelle eine neue Instanz des Template-PDFs aus dem geladenen Bytes-Buffer
                reader = PdfReader(io.BytesIO(template_bytes))
                template_page = reader.pages[0]
            except Exception as e:
                logger.error(f">> Fehler beim Laden der Template-Seite: {str(e)}")
                progress['error'] = True
                return

            try:
                overlay_page = self._create_overlay_page(group)
                template_page.merge_page(overlay_page)
                writer.add_page(template_page)
            except Exception as e:
                logger.error(f">> Fehler beim Zusammenführen der Seiten: {str(e)}")
                progress['error'] = True
                return

            with progress['lock']:
                progress['current'] += 1
                progress['percentage'] = int((progress['current'] / total_groups) * 100)

        if not self._write_pdf(writer, output_pdf):
            progress['error'] = True

    def generate(self) -> None:
        """
        Hauptmethode zum Erzeugen der PDF-Dokumente:
          - Überprüft, ob das Template existiert.
          - Generiert die Verkäuferdaten.
          - Lädt das Template in den Speicher.
          - Nutzt die ProgressBar-Klasse, um die PDF-Erzeugung in einem separaten Thread auszuführen
            und den Fortschritt automatisch anzuzeigen.
        """
        logger.info("Generiere Abholungsbestätigung:\n========================")
        template_path = Path(self.template_pdf)
        if not template_path.is_file():
            logger.error(f">> Das PDF Template {self.template_pdf} konnte nicht gefunden werden. "
                         "Bitte Template hinzufügen und erneut ausführen")
            return

        logger.info(">> Template gefunden\n")
        logger.info(">> Erstelle Verkäuferdaten und Stammnummern\n")
        seller_data: List[Tuple[str, str, str]] = self._generate_seller_data()

        try:
            template_bytes: bytes = self._get_template_bytes()
        except FileNotFoundError as e:
            logger.error(f">> {str(e)}")
            return

        progress_bar = ProgressBar(length=50, update_interval=0.1)

        logger.info(">> Starte Generierung der Abholbestätigungen\n")
        error: bool = progress_bar.run_with_progress(
            target=self.add_text_to_pdf,
            args=(template_bytes, seller_data, self.output_pdf)
        )

        if not error:
            print(f"\n\n>> Abholbestätigungen erstellt! {Path(self.output_pdf).resolve(strict=False)} <<\n")
        else:
            print("\n\n>> Abholbestätigungen fehlgeschlagen! <<\n")

    def write(self) -> None:
        """
        Placeholder-Methode, falls in Zukunft eine alternative Schreiblogik benötigt wird.
        """
        pass
