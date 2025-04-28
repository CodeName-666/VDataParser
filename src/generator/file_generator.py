# --- file_generator.py ---
from pathlib import Path
import time
from typing import Optional, List

# Conditional imports... (keep as they are)
try:
    from log import CustomLogger
except ImportError:
    CustomLogger = None
try:
    from objects import FleatMarket
except ImportError:
    class FleatMarket:
        pass
try:
    from src.display import OutputInterfaceAbstraction  # Added
except ImportError:
    OutputInterfaceAbstraction = None  # Added

# Import generators and progress classes... (keep as they are)
from .price_list_generator import PriceListGenerator
from .seller_data_generator import SellerDataGenerator
from .statistic_data_generator import StatisticDataGenerator
from .receive_info_pdf_generator import ReceiveInfoPdfGenerator
try:
    from src.display import ProgressTrackerAbstraction
except ImportError:
    ProgressTrackerAbstraction = None
try:
    from src.display import ConsoleProgressBar
except ImportError:
    ConsoleProgressBar = None


class FileGenerator:
    """
    Orchestrates file generation with optional logging, output interface, and overall progress.
    """

    def __init__(self,
                 fleat_market_data: FleatMarket,
                 output_path: str = 'output',
                 seller_file_name: str = "kundendaten",
                 price_list_file_name: str = "preisliste",
                 statistic_file_name: str = "versand",
                 pdf_template_path_input: str = 'template/template.pdf',
                 pdf_output_file_name: str = 'Abholbestaetigungen.pdf',
                 logger: Optional[CustomLogger] = None,  # Accept optional logger
                 output_interface: Optional[OutputInterfaceAbstraction] = None  # Added
                 ) -> None:
        """ Initializes FileGenerator and its sub-generators. """
        self.logger = logger  # Store the logger
        self.output_interface = output_interface  # Store the output interface
        self.output_path = Path(output_path) if output_path else Path('.')
        self.fleat_market_data = fleat_market_data

        # Use internal _log for DEBUG, _output_and_log for INFO/ERROR
        self._log("DEBUG", f"FileGenerator initialized. Output path: {self.output_path.resolve()}")

        try:
            self._verify_output_path(self.output_path)
        except Exception as e:
            # Critical setup error
            err_msg = f"Konnte Ausgabepfad '{self.output_path}' nicht erstellen: {e}"
            self._output_and_log("ERROR", err_msg)  # Log and output
            raise RuntimeError(err_msg) from e

        # Initialize generators, passing logger and output_interface
        output_path_str = str(self.output_path)
        common_args = {
            'fleat_market_data': fleat_market_data,
            'path': output_path_str,
            'logger': self.logger,
            'output_interface': self.output_interface  # Pass it down
        }

        self.__seller_generator = SellerDataGenerator(**common_args, file_name=seller_file_name)
        self.__price_list_generator = PriceListGenerator(**common_args, file_name=price_list_file_name)
        self.__statistic_generator = StatisticDataGenerator(**common_args, file_name=statistic_file_name)
        self.__receive_info_pdf_generator = ReceiveInfoPdfGenerator(
            **common_args,  # Pass common args including logger and output_interface
            pdf_template_path_input=pdf_template_path_input,
            pdf_template_path_output=pdf_output_file_name
        )

        # Task list remains the same
        self.generation_tasks = [
            ("Verkäuferdaten (.dat)", self.__seller_generator),
            ("Preisliste (.dat)", self.__price_list_generator),
            ("Statistikdaten (.dat)", self.__statistic_generator),
            ("Abholbestätigung (.pdf)", self.__receive_info_pdf_generator),
        ]
        self.total_steps = len(self.generation_tasks)

        # Progress tracking setup remains the same
        self.__overall_tracker = None
        self.__overall_progress_bar = None
        if ProgressTrackerAbstraction and ConsoleProgressBar:
            self.__overall_tracker = ProgressTrackerAbstraction(total=self.total_steps)
            self.__overall_progress_bar = ConsoleProgressBar(length=60, description="Gesamtfortschritt")
            self._log("DEBUG", "Gesamtfortschrittsanzeige initialisiert.")
        else:
            # Warning relevant to user if progress bar missing
            self._output_and_log(
                "WARNING", "Fortschrittsanzeige nicht verfügbar (ProgressTrackerInterface oder ConsoleProgressBar fehlt).")

    # --- Add Helper Methods for FileGenerator ---
    def _log(self, level: str, message: str) -> None:
        """ Helper method for conditional logging ONLY for FileGenerator itself. """
        if self.logger:
            log_method = getattr(self.logger, level.lower(), None)
            if log_method and callable(log_method):
                # FileGenerator's logs might not need on_verbose separation
                log_method(message)

    def _output(self, message: str) -> None:
        """ Helper method to write ONLY to the output interface for FileGenerator itself. """
        if self.output_interface:
            try:
                self.output_interface.write_message(message)
            except Exception as e:
                self._log("ERROR", f"FileGenerator failed to write message to output interface: {e}")

    def _output_and_log(self, level: str, message: str) -> None:
        """
        Helper method for sending messages to BOTH logger and output interface
        for FileGenerator itself.
        """
        self._log(level, message)
        if level.upper() in ["INFO", "WARNING", "ERROR", "CRITICAL"]:
            self._output(message)
    # --- End Helper Methods ---

    def _verify_output_path(self, path: Path):
        """ Ensures the output path exists. """
        path.mkdir(parents=True, exist_ok=True)
        # Internal confirmation, just log
        self._log("DEBUG", f"Ausgabepfad sichergestellt: {path.resolve()}")

    def generate(self):
        """ Runs all configured generation tasks sequentially. """
        # Main start message for user
        self._output_and_log("INFO", f"Starte Gesamt-Dateigenerierung nach '{self.output_path.resolve()}'...")
        if not self.fleat_market_data:
            # Critical error for user
            self._output_and_log("ERROR", "Keine Flohmarktdaten übergeben. Generierung abgebrochen.")
            return

        start_time = time.time()
        global_success = True

        # Reset progress bar - internal
        if self.__overall_tracker:
            self.__overall_tracker.reset(total=self.total_steps)
            if self.__overall_progress_bar:
                state = self.__overall_tracker.get_state()
                self.__overall_progress_bar.update(state['percentage'], state['current'], state['total'])

        for name, generator_instance in self.generation_tasks:
            # Start message for each step - user relevant
            self._output_and_log("INFO", f"\n--- Starte Schritt: {name} ---")
            if self.output_interface:
                self.output_interface.write_separator('=')  # Optional separator

            step_start_time = time.time()
            try:
                # The generator's generate method now uses its own _output_and_log
                generator_instance.generate(overall_tracker=self.__overall_tracker)

                step_duration = time.time() - step_start_time
                # Step completion message - user relevant
                self._output_and_log("INFO", f"--- Schritt '{name}' beendet (Dauer: {step_duration:.2f}s) ---")

                # Update overall progress bar (visual output)
                if self.__overall_tracker and self.__overall_progress_bar:
                    state = self.__overall_tracker.get_state()
                    self.__overall_progress_bar.update(state['percentage'], state['current'], state['total'])
                    if state['error']:
                        # Error reported by sub-generator (already logged/output there)
                        # Add a high-level notice here too
                        self._output_and_log(
                            "ERROR", f"!! Fehler festgestellt während Schritt '{name}': {state['error']}. Fortfahren...")
                        global_success = False  # Mark overall failure

            except NotImplementedError as e:  # Catch specific error
                err_msg = f"Fehler: Die 'generate'-Methode ist für '{name}' nicht implementiert."
                self._output_and_log("ERROR", err_msg)  # Critical error
                global_success = False
                if self.__overall_tracker:
                    self.__overall_tracker.set_error(e)  # Use the actual exception
                    if self.__overall_tracker.current < self.total_steps:
                        self.__overall_tracker.increment()
                if self.__overall_tracker and self.__overall_progress_bar:
                    state = self.__overall_tracker.get_state()
                    self.__overall_progress_bar.update(state['percentage'], state['current'], state['total'])

            except Exception as e:
                step_duration = time.time() - step_start_time
                # Unexpected error during step - critical for user
                self._output_and_log(
                    "ERROR", f"!! Unerwarteter FEHLER während Schritt '{name}' nach {step_duration:.2f}s: {e}")
                # Optionally add traceback to logger:
                # if self.logger: self.logger.exception(f"Traceback für unerwarteten Fehler in Schritt {name}:")
                global_success = False
                if self.__overall_tracker:
                    self.__overall_tracker.set_error(e)
                    if self.__overall_tracker.current < self.total_steps:
                        self.__overall_tracker.increment()
                if self.__overall_tracker and self.__overall_progress_bar:
                    state = self.__overall_tracker.get_state()
                    self.__overall_progress_bar.update(state['percentage'], state['current'], state['total'])
                # break # Decide whether to stop or continue

        # Final summary for user
        end_time = time.time()
        total_duration = end_time - start_time
        self._output_and_log("INFO", "\n========================================")
        if global_success:
            self._output_and_log(
                "INFO", f"Alle Generierungsschritte erfolgreich abgeschlossen in {total_duration:.2f} Sekunden.")
            if self.__overall_progress_bar:
                self.__overall_progress_bar.complete(success=True)
        else:
            final_error_msg = "Unbekannter Fehler oder Fehler in vorherigen Schritten."
            if self.__overall_tracker and self.__overall_tracker.error:
                final_error_msg = str(self.__overall_tracker.error)
            self._output_and_log(
                "ERROR", f"Dateigenerierung mit FEHLERN abgeschlossen nach {total_duration:.2f} Sekunden.")
            if self.__overall_progress_bar:
                # Progress bar shows its own error message
                self.__overall_progress_bar.complete(
                    success=False, final_message=f"Abgeschlossen mit Fehlern (letzter: {final_error_msg[:80]})")
            # Add explicit final error message via output interface too
            self._output(f"FEHLER: Generierung nicht erfolgreich. Letzter gemeldeter Fehler: {final_error_msg}")

        self._output_and_log("INFO", "========================================")
