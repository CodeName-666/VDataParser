# --- statistic_data_generator.py ---
from pathlib import Path
from typing import List, Optional

# Annahme: Benötigte Objekte sind in 'objects.py' und Logger in 'log.py'
try:
    from objects import FleatMarket # Nur FleatMarket benötigt
    from log import logger
except ImportError:
    print("WARNUNG: Konnte 'objects' oder 'log' nicht importieren. Stellen Sie sicher, dass diese Module existieren.")
    # Dummy-Implementierungen
    class FleatMarket:
        def get_main_number_data_list(self): return []
    class Logger:
        def info(self, msg): print(f"INFO: {msg}")
        def warning(self, msg): print(f"WARN: {msg}")
        def error(self, msg): print(f"ERROR: {msg}")
    logger = Logger()

from .data_generator import DataGenerator
# Annahme: ProgressTracker existiert im selben Verzeichnis oder im PYTHONPATH
try:
    from .progress_tracker import ProgressTracker
except ImportError:
    ProgressTracker = None


class StatisticDataGenerator(DataGenerator):
    """
    Generates a simple statistics file ('versand.dat').
    Format: main_number,"-"
    Only includes entries for valid main numbers.
    """

    FILE_SUFFIX = 'dat'

    def __init__(self, fleat_market_data: FleatMarket, path: str = '', file_name: str = 'versand') -> None:
        """
        Initializes the StatisticDataGenerator.

        Args:
            fleat_market_data: The flea market data object.
            path: The output directory path.
            file_name: The name of the output file (without suffix). Default is 'versand'.
        """
        super().__init__(path, file_name)
        self.__fleat_market_data: FleatMarket = fleat_market_data

    def __create_entry(self, main_number: int) -> str:
        """ Creates a formatted entry: main_number,"-" """
        return f'{main_number},"-"\n'

    def __write(self, output_data: List[str]):
        """ Writes the generated statistic data entries to the file. """
        if not output_data:
            logger.info("Keine Statistikdaten zum Schreiben vorhanden.")
            return

        full_path = self.get_full_path()
        try:
            full_path.parent.mkdir(parents=True, exist_ok=True)
            with open(full_path, 'w', encoding='utf-8') as file: # Specify encoding
                file.writelines(output_data)
            logger.info(f"Statistikdaten erfolgreich geschrieben: {full_path}")
        except IOError as e:
            logger.error(f"Fehler beim Schreiben der Statistikdaten nach {full_path}: {e}")
        except Exception as e:
            logger.error(f"Unerwarteter Fehler beim Schreiben der Statistikdaten: {e}")


    def generate(self, overall_tracker: Optional[ProgressTracker] = None):
        """
        Generates statistic data for valid main numbers, writes the file,
        and updates the overall progress tracker if provided.
        """
        output_data: List[str] = []
        valid_cnt = 0
        invalid_cnt = 0
        logger.info(f"Generiere Statistik Daten ({self.file_name}.{self.FILE_SUFFIX}):\n" +
                    "      ========================")

        try:
            all_main_numbers_data = self.__fleat_market_data.get_main_number_data_list()
        except AttributeError:
             logger.error("FleatMarket Objekt hat keine Methode 'get_main_number_data_list'. Breche Statistik-Generierung ab.")
             if overall_tracker:
                 overall_tracker.set_error(AttributeError("Fehlende Methode in FleatMarket"))
                 overall_tracker.increment()
             return
        except Exception as e:
             logger.error(f"Fehler beim Abrufen der Hauptnummern-Daten: {e}")
             if overall_tracker:
                 overall_tracker.set_error(e)
                 overall_tracker.increment()
             return

        for main_number_data in all_main_numbers_data:
             # Prüfe Datenobjekt
            if not all([hasattr(main_number_data, 'is_valid'),
                        hasattr(main_number_data, 'get_main_number')]):
                 logger.warning("Unerwartetes Datenobjekt in Hauptnummernliste gefunden. Übersprungen.")
                 invalid_cnt += 1
                 continue

            if main_number_data.is_valid():
                try:
                    main_number = int(main_number_data.get_main_number())
                    entry = self.__create_entry(main_number)
                    output_data.append(entry)
                    valid_cnt +=1
                except (ValueError, TypeError) as e:
                     logger.error(f"Konnte Hauptnummer nicht als Zahl interpretieren: {main_number_data.get_main_number()}. Fehler: {e}")
                     invalid_cnt += 1
                except Exception as e:
                     logger.error(f"Unerwarteter Fehler bei gültiger Hauptnummer {main_number_data.get_main_number()}: {e}")
                     invalid_cnt += 1
            else:
                invalid_cnt +=1

        self.__write(output_data)
        logger.info(f"   >> Statistikdaten erstellt: {valid_cnt} gültige Einträge, {invalid_cnt} ungültige/übersprungene Hauptnummern <<\n")

        # Melde Abschluss dieser Aufgabe an den Gesamt-Tracker
        if overall_tracker and isinstance(overall_tracker, ProgressTracker):
            overall_tracker.increment()
        elif overall_tracker:
             logger.warning("overall_tracker wurde übergeben, ist aber kein ProgressTracker.")