# --- price_list_generator.py ---
from pathlib import Path
from typing import List, Optional

# Conditional imports... (keep as they are)
try:
    from log import CustomLogger
except ImportError:
    CustomLogger = None  # type: ignore
try:
    from objects import FleatMarket, Article
except ImportError:
    class FleatMarket:
        def get_main_number_list(self): return []

        class Article:
            def is_valid(self): return False
            def number(self): return "0"
            def price(self): return "0.0"
try:
    from src.display import ProgressTrackerAbstraction
except ImportError:
    ProgressTrackerAbstraction = None  # type: ignore
try:
    from src.display import OutputInterfaceAbstraction  # Added
except ImportError:
    OutputInterfaceAbstraction = None  # type: ignore # Added

from .data_generator import DataGenerator


class PriceListGenerator(DataGenerator):
    """ Generates price lists ('preisliste.dat'), using optional logging and output interface. """

    FILE_SUFFIX = 'dat'

    def __init__(self,
                 fleat_market_data: FleatMarket,
                 path: str = '',
                 file_name: str = 'preisliste',
                 logger: Optional[CustomLogger] = None,
                 output_interface: Optional[OutputInterfaceAbstraction] = None) -> None:  # Added
        """ Initializes the PriceListGenerator with data, path, name, logger, and output interface. """
        super().__init__(path, file_name, logger, output_interface)  # Pass logger and output_interface
        self.__fleat_market_data = fleat_market_data
        # self.logger and self.output_interface are now inherited from DataGenerator

    def __create_entry(self, main_number: str, article_number: str, price: str) -> str:
        """ Creates a formatted entry: main_number[0]article_number,price """
        # Warnings here are likely relevant to the user if they indicate bad data
        try:
            num = int(article_number)
            if 0 <= num < 10:
                article_number_formatted = f'0{num}'
            elif num >= 10:
                article_number_formatted = str(num)
            else:
                # Use _output_and_log for warnings that might affect output
                self._output_and_log(
                    "WARNING", f"Ungültige Artikelnummer '{article_number}' für Hauptnummer {main_number}. Verwende 'XX'.")
                article_number_formatted = "XX"
        except ValueError:
            self._output_and_log(
                "WARNING", f"Nicht-numerische Artikelnummer '{article_number}' für Hauptnummer {main_number}. Verwende 'XX'.")
            article_number_formatted = "XX"

        main_number_formatted = str(main_number).strip()
        price_formatted = str(price).strip().replace(',', '.')

        return f'{main_number_formatted}{article_number_formatted},{price_formatted}\n'

    # Overload write method from base class if specific behavior is needed
    def write(self, output_data: List[str]):
        """ Writes the generated price list entries to the file. """
        if not output_data:
            # This is informational, good for both log and user output
            self._output_and_log("INFO", "Keine gültigen Preislisten-Einträge zum Schreiben vorhanden.")
            return

        full_path = self.get_full_path()  # get_full_path already logs errors if needed
        try:
            full_path.parent.mkdir(parents=True, exist_ok=True)
            with open(full_path, 'w', encoding='utf-8') as file:
                file.writelines(output_data)
            # Success message is important for the user
            self._output_and_log("INFO", f"Preisliste erfolgreich geschrieben: {full_path}")
        except IOError as e:
            # Errors are critical for the user
            self._output_and_log("ERROR", f"Fehler beim Schreiben der Preisliste nach {full_path}: {e}")
        except Exception as e:
            self._output_and_log("ERROR", f"Unerwarteter Fehler beim Schreiben der Preisliste: {e}")

    def generate(self, overall_tracker: Optional[ProgressTrackerAbstraction] = None):
        """
        Generates the price list, writes it, and updates the tracker.
        Uses the logger and output interface passed during initialization.
        """
        # Start message for user and log
        self._output_and_log("INFO", f"Starte Generierung der Preisliste ({self.file_name}.{self.FILE_SUFFIX})...")
        output_data: List[str] = []
        generated_count = 0
        skipped_count = 0

        try:
            all_main_numbers_data = self.__fleat_market_data.get_main_number_list()
        except AttributeError:
            # Critical error, inform user and log
            err_msg = "FleatMarket Objekt hat keine Methode 'get_main_number_list'. Breche Preislisten-Generierung ab."
            self._output_and_log("ERROR", err_msg)
            if overall_tracker and isinstance(overall_tracker, ProgressTrackerAbstraction):
                overall_tracker.set_error(AttributeError("Fehlende Methode in FleatMarket"))
                overall_tracker.increment()
            return
        except Exception as e:
            # Other critical errors during data fetch
            err_msg = f"Fehler beim Abrufen der Hauptnummern-Daten: {e}"
            self._output_and_log("ERROR", err_msg)
            if overall_tracker and isinstance(overall_tracker, ProgressTrackerAbstraction):
                overall_tracker.set_error(e)
                overall_tracker.increment()
            return

        for main_number_data in all_main_numbers_data:
            # Basic validation warnings - might be less critical for end-user, depends on context
            # Keep using _log for these potentially numerous warnings, unless specifically needed by user.
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
                    # This indicates a more significant data structure issue
                    self._output_and_log(
                        "WARNING", f"Ungültige Artikelliste für Hauptnummer {main_number_str}. Übersprungen.")
                    skipped_count += 1
                    continue

                for article in articles:
                    # Similar to main_number_data, keep as _log unless specifically important
                    if not all([hasattr(article, 'is_valid'),
                                hasattr(article, 'number'),
                                hasattr(article, 'price')]):
                        self._log(
                            "WARNING", f"Unerwartetes Artikelobjekt für Hauptnummer {main_number_str}. Übersprungen.")
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
                            # Errors during processing are important
                            self._output_and_log(
                                "ERROR", f"Fehler bei Verarbeitung von Artikel für Hauptnummer {main_number_str}: {e}")
                            skipped_count += 1
                    else:
                        # Skipping invalid articles is normal, maybe just log? Or output if count is high?
                        # Let's keep it as _log for now to avoid too much output.
                        # self._log("DEBUG", f"Überspringe ungültigen Artikel für Hauptnummer {main_number_str}.")
                        skipped_count += 1
            else:
                # Skipping invalid main numbers is also expected behavior
                # self._log("DEBUG", f"Überspringe ungültige Hauptnummer {main_number_data.get_main_number()}.")
                skipped_count += 1

        # Final summary is important for the user
        self._output_and_log(
            "INFO", f"Preislisten-Generierung: {generated_count} Einträge erstellt, {skipped_count} übersprungen.")
        self.write(output_data)  # write method handles its own output/logging

        # Progress tracker update confirmation - internal, just log
        if overall_tracker and isinstance(overall_tracker, ProgressTrackerAbstraction):
            overall_tracker.increment()
            self._log("DEBUG", "Overall tracker incremented for PriceListGenerator.")
        elif overall_tracker:
            # This warning about the tracker itself is relevant
            self._output_and_log("WARNING", "overall_tracker wurde übergeben, ist aber kein ProgressTrackerInterface.")
