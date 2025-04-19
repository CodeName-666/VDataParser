from pypdf import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
import io

def add_text_to_pdf(template_pdf, name, stammnummer, output_pdf):
    # Lese das Template PDF
    reader = PdfReader(template_pdf)
    writer = PdfWriter()

    # Für jeden Namen und Stammnummer eine neue Seite erstellen
    for page_number in range(len(reader.pages)):
        page = reader.pages[page_number]

        # Ein Byte-Objekt erstellen, das als neue Seite mit Text dient
        packet = io.BytesIO()
        can = canvas.Canvas(packet, pagesize=letter)

         # Drehe die Zeichenfläche um 90 Grad
        can.rotate(90)
          # Setze die Schriftart auf "Helvetica-Bold" und Größe auf 12
        can.setFont("Helvetica-Bold", 15)

        # Setze den Text auf eine spezifische Farbe (optional)
        can.setFillColor(colors.black)
        # Beispiel: Namen und Stammnummer an einer bestimmten Position auf der Seite einfügen
        can.drawString(100,-105, f"{name}")  # x und y sind angepasst
        can.drawString(310,-105, f"{stammnummer}")  # y ist leicht verschoben für den zweiten Text
        
        can.drawString(507,-105, f"{name}")  # x und y sind angepasst
        can.drawString(712,-105, f"{stammnummer}")  # y ist leicht verschoben für den zweiten Text
        
        can.drawString(100,-360, f"{name}")  # x und y sind angepasst
        can.drawString(310,-360, f"{stammnummer}")  # y ist leicht verschoben für den zweiten Text 

        can.drawString(507,-360, f"{name}")  # x und y sind angepasst
        can.drawString(712,-360, f"{stammnummer}")  # y ist leicht verschoben für den zweiten Text 
        # Weitere Textfelder nach Bedarf hinzufügen (Positionen anpassen)
        # can.drawString(x, y, "Text")

        can.save()

        # Zurück zum Anfang des Byte-Objekts gehen und die neue Seite lesen
        packet.seek(0)
        new_pdf = PdfReader(packet)
        overlay_page = new_pdf.pages[0]

        # Die neue Seite mit der Originalseite überlagern
        page.merge_page(overlay_page)

        # Die bearbeitete Seite dem PDF-Schreiber hinzufügen
        writer.add_page(page)

    # Speichere das neue PDF
    with open(output_pdf, "wb") as output:
        writer.write(output)

def merge_pdfs(pdf_list, output_pdf):
    writer = PdfWriter()

    # Füge jede PDF aus der Liste zum Writer hinzu
    for pdf in pdf_list:
        reader = PdfReader(pdf)
        for page in range(len(reader.pages)):
            writer.add_page(reader.pages[page])

    # Speichere das zusammengeführte PDF
    with open(output_pdf, "wb") as output_file:
        writer.write(output_file)


# Pfade zu den Dateien
template_pdf = 'data\\Unterlagen\\Abholung\\Abholung_Template.pdf'

namen_und_stammnummern = [
    ("Max Mustermann", 10001),
    ("Erika Musterfrau", 10002),
    ("Hans Meier", 10003),
    ("Anna Schmidt", 10004),
    #("Peter Müller", 10005),
    #("Julia Fischer", 10006),
    #("Stefan Weber", 10007),
    #("Laura Wagner", 10008),
    #("Michael Becker", 10009),
    #("Nina Richter", 10010),
    #("Thomas Hoffmann", 10011),
    #("Claudia Schäfer", 10012),
    #("Martin Köhler", 10013),
    #("Susanne Lehmann", 10014),
    #("Daniel Wolf", 10015),
    #("Katharina Jung", 10016),
    #("Markus Klein", 10017),
    #("Carolin Braun", 10018),
    #("Tobias Krüger", 10019),
    #("Sabine Vogel", 10020),
    #("Oliver Neumann", 10021),
    #("Sandra Zimmermann", 10022),
    #("Christian Schwarz", 10023),
    #("Melanie Mayer", 10024),
    #("Alexander Schröder", 10025),
    #("Birgit Werner", 10026),
    #("Patrick Schulz", 10027),
    #("Vanessa Hartmann", 10028),
    #("Fabian Kaiser", 10029),
    #("Miriam Köster", 10030)
]







# Erstelle für jeden Eintrag ein neues PDF
for i, (name, stammnummer) in enumerate(namen_und_stammnummern):
    output_pdf = f'output_{i+1}.pdf'
    add_text_to_pdf(template_pdf, name, stammnummer, output_pdf)
