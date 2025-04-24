# --- file_generator.py ---
from pathlib import Path
import time
from typing import Optional, List

# Conditional import of CustomLogger
try:
    from log import CustomLogger
except ImportError:
    CustomLogger = None # type: ignore

# Assume objects are available
try:
    from objects import FleatMarket # Adjust name
except ImportError:
    class FleatMarket: pass # Dummy

# Import generators and progress classes (handle imports conditionally/gracefully)
from .price_list_generator import PriceListGenerator
from .seller_data_generator import SellerDataGenerator
from .statistic_data_generator import StatisticDataGenerator
from .receive_info_pdf_generator import ReceiveInfoPdfGenerator
try:
    from .progress_tracker import ProgressTracker
except ImportError:
    ProgressTracker = None # type: ignore
try:
    from .console_progress_bar import ConsoleProgressBar
except ImportError:
    ConsoleProgressBar = None # type: ignore

class FileGenerator:
    """
    Orchestrates file generation with optional logging and overall progress.
    """

    def __init__(self,
                 fleat_market_data: FleatMarket,
                 output_path: str = 'output',
                 seller_file_name: str = "kundendaten",
                 price_list_file_name: str = "preisliste",
                 statistic_file_name: str = "versand",
                 pdf_template_path_input: str = 'template/template.pdf',
                 pdf_output_file_name: str = 'Abholbestaetigungen.pdf',
                 logger: Optional[CustomLogger] = None # Accept optional logger
                 ) -> None:
        """ Initializes FileGenerator and its sub-generators. """
        self.logger = logger # Store the logger
        self.output_path = Path(output_path) if output_path else Path('.')
        self.fleat_market_data = fleat_market_data

        self._log("DEBUG", f"FileGenerator initialized. Output path: {self.output_path.resolve()}")

        try:
            self._verify_output_path(self.output_path)
        except Exception as e:
             self._log("ERROR", f"Konnte Ausgabepfad '{self.output_path}' nicht erstellen: {e}")
             raise RuntimeError(f"Ausgabepfad '{self.output_path}' konnte nicht erstellt werden.") from e

        # Initialize generators, passing the logger instance
        output_path_str = str(self.output_path)
        common_args = {'fleat_market_data': fleat_market_data, 'path': output_path_str, 'logger': self.logger}

        self.__seller_generator = SellerDataGenerator(**common_args, file_name=seller_file_name)
        self.__price_list_generator = PriceListGenerator(**common_args, file_name=price_list_file_name)
        self.__statistic_generator = StatisticDataGenerator(**common_args, file_name=statistic_file_name)
        self.__receive_info_pdf_generator = ReceiveInfoPdfGenerator(
            **common_args, # Pass common args including logger
            pdf_template_path_input=pdf_template_path_input,
            pdf_template_path_output=pdf_output_file_name
        )

        self.generation_tasks = [
            ("Verkäuferdaten (.dat)", self.__seller_generator),
            ("Preisliste (.dat)", self.__price_list_generator),
            ("Statistikdaten (.dat)", self.__statistic_generator),
            ("Abholbestätigung (.pdf)", self.__receive_info_pdf_generator),
        ]
        self.total_steps = len(self.generation_tasks)

        # Setup overall progress tracking if available
        self.__overall_tracker = None
        self.__overall_progress_bar = None
        if ProgressTracker and ConsoleProgressBar:
             self.__overall_tracker = ProgressTracker(total=self.total_steps)
             self.__overall_progress_bar = ConsoleProgressBar(length=60, description="Gesamtfortschritt")
             self._log("DEBUG", "Gesamtfortschrittsanzeige initialisiert.")
        else:
             self._log("WARNING", "Fortschrittsanzeige nicht verfügbar (ProgressTracker oder ConsoleProgressBar fehlt).")

    def _log(self, level: str, message: str, on_verbose: bool = False) -> None:
        """ Helper method for conditional logging for FileGenerator itself. """
        if self.logger:
            log_method = getattr(self.logger, level.lower(), None)
            if log_method and callable(log_method):
                 # Assuming CustomLogger methods handle on_verbose correctly
                if level.lower() in ["debug", "info", "warning", "error"]:
                     log_method(message, on_verbose=on_verbose)
                else:
                     log_method(message) # Fallback

    def _verify_output_path(self, path: Path):
        """ Ensures the output path exists. """
        path.mkdir(parents=True, exist_ok=True)
        self._log("DEBUG", f"Ausgabepfad sichergestellt: {path.resolve()}")

    def generate(self):
        """ Runs all configured generation tasks sequentially. """
        self._log("INFO", f"Starte Gesamt-Dateigenerierung nach '{self.output_path.resolve()}'...")
        if not self.fleat_market_data:
             self._log("ERROR", "Keine Flohmarktdaten übergeben. Generierung abgebrochen.")
             return

        start_time = time.time()
        global_success = True

        # Reset and display initial progress bar state
        if self.__overall_tracker:
            self.__overall_tracker.reset(total=self.total_steps)
            if self.__overall_progress_bar:
                 state = self.__overall_tracker.get_state()
                 self.__overall_progress_bar.update(state['percentage'], state['current'], state['total'])

        for name, generator_instance in self.generation_tasks:
            self._log("INFO", f"\n--- Starte Schritt: {name} ---")
            step_start_time = time.time()
            try:
                # The generator's generate method uses its own logger (passed during init)
                # We pass the overall_tracker for progress updates
                generator_instance.generate(overall_tracker=self.__overall_tracker)

                step_duration = time.time() - step_start_time
                self._log("INFO", f"--- Schritt '{name}' beendet (Dauer: {step_duration:.2f}s) ---")

                # Update overall progress bar
                if self.__overall_tracker and self.__overall_progress_bar:
                    state = self.__overall_tracker.get_state()
                    self.__overall_progress_bar.update(state['percentage'], state['current'], state['total'])
                    if state['error']:
                         self._log("ERROR", f"!! Fehler festgestellt während Schritt '{name}': {state['error']}. Fortfahren...")
                         global_success = False # Mark overall failure

            except NotImplementedError:
                 self._log("ERROR", f"Fehler: Die 'generate'-Methode ist für '{name}' nicht implementiert.")
                 global_success = False
                 if self.__overall_tracker:
                      self.__overall_tracker.set_error(NotImplementedError(f"generate für {name} fehlt"))
                      if self.__overall_tracker.current < self.total_steps: self.__overall_tracker.increment() # Ensure step counted
                 # Update bar after error
                 if self.__overall_tracker and self.__overall_progress_bar:
                      state = self.__overall_tracker.get_state()
                      self.__overall_progress_bar.update(state['percentage'], state['current'], state['total'])

            except Exception as e:
                step_duration = time.time() - step_start_time
                self._log("ERROR", f"!! Unerwarteter FEHLER während Schritt '{name}' nach {step_duration:.2f}s: {e}") # exc_info=True for traceback if logger supports it
                global_success = False
                if self.__overall_tracker:
                    self.__overall_tracker.set_error(e)
                    if self.__overall_tracker.current < self.total_steps: self.__overall_tracker.increment() # Ensure step counted
                 # Update bar after error
                if self.__overall_tracker and self.__overall_progress_bar:
                    state = self.__overall_tracker.get_state()
                    self.__overall_progress_bar.update(state['percentage'], state['current'], state['total'])
                # Decide whether to break or continue on unexpected errors
                # break

        # Final summary
        end_time = time.time()
        total_duration = end_time - start_time
        self._log("INFO", "\n========================================")
        if global_success:
            self._log("INFO", f"Alle Generierungsschritte abgeschlossen in {total_duration:.2f} Sekunden.")
            if self.__overall_progress_bar:
                self.__overall_progress_bar.complete(success=True)
        else:
            final_error_msg = "Unbekannter Fehler"
            if self.__overall_tracker and self.__overall_tracker.error:
                 final_error_msg = str(self.__overall_tracker.error)
            self._log("ERROR", f"Dateigenerierung mit FEHLERN abgeschlossen nach {total_duration:.2f} Sekunden.")
            if self.__overall_progress_bar:
                 self.__overall_progress_bar.complete(success=False, final_message=f"Abgeschlossen mit Fehlern (letzter: {final_error_msg[:80]})")
        self._log("INFO", "========================================")