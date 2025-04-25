# --- statistic_data_generator.py ---
from pathlib import Path
from typing import List, Optional

# Conditional import of CustomLogger
try:
    from log import CustomLogger
except ImportError:
    CustomLogger = None # type: ignore

# Assume objects and ProgressTracker are available
try:
    from objects import FleatMarket # Adjust name as per your project
except ImportError:
    class FleatMarket: get_main_number_list = lambda self: []
try:
    from .progress_tracker import ProgressTracker
except ImportError:
    ProgressTracker = None # type: ignore

from .data_generator import DataGenerator

class StatisticDataGenerator(DataGenerator):
    """ Generates statistic data ('versand.dat'), using optional logging. """

    FILE_SUFFIX = 'dat'

    def __init__(self,
                 fleat_market_data: FleatMarket,
                 path: str = '',
                 file_name: str = 'versand',
                 logger: Optional[CustomLogger] = None) -> None:
        """ Initializes the StatisticDataGenerator with data, path, name, and logger. """
        super().__init__(path, file_name, logger) # Pass logger to base class
        self.__fleat_market_data = fleat_market_data
        # self.logger inherited

    def __create_entry(self, main_number: int) -> str:
        """ Creates a formatted entry: main_number,"-" """
        return f'{main_number},"-"\n'

    def write(self, output_data: List[str]):
        """ Writes the generated statistic data entries to the file. """
        if not output_data:
            self._log("INFO", "Keine Statistikdaten zum Schreiben vorhanden.")
            return
        full_path = self.get_full_path()
        try:
            full_path.parent.mkdir(parents=True, exist_ok=True)
            with open(full_path, 'w', encoding='utf-8') as file:
                file.writelines(output_data)
            self._log("INFO", f"Statistikdaten erfolgreich geschrieben: {full_path}")
        except IOError as e:
            self._log("ERROR", f"Fehler beim Schreiben der Statistikdaten nach {full_path}: {e}")
        except Exception as e:
            self._log("ERROR", f"Unerwarteter Fehler beim Schreiben der Statistikdaten: {e}")

    def generate(self, overall_tracker: Optional[ProgressTracker] = None):
        """ Generates statistic data, writes, and updates tracker. """
        self._log("INFO", f"Generiere Statistik Daten ({self.file_name}.{self.FILE_SUFFIX}):\n" +
                    "      ========================")
        output_data: List[str] = []
        valid_cnt = 0
        invalid_cnt = 0

        try:
            all_main_numbers_data = self.__fleat_market_data.get_main_number_list()
        except AttributeError:
             self._log("ERROR", "FleatMarket Objekt hat keine Methode 'get_main_number_list'. Breche ab.")
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
            if not all([hasattr(main_number_data, 'is_valid'),
                        hasattr(main_number_data, 'get_main_number')]):
                 self._log("WARNING", "Unerwartetes Datenobjekt in Hauptnummernliste gefunden. Übersprungen.")
                 invalid_cnt += 1
                 continue

            if main_number_data.is_valid():
                try:
                    main_number = int(main_number_data.get_main_number())
                    entry = self.__create_entry(main_number)
                    output_data.append(entry)
                    valid_cnt +=1
                except (ValueError, TypeError) as e:
                     self._log("ERROR", f"Hauptnummer nicht als Zahl interpretierbar: {main_number_data.get_main_number()}. Fehler: {e}")
                     invalid_cnt += 1
                except Exception as e:
                     self._log("ERROR", f"Unerwarteter Fehler bei gültiger Hauptnummer {main_number_data.get_main_number()}: {e}")
                     invalid_cnt += 1
            else:
                invalid_cnt +=1

        self.write(output_data)
        self._log("INFO", f"   >> Statistikdaten erstellt: {valid_cnt} gültige Einträge, {invalid_cnt} ungültige/übersprungene Hauptnummern <<\n")

        # Update tracker
        if overall_tracker and isinstance(overall_tracker, ProgressTracker):
            overall_tracker.increment()
        elif overall_tracker:
             self._log("WARNING", "overall_tracker wurde übergeben, ist aber kein ProgressTracker.")