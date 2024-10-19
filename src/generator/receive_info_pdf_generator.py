from pypdf import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
import io
from typing import List
import threading
import time
from .data_generator import DataGenerator
from objects import FleatMarket, Seller
from log import logger
from pathlib import Path

class ReceiveInfoPdfGenerator(DataGenerator):
    
    COORDINATES =  [
        (100, -105, 310, -105),  # x1, y1 for name, x2, y2 for stammnummer
        (507, -105, 712, -105),
        (100, -360, 310, -360),
        (507, -360, 712, -360)
    ]


    def __init__(self, fleat_market_data: FleatMarket, path: str = '', pdf_template_path_input: str = '', pdf_template_path_output: str = '') -> None:
        DataGenerator.__init__(self,path, "")
        self.__fleat_market_data = fleat_market_data
         # Lese das Template PDF
        self.template_pdf = pdf_template_path_input
        self.output_pdf = pdf_template_path_output
        self.permission_error = False

    def add_text_to_pdf(self, template_pdf, namen_und_stammnummern, output_pdf, progress):
        # Initialize the PDF writer
        writer = PdfWriter()
        total_entries = len(namen_und_stammnummern)
        total_groups = (total_entries + 3) // 4  # Number of pages to be created

        for i in range(0, total_entries, 4):
            group = namen_und_stammnummern[i:i+4]

            # Read the template page anew for each group
            reader = PdfReader(template_pdf)
            page = reader.pages[0]

            # Create a new canvas for the text overlay
            packet = io.BytesIO()
            can = canvas.Canvas(packet, pagesize=letter)

            # Rotate the canvas if needed
            can.rotate(90)

            # Set font, color, etc.
            can.setFont("Helvetica-Bold", 15)
            can.setFillColor(colors.black)

            for idx, (name, stammnummer) in enumerate(group):
                x1, y1, x2, y2 = self.COORDINATES[idx]
                can.drawString(x1, y1, f"{name}")
                can.drawString(x2, y2, f"{stammnummer}")

            can.save()

            # Move to the beginning of the BytesIO buffer
            packet.seek(0)
            new_pdf = PdfReader(packet)
            overlay_page = new_pdf.pages[0]

            # Merge the overlay with the page
            page.merge_page(overlay_page)

            # Add the page to the writer
            writer.add_page(page)

            # Update progress
            with progress['lock']:
                progress['current'] += 1
                progress['percentage'] = int((progress['current'] / total_groups) * 100)

        # Save the new PDF
        self.output_pdf = Path(self.path).joinpath(output_pdf)    
        try:
            with open(output_pdf, "wb") as output:
                writer.write(output)
        except PermissionError as e: 
            logger.error("\n\n>> PDF konnte nich erstellt werden. Bitte Prüfen ob PDF geschlossen ist. \n" +
                         f">> {str(e)}")
            progress['error'] = True
            

    def thread_function(self, template_pdf, namen_und_stammnummern, output_pdf, progress):
        self.add_text_to_pdf(template_pdf, namen_und_stammnummern, output_pdf, progress)

    def print_progress_bar(self,percentage, length=50):
        filled_length = int(length * percentage // 100)
        bar = '#' * filled_length + '-' * (length - filled_length)
        print(f'\r>> Progress: |{bar}| {percentage}% Complete', end='')


    def generate(self):
               
        data = []
        logger.info("Generiere Abholungsbestätigung:\n" +
                    "      ========================")
        template_file = Path(self.template_pdf)
        if template_file.is_file():
            logger.info(">> Template gefunden\n\n")


            logger.info(">> Erstelle Verkäuferdaten und Stammnummern\n")
            for index, main_number_data in enumerate(self.__fleat_market_data.get_main_number_data_list()):
                #slogger.log_one_line("INFO",True)
                if main_number_data.is_valid():
                    main_number =  main_number_data.get_main_number()
                    first_name = self.__fleat_market_data.get_seller_data(index).vorname
                    second_name = self.__fleat_market_data.get_seller_data(index).nachname
                    data.append((f'{second_name} {first_name}',main_number))

            progress = {
                'lock': threading.Lock(),
                'current': 0,
                'percentage': 0,
                'error' : False
            }
            logger.info(">> Starte generierung der Abholbestätigungen\n\n")
            # Create and start the thread
            thread = threading.Thread(target=self.thread_function, args=(self.template_pdf, data, self.output_pdf, progress))
            thread.start()

            # Main thread: monitor progress
            while thread.is_alive():
                with progress['lock']:
                    percentage = progress['percentage']
                # Print ASCII progress bar
                self.print_progress_bar(percentage)
                time.sleep(0.1)

            if progress['error'] == False:
                # Ensure the final progress is 100%
                self.print_progress_bar(100)
                
                print(f"\n\n>> Abholbestätigungen erstellt! {Path(self.output_pdf).resolve(strict=False)} <<\n\n")
            else:
                print(f"\n\n>> Abholbestätigungen fehlgeschlagen! <<\n\n")
        
        else:
            logger.error(f">> Das PDF Template {self.template_pdf} konnte nicht gefunden werden." + 
                          ">> Bitte Template hinzufügen und erneut ausführen")

    def write(self):
        pass