import argparse
from version import get_version



def Arguments():
    """Parses command line arguments with detailed help strings."""
    prog_name = '%(prog)s' # argparse ersetzt %(prog)s automatisch

    # Kurze Beschreibung für den Anfang der Hilfe
    main_description = f"Generiert Flohmarkt-Ausgabedateien (DAT, PDF) aus einer JSON-Datei."

    # Kürzerer Epilog, da Details in den Argument-Hilfen stehen
    examples_epilog = f"""
EXAMPLES:

  1. Basic usage (output in current directory):
     {prog_name} -f data/markt_daten.json

  2. Specify output directory:
     {prog_name} -f C:\\Daten\\markt_daten.json -p output_files

  3. Custom PDF template and output name:
     {prog_name} -f input.json --pdf-template templates/layout.pdf --pdf-output Confirmations.pdf

  4. Custom DAT filenames into 'results' folder:
     {prog_name} -f input.json -p results --seller-filename Sellers_M1 --price-filename Prices_M1

  5. Enable verbose/debug output:
     {prog_name} -f input.json -v

  6. Show only warnings and errors on console:
     {prog_name} -f input.json -l WARNING
--------------------------------------------------
"""

    parser = argparse.ArgumentParser(
        prog=prog_name,
        description=main_description,
        epilog=examples_epilog,
        formatter_class=argparse.RawTextHelpFormatter # RawText für Zeilenumbrüche in help/epilog
    )

    # Argumente mit detaillierteren help-Strings hinzufügen
    parser.add_argument(
        "-f", "--file",
        required=False,
        metavar='<path/to/file.json>', # Zeigt an, wie der Wert aussehen soll
        help="REQUIRED WITH CLI: Specifies the full path to the input JSON file.\n"
             "This file must contain all seller and article data according\n"
             "to the expected format for the program to function."
    )
    parser.add_argument(
        "-p", "--path",
        required=False,
        default='',
        metavar='<output/directory>',
        help="Optional: Specifies the directory where all generated output files\n"
             "(.dat files, .pdf file) will be saved. If omitted, files are\n"
             "saved in the current working directory (where the script is run)."
    )
    parser.add_argument(
        "-v", "--verbose",
        action='store_true',
        required=False,
        help="Optional: Enables detailed console output (DEBUG log level).\n"
             "Primarily intended for troubleshooting, as it shows many internal\n"
             "steps. This option overrides the '--log-level' setting."
    )
    parser.add_argument(
        "-V", "--version",
        action='version',
        version=f"{prog_name} {get_version()}",
        help="Shows the program's version number and exits immediately." # Standard help für version
    )
    parser.add_argument(
        '-l', '--log-level',
        choices=['INFO', 'WARNING', 'DEBUG', 'ERROR'],
        default='INFO',
        required=False,
        metavar='{INFO|WARNING|DEBUG|ERROR}',
        help="Optional: Sets the minimum log level for messages displayed on the\n"
             "console (e.g., INFO, WARNING, ERROR, DEBUG). Does not necessarily\n"
             "affect file logging if configured separately.\n"
             "Default: INFO. Overridden by --verbose (which sets DEBUG)."
    )
    parser.add_argument(
        '--pdf-template',
        default='Abholung_Template.pdf',
        required=False,
        metavar='<path/to/template.pdf>',
        help="Optional: Path to an *existing* PDF file to be used as the background\n"
             "or template for generated receive confirmations. Seller data will be\n"
             "merged onto this template.\n"
             "Default: 'Abholung_Template.pdf' (searched in current directory)."
    )
    parser.add_argument(
        '--pdf-output',
        default='Abholung.pdf',
        required=False,
        metavar='<output_filename.pdf>',
        help="Optional: Filename (including .pdf extension) for the *generated* PDF file\n"
             "containing the receive confirmations. This file will be saved in the\n"
             "output directory specified by -p (or current dir if -p is omitted).\n"
             "Default: 'Abholung.pdf'"
    )
    parser.add_argument(
        '--seller-filename',
        default='kundendaten',
        required=False,
        metavar='<base_name>',
        help="Optional: Sets the base filename (WITHOUT the .dat extension) for the\n"
             "seller accounting data file. The '.dat' extension is appended automatically.\n"
             "Default: 'kundendaten' (generates 'kundendaten.dat')."
    )
    parser.add_argument(
        '--price-filename',
        default='preisliste',
        required=False,
        metavar='<base_name>',
        help="Optional: Sets the base filename (WITHOUT the .dat extension) for the\n"
             "price list file. The '.dat' extension is appended automatically.\n"
             "Default: 'preisliste' (generates 'preisliste.dat')."
    )
    parser.add_argument(
        '--stats-filename',
        default='versand',
        required=False,
        metavar='<base_name>',
        help="Optional: Sets the base filename (WITHOUT the .dat extension) for the\n"
             "statistics data file. The '.dat' extension is appended automatically.\n"
             "Default: 'versand' (generates 'versand.dat')."
    )

    return parser.parse_args()
