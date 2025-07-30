from pypdf import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
import io
import threading
import time
import sys

def add_text_to_pdf(template_pdf, namen_und_stammnummern, output_pdf, progress):
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
    with open(output_pdf, "wb") as output:
        writer.write(output)

def thread_function(template_pdf, namen_und_stammnummern, output_pdf, progress):
    add_text_to_pdf(template_pdf, namen_und_stammnummern, output_pdf, progress)

def print_progress_bar(percentage, length=50):
    filled_length = int(length * percentage // 100)
    bar = '#' * filled_length + '-' * (length - filled_length)
    print(f'\rProgress: |{bar}| {percentage}% Complete', end='')

# Paths to the files
template_pdf = 'data\\Unterlagen\\Abholung\\Abholung_Template.pdf'
output_pdf = 'output.pdf'

namen_und_stammnummern = [
    ("Mustermann Max", 10001),
    ("Musterfrau Erika", 10002),
    ("Meier Hans", 10003),
    ("Schmidt Anna", 10004),
    ("Müller Peter", 10005),
    ("Fischer Julia", 10006),
    ("Weber Stefan", 10007),
    ("Wagner Laura", 10008),
    ("Becker Michael", 10009),
    ("Richter Nina", 10010),
    ("Hoffmann Thomas", 10011),
    ("Schäfer Claudia", 10012),
    ("Köhler Martin", 10013),
    ("Lehmann Susanne", 10014),
    ("Wolf Daniel", 10015),
    ("Jung Katharina", 10016),
    ("Klein Markus", 10017),
    ("Braun Carolin", 10018),
    ("Krüger Tobias", 10019),
    ("Vogel Sabine", 10020),
    ("Neumann Oliver", 10021),
    ("Zimmermann Sandra", 10022),
    ("Schwarz Christian", 10023),
    ("Mayer Melanie", 10024),
    ("Schröder Alexander", 10025),
    ("Werner Birgit", 10026),
    ("Schulz Patrick", 10027),
    ("Hartmann Vanessa", 10028),
    ("Kaiser Fabian", 10029),
    ("Köster Miriam", 10030),
    # Zusätzliche zufällige Einträge
    ("Schmidt Luca", 10031),
    ("Schneider Mia", 10032),
    ("Fischer Noah", 10033),
    ("Weber Emma", 10034),
    ("Meyer Leon", 10035),
    ("Wagner Sophia", 10036),
    ("Becker Elias", 10037),
    ("Schulz Hannah", 10038),
    ("Hoffmann Finn", 10039),
    ("Schäfer Marie", 10040),
    ("Koch Ben", 10041),
    ("Bauer Emilia", 10042),
    ("Richter Jonas", 10043),
    ("Klein Lina", 10044),
    ("Wolf Luis", 10045),
    ("Schröder Leonie", 10046),
    ("Neumann Paul", 10047),
    ("Schwarz Anna", 10048),
    ("Zimmermann Henry", 10049),
    ("Braun Emily", 10050),
    ("Krüger Felix", 10051),
    ("Hofmann Laura", 10052),
    ("Hartmann Maximilian", 10053),
    ("Lange Lara", 10054),
    ("Schmitt Theo", 10055),
    ("Werner Sofia", 10056),
    ("Schmitz Julian", 10057),
    ("Krause Clara", 10058),
    ("Meier David", 10059),
    ("Lehmann Mila", 10060),
    ("Schmid Moritz", 10061),
    ("Schulze Luisa", 10062),
    ("Maier Anton", 10063),
    ("Köhler Leni", 10064),
    ("Herrmann Jakob", 10065),
    ("König Amelie", 10066),
    ("Walter Emil", 10067),
    ("Müller Sophie", 10068),
    ("Peters Samuel", 10069),
    ("Lang Charlotte", 10070),
    ("Weiß Oskar", 10071),
    ("Jung Leah", 10072),
    ("Kaiser Erik", 10073),
    ("Fuchs Greta", 10074),
    ("Scholz Linus", 10075),
    ("Möller Johanna", 10076),
    ("Weber Matteo", 10077),
    ("Sauer Nora", 10078),
    ("Vogel Leo", 10079),
    ("Stein Isabella", 10080),
    ("Jäger Niklas", 10081),
    ("Otto Maya", 10082),
    ("Sommer Johann", 10083),
    ("Groß Lilly", 10084),
    ("Seidel Alexander", 10085),
    ("Heinrich Alina", 10086),
    ("Brandt Philipp", 10087),
    ("Haas Paula", 10088),
    ("Schreiber Mats", 10089),
    ("Graf Fiona", 10090),
    ("Dietrich Leonard", 10091),
    ("Ziegler Jana", 10092),
    ("Kuhn Simon", 10093),
    ("Kramer Isabell", 10094),
    ("Böhm Adam", 10095),
    ("Simon Elena", 10096),
    ("Franke Jonathan", 10097),
    ("Albrecht Sara", 10098),
    ("Winter Julius", 10099),
    ("Ludwig Marlene", 10100),
    ("Hein Karl", 10101),
    ("Schumacher Pia", 10102),
    ("Kraus Benno", 10103),
    ("Bauer Elisa", 10104),
    ("Binder Tim", 10105),
    ("Busch Anni", 10106),
    ("Berger Milan", 10107),
    ("Horn Helena", 10108),
    ("Thomas Fabian", 10109),
    ("Pohl Rosa", 10110),
    ("Reuter Till", 10111),
    ("Voigt Lara", 10112),
    ("Günther Sebastian", 10113),
    ("Schäfer Lena", 10114),
    ("Arnold Daniel", 10115),
    ("Bach Lilli", 10116),
    ("Marx Benedikt", 10117),
    ("Kraft Ella", 10118),
    ("Gärtner Christian", 10119),
    ("Hahn Katharina", 10120),
    ("Keller Florian", 10121),
    ("Roth Victoria", 10122),
    ("Friedrich Oliver", 10123),
    ("Lindner Eva", 10124),
    ("Schultz Dominik", 10125),
    ("Hübner Frida", 10126),
    ("Schmidt Lukas", 10127),
    ("Schneider Emilie", 10128),
    ("Fischer Marlon", 10129),
    ("Weber Sina", 10130),
    ("Meyer Fabio", 10131),
    ("Wagner Amelie", 10132),
    ("Becker Tobias", 10133),
    ("Schulz Nina", 10134),
    ("Hoffmann Jonah", 10135),
    ("Schäfer Lisa", 10136),
    ("Koch Bastian", 10137),
    ("Bauer Nele", 10138),
    ("Richter Jannik", 10139),
    ("Klein Jule", 10140),
    ("Wolf Tom", 10141),
    ("Schröder Lara", 10142),
    ("Neumann Aaron", 10143),
    ("Schwarz Paula", 10144),
    ("Zimmermann Nicolas", 10145),
    ("Braun Jasmin", 10146),
    ("Krüger Mattis", 10147),
    ("Hofmann Lena", 10148),
    ("Hartmann Lennard", 10149),
    ("Lange Lea", 10150),
    ("Schmitt Nils", 10151),
    ("Werner Emily", 10152),
    ("Schmitz Benjamin", 10153),
    ("Krause Johanna", 10154),
    ("Meier Jasper", 10155),
    ("Lehmann Melina", 10156),
    ("Schmid Jannis", 10157),
    ("Schulze Maya", 10158),
    ("Maier Max", 10159),
    ("Köhler Kira", 10160),
    ("Herrmann Levi", 10161),
    ("König Clara", 10162),
    ("Walter Henry", 10163),
    ("Müller Pauline", 10164),
    ("Peters Linus", 10165),
    ("Lang Fiona", 10166),
    ("Weiß Lasse", 10167),
    ("Jung Mira", 10168),
    ("Kaiser Jan", 10169),
    ("Fuchs Sofia", 10170),
    ("Scholz David", 10171),
    ("Möller Lilly", 10172),
    ("Weber Felix", 10173),
    ("Sauer Lia", 10174),
    ("Vogel Oscar", 10175),
    ("Stein Hannah", 10176),
    ("Jäger Leonard", 10177),
    ("Otto Emily", 10178),
    ("Sommer Leo", 10179),
    ("Groß Anna", 10180),
    ("Seidel Luis", 10181),
    ("Heinrich Mila", 10182),
    ("Brandt Philipp", 10183),
    ("Haas Charlotte", 10184),
    ("Schreiber Emil", 10185),
    ("Graf Elena", 10186),
    ("Dietrich Samuel", 10187),
    ("Ziegler Marie", 10188),
    ("Kuhn Alexander", 10189),
    ("Kramer Lina", 10190),
    ("Böhm Theodor", 10191),
    ("Simon Isabell", 10192),
    ("Franke Jakob", 10193),
    ("Albrecht Leni", 10194),
    ("Winter Moritz", 10195),
    ("Ludwig Alina", 10196),
    ("Hein Anton", 10197),
    ("Schumacher Greta", 10198),
    ("Kraus Levi", 10199),
    ("Bauer Emma", 10200),
    ("Binder Oskar", 10201),
    ("Busch Nora", 10202),
    ("Berger Paul", 10203),
    ("Horn Jana", 10204),
    ("Thomas Felix", 10205),
    ("Pohl Mia", 10206),
    ("Reuter Noah", 10207),
    ("Voigt Lea", 10208),
    ("Günther Ben", 10209),
    ("Schäfer Sophia", 10210),
    ("Arnold Elias", 10211),
    ("Bach Hannah", 10212),
    ("Marx Jonas", 10213),
    ("Kraft Lina", 10214),
    ("Gärtner Luis", 10215),
    ("Hahn Leonie", 10216),
    ("Keller Paulina", 10217),
    ("Roth Henry", 10218),
    ("Friedrich Emily", 10219),
    ("Lindner Maximilian", 10220),
    ("Schultz Lara", 10221),
    ("Hübner Theo", 10222),
    ("Schmidt Sofia", 10223),
    ("Schneider Julian", 10224),
    ("Fischer Clara", 10225),
    ("Weber David", 10226),
    ("Meyer Mila", 10227),
    ("Wagner Emil", 10228),
    ("Becker Sophie", 10229),
    ("Schulz Samuel", 10230),
    ("Hoffmann Charlotte", 10231),
    ("Schäfer Oskar", 10232),
    ("Koch Leah", 10233),
    ("Bauer Erik", 10234),
    ("Richter Greta", 10235),
    ("Klein Linus", 10236),
    ("Wolf Johanna", 10237),
    ("Schröder Matteo", 10238),
    ("Neumann Nora", 10239),
    ("Schwarz Leo", 10240),
    ("Zimmermann Isabella", 10241),
    ("Braun Niklas", 10242),
    ("Krüger Maya", 10243),
    ("Hofmann Johann", 10244),
    ("Hartmann Lilly", 10245),
    ("Lange Alexander", 10246),
    ("Schmitt Alina", 10247),
    ("Werner Philipp", 10248),
    ("Schmitz Paula", 10249),
    ("Krause Mats", 10250),
    ("Meier Fiona", 10251),
    ("Lehmann Leonard", 10252),
    ("Schmid Jana", 10253),
    ("Schulze Simon", 10254),
    ("Maier Isabell", 10255),
    ("Köhler Adam", 10256),
    ("Herrmann Elena", 10257),
    ("König Jonathan", 10258),
    ("Walter Sara", 10259),
    ("Müller Julius", 10260),
    ("Peters Marlene", 10261),
    ("Lang Karl", 10262),
    ("Weiß Pia", 10263),
    ("Jung Benno", 10264),
    ("Kaiser Elisa", 10265),
    ("Fuchs Tim", 10266),
    ("Scholz Anni", 10267),
    ("Möller Milan", 10268),
    ("Weber Helena", 10269),
    ("Sauer Fabian", 10270),
    ("Vogel Rosa", 10271),
    ("Stein Till", 10272),
    ("Jäger Lara", 10273),
    ("Otto Sebastian", 10274),
    ("Sommer Lena", 10275),
    ("Groß Daniel", 10276),
    ("Seidel Lilli", 10277),
    ("Heinrich Benedikt", 10278),
    ("Brandt Ella", 10279),
    ("Haas Christian", 10280),
    ("Schreiber Katharina", 10281),
    ("Graf Florian", 10282),
    ("Dietrich Victoria", 10283),
    ("Ziegler Oliver", 10284),
    ("Kuhn Eva", 10285),
    ("Kramer Dominik", 10286),
    ("Böhm Frida", 10287),
    ("Simon Lukas", 10288),
    ("Franke Emilie", 10289),
    ("Albrecht Marlon", 10290),
    ("Winter Sina", 10291),
    ("Ludwig Fabio", 10292),
    ("Hein Amelie", 10293),
    ("Schumacher Tobias", 10294),
    ("Kraus Nina", 10295),
    ("Bauer Jonah", 10296),
    ("Binder Lisa", 10297),
    ("Busch Bastian", 10298),
    ("Berger Nele", 10299),
    ("Horn Jannik", 10300),
    ("Thomas Jule", 10301),
    ("Pohl Tom", 10302),
    ("Reuter Lara", 10303),
    ("Voigt Aaron", 10304),
    ("Günther Paula", 10305),
    ("Schäfer Nicolas", 10306),
    ("Arnold Jasmin", 10307),
    ("Bach Mattis", 10308),
    ("Marx Lena", 10309),
    ("Kraft Lennard", 10310),
    ("Gärtner Lea", 10311),
    ("Hahn Nils", 10312),
    ("Keller Emily", 10313),
    ("Roth Benjamin", 10314),
    ("Friedrich Johanna", 10315),
    ("Lindner Jasper", 10316),
    ("Schultz Melina", 10317),
    ("Hübner Jannis", 10318),
    ("Schmidt Maya", 10319),
    ("Schulz Max", 10320),
    ("Fischer Kira", 10321),
    ("Weber Levi", 10322),
    ("Meyer Clara", 10323),
    ("Wagner Henry", 10324),
    ("Becker Pauline", 10325),
    ("Schulz Linus", 10326),
    ("Hoffmann Fiona", 10327),
    ("Schäfer Lasse", 10328),
    ("Koch Mira", 10329),
    ("Bauer Jan", 10330),
    ("Richter Sofia", 10331),
    ("Klein David", 10332),
    ("Wolf Lilly", 10333),
    ("Schröder Felix", 10334),
    ("Neumann Lia", 10335),
    ("Schwarz Oscar", 10336),
    ("Zimmermann Hannah", 10337),
    ("Braun Leonard", 10338),
    ("Krüger Emily", 10339),
    ("Hofmann Leo", 10340),
    ("Hartmann Anna", 10341),
    ("Lange Luis", 10342),
    ("Schmitt Mila", 10343),
    ("Werner Philipp", 10344),
    ("Schmitz Charlotte", 10345),
    ("Krause Emil", 10346),
    ("Meier Elena", 10347),
    ("Lehmann Samuel", 10348),
    ("Schmid Marie", 10349),
    ("Schulze Alexander", 10350),
    ("Maier Lina", 10351),
    ("Köhler Theodor", 10352),
    ("Herrmann Isabell", 10353),
    ("König Jakob", 10354),
    ("Walter Leni", 10355),
    ("Müller Moritz", 10356),
    ("Peters Alina", 10357),
    ("Lang Anton", 10358),
    ("Weiß Greta", 10359),
    ("Jung Levi", 10360),
    ("Kaiser Emma", 10361),
    ("Fuchs Oskar", 10362),
    ("Scholz Nora", 10363),
    ("Weber Paul", 10364),
    ("Sauer Jana", 10365),
    ("Vogel Felix", 10366),
    ("Stein Mia", 10367),
    ("Jäger Noah", 10368),
    ("Otto Lea", 10369),
    ("Sommer Ben", 10370),
    ("Groß Sophia", 10371),
    ("Seidel Elias", 10372),
    ("Heinrich Hannah", 10373),
    ("Brandt Jonas", 10374),
    ("Haas Lina", 10375),
    ("Schreiber Luis", 10376),
    ("Graf Leonie", 10377),
    ("Dietrich Paulina", 10378),
    ("Ziegler Henry", 10379),
    ("Kuhn Emily", 10380),
    ("Kramer Maximilian", 10381),
    ("Böhm Lara", 10382),
    ("Simon Theo", 10383),
    ("Franke Sofia", 10384),
    ("Albrecht Julian", 10385),
    ("Winter Clara", 10386),
    ("Ludwig David", 10387),
    ("Hein Mila", 10388),
    ("Schumacher Emil", 10389),
    ("Kraus Sophie", 10390),
    ("Bauer Samuel", 10391),
    ("Binder Charlotte", 10392),
    ("Busch Oskar", 10393),
    ("Berger Leah", 10394),
    ("Horn Erik", 10395),
    ("Thomas Greta", 10396),
    ("Pohl Linus", 10397),
    ("Reuter Johanna", 10398),
    ("Voigt Matteo", 10399),
    ("Günther Nora", 10400)
]


# Shared progress variable
progress = {
    'lock': threading.Lock(),
    'current': 0,
    'percentage': 0
}

namen_und_stammnummern.sort(key=lambda x: x[0])
# Create and start the thread
thread = threading.Thread(target=thread_function, args=(template_pdf, namen_und_stammnummern, output_pdf, progress))
thread.start()

# Main thread: monitor progress
while thread.is_alive():
    with progress['lock']:
        percentage = progress['percentage']
    # Print ASCII progress bar
    print_progress_bar(percentage)
    time.sleep(0.1)

# Ensure the final progress is 100%
print_progress_bar(100)
print("\nProcessing complete!")
