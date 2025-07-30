from pypdf import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
import io
import copy  # Import the copy module

def add_text_to_pdf(template_pdf, namen_und_stammnummern, output_pdf):
    # Read the template PDF
    #reader = PdfReader(template_pdf)
    writer = PdfWriter()

    # Process the names in groups of 4
    for i in range(0, len(namen_und_stammnummern), 4):
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

        # Positions for the 4 names and stammnummern
        positions = [
            (100, -105, 310, -105),  # x1, y1 for name, x2, y2 for stammnummer
            (507, -105, 712, -105),
            (100, -360, 310, -360),
            (507, -360, 712, -360)
        ]

        for idx, (name, stammnummer) in enumerate(group):
            x1, y1, x2, y2 = positions[idx]
            can.drawString(x1, y1, f"{name}")
            can.drawString(x2, y2, f"{stammnummer}")

        can.save()
        # Move to the beginning of the StringIO buffer
        packet.seek(0)
        new_pdf = PdfReader(packet)
        overlay_page = new_pdf.pages[0]

        # Merge the overlay with the page
        page.merge_page(overlay_page)

        # Add the page to the writer
        writer.add_page(page)

    # Save the new PDF
    with open(output_pdf, "wb") as output:
        writer.write(output)

# Paths to the files
template_pdf = 'data\\Unterlagen\\Abholung\\Abholung_Template.pdf'
output_pdf = 'output.pdf'

# The list of names and Stammnummern
namen_und_stammnummern = [
    ("Max Mustermann", 10001),
    ("Erika Musterfrau", 10002),
    ("Hans Meier", 10003),
    ("Anna Schmidt", 10004),
    ("Peter Müller", 10005),
    ("Julia Fischer", 10006),
    ("Stefan Weber", 10007),
    ("Laura Wagner", 10008),
    ("Michael Becker", 10009),
    ("Nina Richter", 10010),
    ("Thomas Hoffmann", 10011),
    ("Claudia Schäfer", 10012),
    ("Martin Köhler", 10013),
    ("Susanne Lehmann", 10014),
    ("Daniel Wolf", 10015),
    ("Katharina Jung", 10016),
    ("Markus Klein", 10017),
    ("Carolin Braun", 10018),
    ("Tobias Krüger", 10019),
    ("Sabine Vogel", 10020),
    ("Oliver Neumann", 10021),
    ("Sandra Zimmermann", 10022),
    ("Christian Schwarz", 10023),
    ("Melanie Mayer", 10024),
    ("Alexander Schröder", 10025),
    ("Birgit Werner", 10026),
    ("Patrick Schulz", 10027),
    ("Vanessa Hartmann", 10028),
    ("Fabian Kaiser", 10029),
    ("Miriam Köster", 10030)
]

# Call the function with the entire list
add_text_to_pdf(template_pdf, namen_und_stammnummern, output_pdf)