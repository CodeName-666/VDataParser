# --- price_list_generator.py ---
from pathlib import Path
from typing import List, Optional

# Annahme: Benötigte Objekte sind in 'objects.py' und Logger in 'log.py'
try:
    from objects import FleatMarket, Article # Beispielnamen, bitte anpassen!
    from log import logger # Beispielnamen, bitte anpassen!
except ImportError:
    print("WARNUNG: Konnte 'objects' oder 'log' nicht importieren. Stellen Sie sicher, dass diese Module existieren.")
    # Dummy-Implementierungen für den Fall, dass die Module fehlen
    class FleatMarket:
        def get_main_number_data_list(self): return []
    class Article:
        def is_valid(self): return False
        def number(self): return "0"
        def price(self): return "0.00"
    class Logger:
        def info(self, msg): print(f"INFO: {msg}")
        def error(self, msg): print(f"ERROR: {msg}")
    logger = Logger()


from .data_generator import DataGenerator
# Annahme: ProgressTracker existiert im selben Verzeichnis oder im PYTHONPATH
try:
    from .progress_tracker import ProgressTracker
except ImportError:
    ProgressTracker = None


class PriceListGenerator(DataGenerator):
    """
    A class to generate price lists ('preisliste.dat') for a flea market.
    """

    FILE_SUFFIX = 'dat'

    def __init__(self, fleat_market_data: FleatMarket, path: str = '', file_name: str = 'preisliste') -> None:
        """
        Initializes the PriceListGenerator.

        Args:
            fleat_market_data: The flea market data object.
            path: The output directory path.
            file_name: The name of the output file (without suffix). Default is 'preisliste'.
        """
        super().__init__(path, file_name)
        self.__fleat_market_data = fleat_market_data

    def __create_entry(self, main_number: str, article_number: str, price: str) -> str:
        """ Creates a formatted entry: main_number[0]article_number,price """
        # Ensure article_number is two digits with leading zero if needed
        try:
             num = int(article_number)
             if 0 <= num < 10:
                 article_number_formatted = f'0{num}'
             elif num >= 10:
                 article_number_formatted = str(num)
             else:
                  # Handle negative or invalid numbers if necessary
                  logger.warning(f"Ungültige Artikelnummer '{article_number}' für Hauptnummer {main_number}. Übersprungen?")
                  # Decide how to handle: return empty string, raise error, or format differently
                  article_number_formatted = "XX" # Placeholder for invalid
        except ValueError:
             logger.warning(f"Nicht-numerische Artikelnummer '{article_number}' für Hauptnummer {main_number}. Übersprungen?")
             article_number_formatted = "XX" # Placeholder for invalid


        # Ensure main_number has the expected format (e.g., exactly 4 digits) - Adjust if needed
        main_number_formatted = str(main_number).strip()
        # if not (main_number_formatted.isdigit() and len(main_number_formatted) == 4):
        #      logger.warning(f"Ungültige Hauptnummer '{main_number_formatted}'.")
             # Decide handling

        # Ensure price has the expected format (e.g., "1.23") - Adjust if needed
        price_formatted = str(price).strip().replace(',', '.') # Ensure dot as decimal separator

        return f'{main_number_formatted}{article_number_formatted},{price_formatted}\n'

    def __write(self, output_data: List[str]):
        """ Writes the generated price list entries to the file. """
        if not output_data:
            logger.info("Keine gültigen Preislisten-Einträge zum Schreiben vorhanden.")
            return

        full_path = self.get_full_path()
        try:
            full_path.parent.mkdir(parents=True, exist_ok=True)
            with open(full_path, 'w', encoding='utf-8') as file: # Specify encoding
                file.writelines(output_data)
            logger.info(f"Preisliste erfolgreich geschrieben: {full_path}")
        except IOError as e:
            logger.error(f"Fehler beim Schreiben der Preisliste nach {full_path}: {e}")
            # Optional: Fehler an Tracker melden, falls einer übergeben wurde (hier nicht direkt möglich)
        except Exception as e:
            logger.error(f"Unerwarteter Fehler beim Schreiben der Preisliste: {e}")


    def generate(self, overall_tracker: Optional[ProgressTracker] = None):
        """
        Generates the price list from the flea market data and writes it to a file.
        Updates the overall progress tracker if provided.
        """
        logger.info(f"Starte Generierung der Preisliste ({self.file_name}.{self.FILE_SUFFIX})...")
        output_data: List[str] = []
        generated_count = 0
        skipped_count = 0

        try:
            all_main_numbers_data = self.__fleat_market_data.get_main_number_data_list()
        except AttributeError:
             logger.error("FleatMarket Objekt hat keine Methode 'get_main_number_data_list'. Breche Preislisten-Generierung ab.")
             if overall_tracker:
                 overall_tracker.set_error(AttributeError("Fehlende Methode in FleatMarket"))
                 overall_tracker.increment() # Zähle als erledigt (mit Fehler)
             return
        except Exception as e:
             logger.error(f"Fehler beim Abrufen der Hauptnummern-Daten: {e}")
             if overall_tracker:
                 overall_tracker.set_error(e)
                 overall_tracker.increment()
             return


        for main_number_data in all_main_numbers_data:
            # Prüfe, ob main_number_data die erwarteten Methoden hat
            if not all([hasattr(main_number_data, 'is_valid'),
                        hasattr(main_number_data, 'article_list'),
                        hasattr(main_number_data, 'get_main_number')]):
                 logger.warning("Unerwartetes Datenobjekt in Hauptnummernliste gefunden. Übersprungen.")
                 skipped_count += 1
                 continue

            if main_number_data.is_valid():
                main_number_str = str(main_number_data.get_main_number())
                articles = main_number_data.article_list

                if not isinstance(articles, list):
                     logger.warning(f"Ungültige Artikelliste für Hauptnummer {main_number_str}. Übersprungen.")
                     skipped_count +=1
                     continue

                for article in articles:
                     # Prüfe, ob article die erwarteten Methoden hat
                     if not all([hasattr(article, 'is_valid'),
                                 hasattr(article, 'number'),
                                 hasattr(article, 'price')]):
                          logger.warning(f"Unerwartetes Artikelobjekt für Hauptnummer {main_number_str}. Übersprungen.")
                          skipped_count += 1
                          continue

                     if article.is_valid():
                         try:
                             a_n = article.number() # Sollte String oder Int sein
                             a_p = article.price()  # Sollte String oder Float/Decimal sein
                             entry = self.__create_entry(main_number_str, str(a_n), str(a_p))
                             if entry.strip(): # Nur hinzufügen, wenn Eintrag nicht leer ist
                                 output_data.append(entry)
                                 generated_count += 1
                         except Exception as e:
                              logger.error(f"Fehler bei Verarbeitung von Artikel für Hauptnummer {main_number_str}: {e}")
                              skipped_count += 1
                     else:
                          # Optional: Loggen von ungültigen Artikeln
                          # logger.debug(f"Ungültiger Artikel für Hauptnummer {main_number_str} übersprungen.")
                          skipped_count += 1
            else:
                 # Optional: Loggen von ungültigen Hauptnummern
                 # logger.debug(f"Ungültige Hauptnummer {main_number_data.get_main_number()} übersprungen.")
                 skipped_count += 1


        logger.info(f"Preislisten-Generierung: {generated_count} Einträge erstellt, {skipped_count} übersprungen.")
        self.__write(output_data)

        # Melde Abschluss dieser Aufgabe an den Gesamt-Tracker
        if overall_tracker and isinstance(overall_tracker, ProgressTracker):
            overall_tracker.increment()
        elif overall_tracker:
             logger.warning("overall_tracker wurde übergeben, ist aber kein ProgressTracker.")