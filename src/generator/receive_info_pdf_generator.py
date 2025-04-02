import io
import threading
import time
from pathlib import Path
from pypdf import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from .data_generator import DataGenerator
from objects import FleatMarket, Seller
from log import logger
from progress_bar import ProgressBar  # Vorausgesetzt, diese Klasse existiert bereits

class ReceiveInfoPdfGenerator(DataGenerator):
    """
    Generiert PDF-Dokumente mit Verkäuferinformationen und Stammnummern für einen Flohmarkt.

    Die Positionierung der Texte erfolgt anhand von Koordinaten, die direkt als Parameter übergeben werden.
    Erwartetes Format der Koordinaten:
        (x1, y1, x2, y2, x3, y3, font_size)
    Hierbei werden drei x,y-Paare (für drei Textfelder) und ein Fontsize-Wert erwartet.
    """

    def __init__(self, fleat_market_data: FleatMarket, path: str = '',
                 pdf_template_path_input: str = '', pdf_template_path_output: str = '',
                 coordinates: list = None) -> None:
        """
        Initialisiert den PDF-Generator.

        Args:
            fleat_market_data (FleatMarket): Flohmarktdaten.
            path (str, optional): Pfad, in dem die PDF gespeichert wird.
            pdf_template_path_input (str, optional): Pfad zur Eingabe-PDF-Vorlage.
            pdf_template_path_output (str, optional): Pfad zur Ausgabe-PDF.
            coordinates (list, optional): Liste der Koordinaten, wobei jedes Element ein Tupel mit
                7 Werten ist (3 x,y-Paare und ein Fontsize-Wert). Falls nicht angegeben, werden Standardwerte genutzt.
        """
        super().__init__(path, "")
        self.__fleat_market_data = fleat_market_data
        self.template_pdf = pdf_template_path_input
        self.output_pdf = pdf_template_path_output
        self.permission_error = False

        # Falls keine Koordinaten übergeben werden, werden Standardwerte genutzt.
        self.COORDINATES = coordinates if coordinates is not None else [
            (100, -105, 310, -105, 520, -105, 15),
            (507, -105, 712, -105, 917, -105, 15),
            (100, -360, 310, -360, 520, -360, 15),
            (507, -360, 712, -360, 917, -360, 15)
        ]

    def _generate_seller_data(self) -> list:
        """
        Generiert eine Liste von Tupeln (Name, Stammnummer, Zusatzinfo) basierend auf den Flohmarktdaten.
        Die Zusatzinfo wird hier als leerer String eingesetzt.
        """
        data = []
        for index, main_number_data in enumerate(self.__fleat_market_data.get_main_number_data_list()):
            if main_number_data.is_valid():
                main_number = main_number_data.get_main_number()
                seller = self.__fleat_market_data.get_seller_data(index)
                # Reihenfolge: Nachname, Vorname, Stammnummer, Zusatzinfo
                data.append((f'{seller.nachname} {seller.vorname}', main_number, ""))
        return data

    def _create_overlay_page(self, group: list) -> object:
        """
        Erstellt eine Overlay-Seite mit den Textinformationen für eine Gruppe von Einträgen.
        Für jeden Eintrag werden drei Textfelder anhand der übergebenen Koordinaten positioniert.
        """
        packet = io.BytesIO()
        can = canvas.Canvas(packet, pagesize=letter)
        can.rotate(90)
        can.setFillColor(colors.black)

        for idx, (field1, field2, field3) in enumerate(group):
            try:
                # Erwartet wird ein Tupel mit 7 Werten: x1, y1, x2, y2, x3, y3, font_size
                x1, y1, x2, y2, x3, y3, font_size = self.COORDINATES[idx]
            except (ValueError, IndexError):
                # Fallback-Werte, falls die Koordinaten nicht korrekt übergeben wurden
                x1, y1, x2, y2, x3, y3, font_size = 0, 0, 0, 0, 0, 0, 15
            can.setFont("Helvetica-Bold", font_size)
            can.drawString(x1, y1, f"{field1}")
            can.drawString(x2, y2, f"{field2}")
            can.drawString(x3, y3, f"{field3}")

        can.save()
        packet.seek(0)
        new_pdf = PdfReader(packet)
        return new_pdf.pages[0]

    def _write_pdf(self, writer: PdfWriter, output_pdf: str) -> bool:
        """
        Schreibt das PDF in die Ausgabedatei.
        Gibt True zurück, wenn erfolgreich, sonst False.
        """
        output_path = Path(self.path).joinpath(output_pdf)
        try:
            with open(output_path, "wb") as output:
                writer.write(output)
            return True
        except PermissionError as e:
            logger.error("\n\n>> PDF konnte nicht erstellt werden. Bitte prüfen, ob die PDF geschlossen ist.\n" +
                         f">> {str(e)}")
            return False

    def add_text_to_pdf(self, template_pdf: str, data: list, output_pdf: str, progress: dict):
        """
        Erstellt neue PDF-Seiten, indem ein Template geladen, mit Overlay-Informationen versehen
        und anschließend zusammengeführt wird.
        """
        writer = PdfWriter()
        total_entries = len(data)
        total_groups = (total_entries + 3) // 4  # jeweils 4 Einträge pro Seite

        for i in range(0, total_entries, 4):
            group = data[i:i+4]
            reader = PdfReader(template_pdf)
            template_page = reader.pages[0]
            overlay_page = self._create_overlay_page(group)
            template_page.merge_page(overlay_page)
            writer.add_page(template_page)
            with progress['lock']:
                progress['current'] += 1
                progress['percentage'] = int((progress['current'] / total_groups) * 100)

        if not self._write_pdf(writer, output_pdf):
            progress['error'] = True

    def generate(self):
        """
        Hauptmethode zum Erzeugen der PDF-Dokumente:
          - Prüft, ob das Template existiert.
          - Generiert die Verkäuferdaten.
          - Nutzt die erweiterte ProgressBar-Klasse, um die PDF-Erzeugung in einem separaten Thread
            auszuführen und den Fortschritt automatisch anzuzeigen.
        """
        logger.info("Generiere Abholungsbestätigung:\n========================")
        template_file = Path(self.template_pdf)
        if not template_file.is_file():
            logger.error(f">> Das PDF Template {self.template_pdf} konnte nicht gefunden werden. " +
                         "Bitte Template hinzufügen und erneut ausführen")
            return

        logger.info(">> Template gefunden\n")
        logger.info(">> Erstelle Verkäuferdaten und Stammnummern\n")
        seller_data = self._generate_seller_data()

        progress_bar = ProgressBar(length=50, update_interval=0.1)

        logger.info(">> Starte Generierung der Abholbestätigungen\n")
        # Über die ProgressBar wird add_text_to_pdf in einem eigenen Thread ausgeführt
        error = progress_bar.run_with_progress(
            target=self.add_text_to_pdf,
            args=(self.template_pdf, seller_data, self.output_pdf)
        )

        if not error:
            print(f"\n\n>> Abholbestätigungen erstellt! {Path(self.output_pdf).resolve(strict=False)} <<\n")
        else:
            print("\n\n>> Abholbestätigungen fehlgeschlagen! <<\n")

    def write(self):
        pass
