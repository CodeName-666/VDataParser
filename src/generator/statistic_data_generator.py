# --- statistic_data_generator.py ---
from pathlib import Path
from typing import List, Optional


from log import CustomLogger
from objects import FleatMarket
from display import ProgressTrackerAbstraction
from display import OutputInterfaceAbstraction
try:
    from display import ProgressBarAbstraction as _BarBase
except Exception:  # pragma: no cover - optional dependency
    _BarBase = None  # type: ignore
try:
    from display import ConsoleProgressBar as _ConsoleBar
except Exception:  # pragma: no cover - optional dependency
    _ConsoleBar = None  # type: ignore
from display import BasicProgressTracker as ProgressTracker
from .data_generator import DataGenerator


class StatisticDataGenerator(DataGenerator):
    """ Generates statistic data ('versand.dat'), using optional logging and output interface. """

    FILE_SUFFIX = 'dat'

    def __init__(self, fleat_market_data: FleatMarket, path: str = '', file_name: str = 'statistic_data',
                 logger: Optional[CustomLogger] = None, output_interface: Optional[OutputInterfaceAbstraction] = None):
        
        """ Initializes the StatisticDataGenerator with data, path, name, logger, and output interface. """
        super().__init__(path, file_name, logger, output_interface)  # Pass both
        self.__fleat_market_data = fleat_market_data
       

    def __create_entry(self, main_number: int) -> str:
        """ Creates a formatted entry: main_number,"-" """
        return f'{main_number},"-"\n'

    def write(
        self,
        output_data: List[str],
        tracker: Optional[ProgressTrackerAbstraction] = None,
    ) -> bool:
        """Write ``output_data`` to disk."""
        if not output_data:
            self._output_and_log("INFO", "Keine Statistikdaten zum Schreiben vorhanden.")
            if tracker is not None:
                tracker.set_error(RuntimeError("no data"))
            return False
        full_path = self.get_full_path()  # Handles its own errors
        try:
            full_path.parent.mkdir(parents=True, exist_ok=True)
            with open(full_path, 'w', encoding='utf-8') as file:
                file.writelines(output_data)
            # Success message for user
            self._output_and_log("INFO", f"Statistikdaten erfolgreich geschrieben: {full_path}")
            return True
        except IOError as e:
            # Critical errors for user
            self._output_and_log("ERROR", f"Fehler beim Schreiben der Statistikdaten nach {full_path}: {e}")
            if tracker is not None:
                tracker.set_error(e)
            return False
        except Exception as e:
            self._output_and_log("ERROR", f"Unerwarteter Fehler beim Schreiben der Statistikdaten: {e}")
            if tracker is not None:
                tracker.set_error(e)
            return False

    def generate(
        self,
        overall_tracker: Optional[ProgressTrackerAbstraction] = None,
        *,
        bar: Optional[_BarBase] = None,
    ) -> None:
        """Generate statistic data and update ``overall_tracker``."""
        # Start message for user
        self._output_and_log("INFO", f"Generiere Statistik Daten ({self.file_name}.{self.FILE_SUFFIX}):\n" +
                             "      ========================")
        output_data: List[str] = []
        valid_cnt = 0
        invalid_cnt = 0

        try:
            all_main_numbers_data = self.__fleat_market_data.main_numbers()
            tracker = ProgressTracker()
            tracker.reset(total=len(all_main_numbers_data) + 1)
            if hasattr(self.output_interface, "set_secondary_tracker"):
                try:
                    self.output_interface.set_secondary_tracker(tracker)  # type: ignore[attr-defined]
                except Exception:
                    pass
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
                invalid_cnt += 1

            if tracker is not None:
                tracker.increment()

        success = self.write(output_data, tracker)
        if success:
            tracker.increment()
        # Final summary for user
        self._output_and_log(
            "INFO", f"   >> Statistikdaten erstellt: {valid_cnt} gültige Einträge, {invalid_cnt} ungültige/übersprungene Hauptnummern <<\n")

        if tracker.has_error:
            self._output_and_log("ERROR", "Statistikdatei konnte nicht erstellt werden – siehe Log.")
            if overall_tracker:
                overall_tracker.set_error(RuntimeError("statistic data error"))  # type: ignore[attr-defined]

        if overall_tracker and isinstance(overall_tracker, ProgressTrackerAbstraction):
            overall_tracker.increment()
            self._log("DEBUG", "Overall tracker incremented for StatisticDataGenerator.")
        elif overall_tracker:
            self._output_and_log("WARNING", "overall_tracker wurde übergeben, ist aber kein ProgressTrackerInterface.")
