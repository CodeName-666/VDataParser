# --- file_generator.py ---
from pathlib import Path
import time
from typing import Optional, List, Type # Added Type for type hinting abstract classes

# Conditional imports... (keep as they are)
try:
    from log import CustomLogger
except ImportError:
    CustomLogger = None
try:
    from objects import FleatMarket
except ImportError:
    class FleatMarket: # type: ignore
        pass
try:
    from src.display import OutputInterfaceAbstraction
except ImportError:
    OutputInterfaceAbstraction = None # type: ignore

# Import Abstractions/Interfaces
try:
    # Import the tracker abstraction
    from src.display import ProgressTrackerAbstraction
except ImportError:
    ProgressTrackerAbstraction = None # type: ignore

try:
    # Import the progress bar abstraction
    from src.display.progress_bar.progress_bar_abstraction import ProgressBarAbstraction
    # Import specific implementations only for type checking if needed downstream,
    # but FileGenerator itself should NOT depend on them directly.
    # from src.display.progress_bar.console_progress_bar import ConsoleProgressBar # Example
    # from src.display.progress_bar.qt_progress_bar import QtProgressBar # Example
except ImportError:
    ProgressBarAbstraction = None # type: ignore


# Import specific generators (keep as they are)
from .price_list_generator import PriceListGenerator
from .seller_data_generator import SellerDataGenerator
from .statistic_data_generator import StatisticDataGenerator
from .receive_info_pdf_generator import ReceiveInfoPdfGenerator


class FileGenerator:
    """
    Orchestrates file generation using provided progress tracking and display abstractions.
    """

    def __init__(self,
                 fleat_market_data: FleatMarket,
                 output_path: str = 'output',
                 seller_file_name: str = "kundendaten",
                 price_list_file_name: str = "preisliste",
                 statistic_file_name: str = "versand",
                 pdf_template_path_input: str = 'template/template.pdf',
                 pdf_output_file_name: str = 'Abholbestaetigungen.pdf',
                 logger: Optional[CustomLogger] = None,
                 output_interface: Optional[OutputInterfaceAbstraction] = None,
                 # --- Accept tracker and progress bar instances ---
                 progress_tracker: Optional[ProgressTrackerAbstraction] = None,
                 progress_bar: Optional[ProgressBarAbstraction] = None
                 ) -> None:
        """
        Initializes FileGenerator and its sub-generators.

        Args:
            fleat_market_data: Data object containing market information.
            output_path: Base directory for output files.
            seller_file_name: Base name for the seller data file.
            price_list_file_name: Base name for the price list file.
            statistic_file_name: Base name for the statistics file.
            pdf_template_path_input: Path to the PDF template file.
            pdf_output_file_name: Base name for the output PDF file.
            logger: Optional logger instance.
            output_interface: Optional interface for displaying messages.
            progress_tracker: Optional instance implementing ProgressTrackerAbstraction.
            progress_bar: Optional instance implementing ProgressBarAbstraction.
        """
        self.logger = logger
        self.output_interface = output_interface
        self.output_path = Path(output_path) if output_path else Path('.')
        self.fleat_market_data = fleat_market_data

        # Store the provided tracker and progress bar
        self.progress_tracker = progress_tracker
        self.progress_bar = progress_bar

        # Use internal _log for DEBUG, _output_and_log for INFO/ERROR
        self._log("DEBUG", f"FileGenerator initialized. Output path: {self.output_path.resolve()}")

        try:
            self._verify_output_path(self.output_path)
        except Exception as e:
            # Critical setup error
            err_msg = f"Konnte Ausgabepfad '{self.output_path}' nicht erstellen: {e}"
            self._output_and_log("ERROR", err_msg)
            raise RuntimeError(err_msg) from e

        # Initialize generators, passing logger and output_interface
        output_path_str = str(self.output_path)
        common_args = {
            'fleat_market_data': fleat_market_data,
            'path': output_path_str,
            'logger': self.logger,
            'output_interface': self.output_interface
            # Note: We don't pass the overall tracker/bar here.
            # The overall tracker is passed to the sub-generator's generate() method.
        }

        # Sub-generator initialization remains mostly the same
        self.__seller_generator = SellerDataGenerator(**common_args, file_name=seller_file_name)
        self.__price_list_generator = PriceListGenerator(**common_args, file_name=price_list_file_name)
        self.__statistic_generator = StatisticDataGenerator(**common_args, file_name=statistic_file_name)
        self.__receive_info_pdf_generator = ReceiveInfoPdfGenerator(
            **common_args,
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

        # Progress tracking setup - based on provided instances
        if self.progress_tracker and self.progress_bar:
            # Assume the tracker is already configured or will be reset in generate()
            self._log("DEBUG", f"Using provided Progress Tracker ({type(self.progress_tracker).__name__}) and Progress Bar ({type(self.progress_bar).__name__}).")
        elif self.progress_tracker:
            self._log("DEBUG", f"Using provided Progress Tracker ({type(self.progress_tracker).__name__}), but no Progress Bar provided.")
        elif self.progress_bar:
            # Warning: Progress bar without a tracker might not be very useful
            self._output_and_log("WARNING", f"Progress Bar ({type(self.progress_bar).__name__}) provided, but no Progress Tracker. Progress display may not function correctly.")
        else:
            # Log if abstractions are missing entirely, otherwise just note that instances weren't provided
            if ProgressTrackerAbstraction is None or ProgressBarAbstraction is None:
                 self._output_and_log("WARNING", "Fortschrittsanzeige nicht verfügbar (Abstraktionsklassen nicht gefunden oder Implementierung fehlt).")
            else:
                 self._log("INFO", "Kein Progress Tracker oder Progress Bar übergeben. Fortschritt wird nicht angezeigt.")


    # --- Helper Methods (_log, _output, _output_and_log) remain the same ---
    def _log(self, level: str, message: str) -> None:
        """ Helper method for conditional logging ONLY for FileGenerator itself. """
        if self.logger:
            log_method = getattr(self.logger, level.lower(), None)
            if log_method and callable(log_method):
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
        self._log("DEBUG", f"Ausgabepfad sichergestellt: {path.resolve()}")

    def generate(self):
        """ Runs all configured generation tasks sequentially, using provided progress tracker and bar. """
        self._output_and_log("INFO", f"Starte Gesamt-Dateigenerierung nach '{self.output_path.resolve()}'...")
        if not self.fleat_market_data:
            self._output_and_log("ERROR", "Keine Flohmarktdaten übergeben. Generierung abgebrochen.")
            return

        start_time = time.time()
        global_success = True

        # --- Use provided progress tracker and bar ---
        # Reset progress tracker if it exists
        if self.progress_tracker:
            try:
                # Ensure the tracker reflects the total steps for *this* run
                self.progress_tracker.reset(total=self.total_steps)
                # Update progress bar with initial state if both exist
                if self.progress_bar:
                    state = self.progress_tracker.get_state()
                    self.progress_bar.update(state.get('percentage', 0), state.get('current'), state.get('total'))
            except Exception as e:
                 self._output_and_log("ERROR", f"Fehler beim Initialisieren des Progress Trackers: {e}")
                 # Decide if we should continue without progress tracking
                 self.progress_tracker = None # Disable tracker for this run
                 self.progress_bar = None # Disable bar as well, as it needs the tracker

        for name, generator_instance in self.generation_tasks:
            self._output_and_log("INFO", f"\n--- Starte Schritt: {name} ---")
            if self.output_interface:
                self.output_interface.write_separator('=')

            step_start_time = time.time()
            current_step_success = True
            step_error: Optional[Exception] = None

            try:
                # Pass the *overall* tracker to the sub-generator's generate method
                # The sub-generator is responsible for calling increment() or set_error() on it.
                generator_instance.generate(overall_tracker=self.progress_tracker)

                # Check tracker state *after* the step for errors set by the sub-generator
                if self.progress_tracker:
                    state = self.progress_tracker.get_state()
                    step_error = state.get('error')
                    if step_error:
                        current_step_success = False
                        # Error logged/output by sub-generator ideally, but add high-level note
                        self._output_and_log("ERROR", f"!! Fehler festgestellt während Schritt '{name}' (vom Tracker gemeldet).")


            except NotImplementedError as e:
                err_msg = f"Fehler: Die 'generate'-Methode ist für '{name}' nicht implementiert."
                self._output_and_log("ERROR", err_msg)
                current_step_success = False
                step_error = e
                # Manually update tracker if step failed *before* calling its generate
                if self.progress_tracker:
                    try:
                        self.progress_tracker.set_error(e)
                        # Ensure progress moves forward even on error if tracker allows
                        if self.progress_tracker.current < self.total_steps:
                             self.progress_tracker.increment()
                    except Exception as te:
                        self._log("ERROR", f"Konnte Tracker-Fehler nicht setzen für '{name}': {te}")


            except Exception as e:
                step_duration = time.time() - step_start_time
                self._output_and_log("ERROR", f"!! Unerwarteter FEHLER während Schritt '{name}' nach {step_duration:.2f}s: {e}")
                # if self.logger: self.logger.exception(f"Traceback für unerwarteten Fehler in Schritt {name}:") # Optional traceback
                current_step_success = False
                step_error = e
                # Manually update tracker after unexpected exception in the loop
                if self.progress_tracker:
                     try:
                        self.progress_tracker.set_error(e)
                        if self.progress_tracker.current < self.total_steps:
                             self.progress_tracker.increment()
                     except Exception as te:
                        self._log("ERROR", f"Konnte Tracker-Fehler nicht setzen nach unerwartetem Fehler für '{name}': {te}")

            # --- Post-step processing ---
            step_duration = time.time() - step_start_time
            if current_step_success:
                self._output_and_log("INFO", f"--- Schritt '{name}' beendet (Dauer: {step_duration:.2f}s) ---")
            else:
                global_success = False # Mark overall failure if any step failed

            # Update overall progress bar (visual output) using tracker state
            if self.progress_tracker and self.progress_bar:
                try:
                    state = self.progress_tracker.get_state()
                    self.progress_bar.update(
                        state.get('percentage', 0),
                        state.get('current'),
                        state.get('total'),
                        state.get('error') # Pass error state to bar
                    )
                except Exception as e:
                    self._output_and_log("ERROR", f"Fehler beim Aktualisieren der Progress Bar nach Schritt '{name}': {e}")
                    # Consider disabling the bar if updates fail repeatedly
                    # self.progress_bar = None

            # Optional: Decide whether to stop processing on error
            # if not current_step_success:
            #     self._output_and_log("ERROR", f"Breche Generierung nach Fehler in Schritt '{name}' ab.")
            #     break


        # --- Final Summary ---
        end_time = time.time()
        total_duration = end_time - start_time
        self._output_and_log("INFO", "\n========================================")

        final_error_msg = "Unbekannter Fehler oder Fehler in vorherigen Schritten."
        final_error_details = None
        if self.progress_tracker:
            try:
                final_state = self.progress_tracker.get_state()
                final_error_details = final_state.get('error')
                if final_error_details:
                    final_error_msg = str(final_error_details)
            except Exception as e:
                self._log("ERROR", f"Fehler beim Abrufen des finalen Tracker-Status: {e}")
                final_error_msg = f"Fehler beim Abrufen des finalen Status ({e})"
                if not global_success: # If we already knew about failure, keep that status
                    pass
                else: # If this is the first indication of failure
                    global_success = False


        if global_success:
            self._output_and_log(
                "INFO", f"Alle Generierungsschritte erfolgreich abgeschlossen in {total_duration:.2f} Sekunden.")
            if self.progress_bar:
                 try:
                     self.progress_bar.complete(success=True)
                 except Exception as e:
                      self._log("ERROR", f"Fehler beim Abschliessen der Progress Bar (Erfolg): {e}")
        else:
            self._output_and_log(
                "ERROR", f"Dateigenerierung mit FEHLERN abgeschlossen nach {total_duration:.2f} Sekunden.")
            if self.progress_bar:
                try:
                    # Provide a concise final message for the bar
                    bar_msg = f"Abgeschlossen mit Fehlern (letzter: {final_error_msg[:80]})"
                    self.progress_bar.complete(success=False, final_message=bar_msg)
                except Exception as e:
                    self._log("ERROR", f"Fehler beim Abschliessen der Progress Bar (Fehler): {e}")
            # Add explicit final error message via output interface too
            self._output(f"FEHLER: Generierung nicht erfolgreich. Letzter gemeldeter Fehler: {final_error_msg}")

        self._output_and_log("INFO", "========================================")