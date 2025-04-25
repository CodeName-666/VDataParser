# --- seller_data_generator.py ---
from pathlib import Path
from typing import List, Optional
import time  # Keep for potential delays if needed, but logging is primary now

# Conditional import of CustomLogger
try:
    from log import CustomLogger
except ImportError:
    CustomLogger = None  # type: ignore

# Assume objects and ProgressTracker are available
try:
    from objects import FleatMarket, Seller  # Adjust names as per your project
except ImportError:
    class FleatMarket:
        def get_main_number_list(self): return []
        def get_seller_data(i): return Seller()

    class Seller:
        vorname = "Dummy"
        nachname = "Dummy"
try:
    from .progress_tracker import ProgressTracker
except ImportError:
    ProgressTracker = None  # type: ignore

from .data_generator import DataGenerator


class SellerDataGenerator(DataGenerator):
    """ Generates seller data ('kundendaten.dat'), using optional logging. """

    FILE_SUFFIX = 'dat'

    def __init__(self,
                 fleat_market_data: FleatMarket,
                 path: str = '',
                 file_name: str = 'kundendaten',
                 logger: Optional[CustomLogger] = None) -> None:
        """ Initializes the SellerDataGenerator with data, path, name, and logger. """
        super().__init__(path, file_name, logger)  # Pass logger to base class
        self.__fleat_market_data = fleat_market_data
        # self.logger inherited

    def __create_entry(self, main_number: int, article_quantity: int, article_total_value: float) -> str:
        """ Creates a formatted entry: "main_number","B",quantity,total_value """
        # Format as required by the target system
        # Example: Comma decimal
        return f'"{main_number}","B",{article_quantity},{article_total_value:.2f}\n'.replace('.', ',')

    def write(self, output_data: List[str]):
        """ Writes the generated seller data entries to the file. """
        if not output_data:
            self._log("INFO", "Keine Verkäuferdaten zum Schreiben vorhanden.")
            return
        full_path = self.get_full_path()
        try:
            full_path.parent.mkdir(parents=True, exist_ok=True)
            with open(full_path, 'w', encoding='utf-8') as file:
                file.writelines(output_data)
            self._log(
                "INFO", f"Verkäuferdaten erfolgreich geschrieben: {full_path}")
        except IOError as e:
            self._log(
                "ERROR", f"Fehler beim Schreiben der Verkäuferdaten nach {full_path}: {e}")
        except Exception as e:
            self._log(
                "ERROR", f"Unerwarteter Fehler beim Schreiben der Verkäuferdaten: {e}")

    def generate(self, overall_tracker: Optional[ProgressTracker] = None):
        """ Generates seller data, logs, writes, and updates tracker. """
        self._log("INFO", f"Starte Erstellung der Verkäuferliste ({self.file_name}.{self.FILE_SUFFIX}):\n" +
                  "      ========================")
        output_data: List[str] = []
        valid_cnt = 0
        invalid_cnt = 0
        processed_count = 0

        try:
            all_main_numbers_data = self.__fleat_market_data.get_main_number_list()
            total_items = len(all_main_numbers_data)
        except AttributeError:
            self._log(
                "ERROR", "FleatMarket Objekt hat keine Methode 'get_main_number_list'. Breche ab.")
            if overall_tracker and isinstance(overall_tracker, ProgressTracker):
                overall_tracker.set_error(AttributeError(
                    "Fehlende Methode in FleatMarket"))
                overall_tracker.increment()
            return
        except Exception as e:
            self._log(
                "ERROR", f"Fehler beim Abrufen der Hauptnummern-Daten: {e}")
            if overall_tracker and isinstance(overall_tracker, ProgressTracker):
                overall_tracker.set_error(e)
                overall_tracker.increment()
            return

        for index, main_number_data in enumerate(all_main_numbers_data):
            processed_count += 1
            self._log(
                "DEBUG", f"Verarbeite Verkäufer-Eintrag {processed_count}/{total_items}...")

            if not all([hasattr(main_number_data, 'is_valid'),
                        hasattr(main_number_data, 'get_main_number'),
                        hasattr(main_number_data, 'get_article_quantity'),
                        # Check name: get_article_total?
                        hasattr(main_number_data, 'get_article_total')]):
                self._log(
                    "WARNING", f"Unerwartetes Datenobjekt bei Index {index}. Übersprungen.")
                invalid_cnt += 1
                continue

            main_number_val = main_number_data.get_main_number()
            first_name, second_name = "Unbekannt", "Unbekannt"
            try:
                seller: Seller = self.__fleat_market_data.get_seller_data(
                    index)
                if hasattr(seller, 'vorname') and hasattr(seller, 'nachname'):
                    first_name = seller.vorname
                    second_name = seller.nachname
            except IndexError:
                self._log(
                    "ERROR", f"Kein Verkäufer für Index {index} (Hauptnummer {main_number_val}) gefunden.")
                invalid_cnt += 1
                continue  # Skip if seller missing
            except AttributeError:
                self._log(
                    "ERROR", "FleatMarket Objekt hat keine Methode 'get_seller_data'. Breche Schleife ab.")
                invalid_cnt += total_items - processed_count + 1
                if overall_tracker:
                    overall_tracker.set_error(
                        AttributeError("Missing get_seller_data"))
                break  # Abort loop
            except Exception as e:
                self._log(
                    "ERROR", f"Unerwarteter Fehler beim Holen von Verkäuferdaten für Index {index}: {e}")
                invalid_cnt += 1
                continue

            # Use logger's one-line feature example (optional)
            # if self.logger: self.logger.one_line_log("INFO", True)
            # self._log("INFO", f">> Prüfe Eintrag: {second_name}, {first_name} ({main_number_val})")

            if main_number_data.is_valid():
                try:
                    m_n = int(main_number_val)
                    a_q = int(main_number_data.get_article_quantity())
                    a_t_val = main_number_data.get_article_total()  # Adjust method name if needed
                    a_t = float(a_t_val) if a_t_val is not None else 0.0

                    entry = self.__create_entry(m_n, a_q, a_t)
                    output_data.append(entry)
                    valid_cnt += 1
                    self._log(
                        "DEBUG", f">> Verkäufer-Eintrag (OK): {first_name} {second_name}, MNr: {m_n}, Artikel: {a_q}, Wert: {a_t:.2f} EUR")
                except (ValueError, TypeError) as e:
                    self._log(
                        "ERROR", f"Datenkonvertierungsfehler für Hauptnummer {main_number_val}: {e}")
                    invalid_cnt += 1
                except Exception as e:
                    self._log(
                        "ERROR", f"Unerwarteter Fehler bei gültigem Eintrag {main_number_val}: {e}")
                    invalid_cnt += 1
            else:
                invalid_cnt += 1
                m_n_str = str(main_number_val)
                a_q_val = main_number_data.get_article_quantity()
                a_t_val = main_number_data.get_article_total()  # Adjust if needed
                a_q_str = str(a_q_val) if a_q_val is not None else "N/A"
                a_t_str = f"{float(a_t_val):.2f} EUR" if a_t_val is not None else "N/A"
                self._log(
                    "WARNING", f">> Verkäufer-Eintrag (UNGÜLTIG): {first_name} {second_name}, MNr: {m_n_str}, Artikel: {a_q_str}, Wert: {a_t_str}")

            # if self.logger: self.logger.one_line_log("INFO", False) # Finish one-line log
            # time.sleep(0.01) # Minimal delay if needed

        self.write(output_data)
        self._log("INFO", f"Verkäuferliste abgeschlossen: \n" +
                  "      ========================\n" +
                  f"          --> Gültige Einträge: {valid_cnt}\n" +
                  f"          --> Ungültige/Übersprungene Einträge: {invalid_cnt}\n")

        # Update tracker
        if overall_tracker and isinstance(overall_tracker, ProgressTracker):
            overall_tracker.increment()
        elif overall_tracker:
            self._log(
                "WARNING", "overall_tracker wurde übergeben, ist aber kein ProgressTracker.")
