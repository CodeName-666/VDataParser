# --- seller_data_generator.py ---
from pathlib import Path
from typing import List, Optional
import time

# Conditional imports... (keep as they are)
try:
    from log import CustomLogger
except ImportError:
    CustomLogger = None
try:
    from objects import FleatMarket, Seller
except ImportError:
    class FleatMarket:
        def get_main_number_list(self): return []
        def get_seller_data(i): return Seller()

        class Seller:
            vorname = "Dummy"
            nachname = "Dummy"
try:
    from src.display import ProgressTrackerAbstraction
except ImportError:
    ProgressTrackerAbstraction = None
try:
    from src.display import OutputInterfaceAbstraction  # Added
except ImportError:
    OutputInterfaceAbstraction = None  # Added

from .data_generator import DataGenerator


class SellerDataGenerator(DataGenerator):
    """ Generates seller data ('kundendaten.dat'), using optional logging and output interface. """

    FILE_SUFFIX = 'dat'

    def __init__(self,
                 fleat_market_data: FleatMarket,
                 path: str = '',
                 file_name: str = 'kundendaten',
                 logger: Optional[CustomLogger] = None,
                 output_interface: Optional[OutputInterfaceAbstraction] = None) -> None:  # Added
        """ Initializes the SellerDataGenerator with data, path, name, logger, and output interface. """
        super().__init__(path, file_name, logger, output_interface)  # Pass both
        self.__fleat_market_data = fleat_market_data
        # self.logger, self.output_interface inherited

    def __create_entry(self, main_number: int, article_quantity: int, article_total_value: float) -> str:
        """ Creates a formatted entry: "main_number","B",quantity,total_value """
        return f'"{main_number}","B",{article_quantity},{article_total_value:.2f}\n'.replace('.', ',')

    def write(self, output_data: List[str]):
        """ Writes the generated seller data entries to the file. """
        if not output_data:
            # Inform user and log
            self._output_and_log("INFO", "Keine Verkäuferdaten zum Schreiben vorhanden.")
            return
        full_path = self.get_full_path()  # Handles its own errors
        try:
            full_path.parent.mkdir(parents=True, exist_ok=True)
            with open(full_path, 'w', encoding='utf-8') as file:
                file.writelines(output_data)
            # Success message for user
            self._output_and_log("INFO", f"Verkäuferdaten erfolgreich geschrieben: {full_path}")
        except IOError as e:
            # Critical errors for user
            self._output_and_log("ERROR", f"Fehler beim Schreiben der Verkäuferdaten nach {full_path}: {e}")
        except Exception as e:
            self._output_and_log("ERROR", f"Unerwarteter Fehler beim Schreiben der Verkäuferdaten: {e}")

    def generate(self, overall_tracker: Optional[ProgressTrackerAbstraction] = None):
        """ Generates seller data, logs, writes, and updates tracker. """
        # Start message for user
        self._output_and_log("INFO", f"Starte Erstellung der Verkäuferliste ({self.file_name}.{self.FILE_SUFFIX}):\n" +
                             "      ========================")
        output_data: List[str] = []
        valid_cnt = 0
        invalid_cnt = 0
        processed_count = 0

        try:
            all_main_numbers_data = self.__fleat_market_data.get_main_number_list()
            total_items = len(all_main_numbers_data)
        except AttributeError:
            # Critical error
            err_msg = "FleatMarket Objekt hat keine Methode 'get_main_number_list'. Breche ab."
            self._output_and_log("ERROR", err_msg)
            if overall_tracker and isinstance(overall_tracker, ProgressTrackerAbstraction):
                overall_tracker.set_error(AttributeError("Fehlende Methode in FleatMarket"))
                overall_tracker.increment()
            return
        except Exception as e:
            # Critical error
            err_msg = f"Fehler beim Abrufen der Hauptnummern-Daten: {e}"
            self._output_and_log("ERROR", err_msg)
            if overall_tracker and isinstance(overall_tracker, ProgressTrackerAbstraction):
                overall_tracker.set_error(e)
                overall_tracker.increment()
            return

        for index, main_number_data in enumerate(all_main_numbers_data):
            processed_count += 1
            # Progress update - use _log for frequent messages
            self._log("DEBUG", f"Verarbeite Verkäufer-Eintrag {processed_count}/{total_items}...")

            # Data structure checks - use _output_and_log for warnings about unexpected structure
            if not all([hasattr(main_number_data, 'is_valid'),
                        hasattr(main_number_data, 'get_main_number'),
                        hasattr(main_number_data, 'get_article_quantity'),
                        hasattr(main_number_data, 'get_article_total')]):  # Corrected check
                self._output_and_log("WARNING", f"Unerwartetes Datenobjekt bei Index {index}. Übersprungen.")
                invalid_cnt += 1
                continue

            main_number_val = main_number_data.get_main_number()
            first_name, second_name = "Unbekannt", "Unbekannt"
            try:
                seller: Seller = self.__fleat_market_data.get_seller_data(index)
                if hasattr(seller, 'vorname') and hasattr(seller, 'nachname'):
                    first_name = seller.vorname
                    second_name = seller.nachname
            except IndexError:
                # Error: Missing seller for a potentially valid entry
                self._output_and_log(
                    "ERROR", f"Kein Verkäufer für Index {index} (Hauptnummer {main_number_val}) gefunden. Übersprungen.")
                invalid_cnt += 1
                continue
            except AttributeError:
                # Critical error: Missing method on main data object
                err_msg = "FleatMarket Objekt hat keine Methode 'get_seller_data'. Breche Schleife ab."
                self._output_and_log("ERROR", err_msg)
                invalid_cnt += total_items - processed_count + 1
                if overall_tracker:
                    overall_tracker.set_error(AttributeError("Missing get_seller_data"))
                break
            except Exception as e:
                # Unexpected error fetching seller
                self._output_and_log(
                    "ERROR", f"Unerwarteter Fehler beim Holen von Verkäuferdaten für Index {index}: {e}. Übersprungen.")
                invalid_cnt += 1
                continue

            # Internal check logging
            # self._log("DEBUG", f">> Prüfe Eintrag: {second_name}, {first_name} ({main_number_val})")

            if main_number_data.is_valid():
                try:
                    m_n = int(main_number_val)
                    a_q = int(main_number_data.get_article_quantity())
                    a_t_val = main_number_data.get_article_total()
                    a_t = float(a_t_val) if a_t_val is not None else 0.0

                    entry = self.__create_entry(m_n, a_q, a_t)
                    output_data.append(entry)
                    valid_cnt += 1
                    # Log successful processing at DEBUG level
                    self._log(
                        "DEBUG", f">> Verkäufer-Eintrag (OK): {first_name} {second_name}, MNr: {m_n}, Artikel: {a_q}, Wert: {a_t:.2f} EUR")
                except (ValueError, TypeError) as e:
                    # Data conversion errors are important warnings/errors
                    self._output_and_log("ERROR", f"Datenkonvertierungsfehler für Hauptnummer {main_number_val}: {e}")
                    invalid_cnt += 1
                except Exception as e:
                    # Unexpected errors during processing
                    self._output_and_log("ERROR", f"Unerwarteter Fehler bei gültigem Eintrag {main_number_val}: {e}")
                    invalid_cnt += 1
            else:
                invalid_cnt += 1
                m_n_str = str(main_number_val)
                a_q_val = main_number_data.get_article_quantity()
                a_t_val = main_number_data.get_article_total()
                a_q_str = str(a_q_val) if a_q_val is not None else "N/A"
                a_t_str = f"{float(a_t_val):.2f} EUR" if a_t_val is not None and isinstance(
                    a_t_val, (int, float)) else "N/A"  # Added type check
                # Log skipped invalid entries at WARNING level, maybe also output if user needs to know why counts differ
                self._output_and_log(
                    "WARNING", f">> Verkäufer-Eintrag (UNGÜLTIG): {first_name} {second_name}, MNr: {m_n_str}, Artikel: {a_q_str}, Wert: {a_t_str}. Übersprungen.")

        self.write(output_data)  # write handles its own messages
        # Final summary for user
        self._output_and_log("INFO", f"Verkäuferliste abgeschlossen: \n" +
                             "      ========================\n" +
                             f"          --> Gültige Einträge: {valid_cnt}\n" +
                             f"          --> Ungültige/Übersprungene Einträge: {invalid_cnt}\n")

        # Update tracker - internal log
        if overall_tracker and isinstance(overall_tracker, ProgressTrackerAbstraction):
            overall_tracker.increment()
            self._log("DEBUG", "Overall tracker incremented for SellerDataGenerator.")
        elif overall_tracker:
            # Warning about tracker type
            self._output_and_log("WARNING", "overall_tracker wurde übergeben, ist aber kein ProgressTrackerInterface.")
