# --- statistic_data_generator.py ---
from pathlib import Path
from typing import List, Optional


from log import CustomLogger
from objects import FleatMarket
from display import ProgressTrackerAbstraction
from display import OutputInterfaceAbstraction  # Added
from .data_generator import DataGenerator


class StatisticDataGenerator(DataGenerator):
    """ Generates statistic data ('versand.dat'), using optional logging and output interface. """

    FILE_SUFFIX = 'dat'

    def __init__(self, fleat_market_data: FleatMarket, path: str = '', file_name: str = 'versand',
                 logger: Optional[CustomLogger] = None, output_interface: Optional[OutputInterfaceAbstraction] = None):
        
        """ Initializes the StatisticDataGenerator with data, path, name, logger, and output interface. """
        super().__init__(path, file_name, logger, output_interface)  # Pass both
        self.__fleat_market_data = fleat_market_data
       

    def __create_entry(self, main_number: int) -> str:
        """ Creates a formatted entry: main_number,"-" """
        return f'{main_number},"-"\n'

    def write(self, output_data: List[str]):
        """ Writes the generated statistic data entries to the file. """
        if not output_data:
            # Inform user and log
            self._output_and_log("INFO", "Keine Statistikdaten zum Schreiben vorhanden.")
            return
        full_path = self.get_full_path()  # Handles its own errors
        try:
            full_path.parent.mkdir(parents=True, exist_ok=True)
            with open(full_path, 'w', encoding='utf-8') as file:
                file.writelines(output_data)
            # Success message for user
            self._output_and_log("INFO", f"Statistikdaten erfolgreich geschrieben: {full_path}")
        except IOError as e:
            # Critical errors for user
            self._output_and_log("ERROR", f"Fehler beim Schreiben der Statistikdaten nach {full_path}: {e}")
        except Exception as e:
            self._output_and_log("ERROR", f"Unerwarteter Fehler beim Schreiben der Statistikdaten: {e}")

    def generate(self, overall_tracker: Optional[ProgressTrackerAbstraction] = None):
        """ Generates statistic data, writes, and updates tracker. """
        # Start message for user
        self._output_and_log("INFO", f"Generiere Statistik Daten ({self.file_name}.{self.FILE_SUFFIX}):\n" +
                             "      ========================")
        output_data: List[str] = []
        valid_cnt = 0
        invalid_cnt = 0

        try:
            all_main_numbers_data = self.__fleat_market_data.main_numbers()
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

        for main_number_data in all_main_numbers_data:
            # Data structure check - potentially relevant warning
            if not all([hasattr(main_number_data, 'is_valid'),
                        hasattr(main_number_data, 'number')]):
                self._output_and_log("WARNING", "Unerwartetes Datenobjekt in Hauptnummernliste gefunden. Übersprungen.")
                invalid_cnt += 1
                continue

            if main_number_data.is_valid():
                try:
                    main_number = int(main_number_data.number())
                    entry = self.__create_entry(main_number)
                    output_data.append(entry)
                    valid_cnt += 1
                except (ValueError, TypeError) as e:
                    # Data conversion error
                    self._output_and_log(
                        "ERROR", f"Hauptnummer nicht als Zahl interpretierbar: {main_number_data.number()}. Fehler: {e}. Übersprungen.")
                    invalid_cnt += 1
                except Exception as e:
                    # Unexpected processing error
                    self._output_and_log(
                        "ERROR", f"Unerwarteter Fehler bei gültiger Hauptnummer {main_number_data.number()}: {e}. Übersprungen.")
                    invalid_cnt += 1
            else:
                # Skipping invalid is expected, just increment count
                # self._log("DEBUG", f"Überspringe ungültige Hauptnummer für Statistik: {main_number_data.get_main_number()}")
                invalid_cnt += 1

        self.write(output_data)  # write handles its own messages
        # Final summary for user
        self._output_and_log(
            "INFO", f"   >> Statistikdaten erstellt: {valid_cnt} gültige Einträge, {invalid_cnt} ungültige/übersprungene Hauptnummern <<\n")

        # Update tracker - internal log
        if overall_tracker and isinstance(overall_tracker, ProgressTrackerAbstraction):
            overall_tracker.increment()
            self._log("DEBUG", "Overall tracker incremented for StatisticDataGenerator.")
        elif overall_tracker:
            # Warning about tracker type
            self._output_and_log("WARNING", "overall_tracker wurde übergeben, ist aber kein ProgressTrackerInterface.")
