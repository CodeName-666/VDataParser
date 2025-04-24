# --- price_list_generator.py ---
from pathlib import Path
from typing import List, Optional

# Conditional import of CustomLogger
try:
    from log import CustomLogger
except ImportError:
    CustomLogger = None # type: ignore

# Assume objects and ProgressTracker are available (handle imports as needed)
try:
    from objects import FleatMarket, Article # Adjust names as per your project
except ImportError:
    # Define dummy classes if objects.py is missing, to allow script parsing
    class FleatMarket: get_main_number_data_list = lambda self: []
    class Article: is_valid = lambda self: False; number = lambda self: "0"; price = lambda self: "0.0"
try:
    from .progress_tracker import ProgressTracker
except ImportError:
    ProgressTracker = None # type: ignore

from .data_generator import DataGenerator

class PriceListGenerator(DataGenerator):
    """ Generates price lists ('preisliste.dat'), using optional logging. """

    FILE_SUFFIX = 'dat'

    def __init__(self,
                 fleat_market_data: FleatMarket,
                 path: str = '',
                 file_name: str = 'preisliste',
                 logger: Optional[CustomLogger] = None) -> None:
        """ Initializes the PriceListGenerator with data, path, name, and logger. """
        super().__init__(path, file_name, logger) # Pass logger to base class
        self.__fleat_market_data = fleat_market_data
        # self.logger is now inherited from DataGenerator

    def __create_entry(self, main_number: str, article_number: str, price: str) -> str:
        """ Creates a formatted entry: main_number[0]article_number,price """
        try:
             num = int(article_number)
             if 0 <= num < 10:
                 article_number_formatted = f'0{num}'
             elif num >= 10:
                 article_number_formatted = str(num)
             else:
                  self._log("WARNING", f"Ungültige Artikelnummer '{article_number}' für Hauptnummer {main_number}. Verwende 'XX'.")
                  article_number_formatted = "XX"
        except ValueError:
             self._log("WARNING", f"Nicht-numerische Artikelnummer '{article_number}' für Hauptnummer {main_number}. Verwende 'XX'.")
             article_number_formatted = "XX"

        main_number_formatted = str(main_number).strip()
        price_formatted = str(price).strip().replace(',', '.')

        return f'{main_number_formatted}{article_number_formatted},{price_formatted}\n'

    # Overload write method from base class if specific behavior is needed
    def write(self, output_data: List[str]):
        """ Writes the generated price list entries to the file. """
        if not output_data:
            self._log("INFO", "Keine gültigen Preislisten-Einträge zum Schreiben vorhanden.")
            return

        full_path = self.get_full_path()
        try:
            full_path.parent.mkdir(parents=True, exist_ok=True)
            # Specify encoding for potentially non-ASCII characters in price/number? Unlikely but safe.
            with open(full_path, 'w', encoding='utf-8') as file:
                file.writelines(output_data)
            self._log("INFO", f"Preisliste erfolgreich geschrieben: {full_path}")
        except IOError as e:
            self._log("ERROR", f"Fehler beim Schreiben der Preisliste nach {full_path}: {e}")
        except Exception as e:
            self._log("ERROR", f"Unerwarteter Fehler beim Schreiben der Preisliste: {e}")


    def generate(self, overall_tracker: Optional[ProgressTracker] = None):
        """
        Generates the price list, writes it, and updates the tracker.
        Uses the logger passed during initialization (if any).
        """
        self._log("INFO", f"Starte Generierung der Preisliste ({self.file_name}.{self.FILE_SUFFIX})...")
        output_data: List[str] = []
        generated_count = 0
        skipped_count = 0

        try:
            all_main_numbers_data = self.__fleat_market_data.get_main_number_data_list()
        except AttributeError:
             self._log("ERROR","FleatMarket Objekt hat keine Methode 'get_main_number_data_list'. Breche Preislisten-Generierung ab.")
             if overall_tracker and isinstance(overall_tracker, ProgressTracker):
                 overall_tracker.set_error(AttributeError("Fehlende Methode in FleatMarket"))
                 overall_tracker.increment()
             return
        except Exception as e:
             self._log("ERROR", f"Fehler beim Abrufen der Hauptnummern-Daten: {e}")
             if overall_tracker and isinstance(overall_tracker, ProgressTracker):
                 overall_tracker.set_error(e)
                 overall_tracker.increment()
             return

        for main_number_data in all_main_numbers_data:
            # Basic validation of the data object structure
            if not all([hasattr(main_number_data, 'is_valid'),
                        hasattr(main_number_data, 'article_list'),
                        hasattr(main_number_data, 'get_main_number')]):
                 self._log("WARNING", "Unerwartetes Datenobjekt in Hauptnummernliste gefunden. Übersprungen.")
                 skipped_count += 1
                 continue

            if main_number_data.is_valid():
                main_number_str = str(main_number_data.get_main_number())
                articles = main_number_data.article_list

                if not isinstance(articles, list):
                     self._log("WARNING", f"Ungültige Artikelliste für Hauptnummer {main_number_str}. Übersprungen.")
                     skipped_count +=1
                     continue

                for article in articles:
                     if not all([hasattr(article, 'is_valid'),
                                 hasattr(article, 'number'),
                                 hasattr(article, 'price')]):
                          self._log("WARNING", f"Unerwartetes Artikelobjekt für Hauptnummer {main_number_str}. Übersprungen.")
                          skipped_count += 1
                          continue

                     if article.is_valid():
                         try:
                             a_n = article.number()
                             a_p = article.price()
                             entry = self.__create_entry(main_number_str, str(a_n), str(a_p))
                             if entry.strip():
                                 output_data.append(entry)
                                 generated_count += 1
                         except Exception as e:
                              self._log("ERROR", f"Fehler bei Verarbeitung von Artikel für Hauptnummer {main_number_str}: {e}")
                              skipped_count += 1
                     else:
                          skipped_count += 1
            else:
                 skipped_count += 1


        self._log("INFO", f"Preislisten-Generierung: {generated_count} Einträge erstellt, {skipped_count} übersprungen.")
        self.write(output_data) # Use the overloaded write method

        # Update tracker
        if overall_tracker and isinstance(overall_tracker, ProgressTracker):
            overall_tracker.increment()
        elif overall_tracker:
             self._log("WARNING", "overall_tracker wurde übergeben, ist aber kein ProgressTracker.")