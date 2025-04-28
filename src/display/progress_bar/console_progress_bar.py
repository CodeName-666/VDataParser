# --- console_progress_bar.py ---
import sys
import time
import threading
from typing import Optional, Callable, Dict, Any, Tuple

# Import the Abstraction
try:
    from ..progress_bar_abstraction import ProgressBarAbstraction
except ImportError:
    # Fallback if running standalone or structure differs
    try:
        from progress_bar_abstraction import ProgressBarAbstraction
    except ImportError:
        print("Error: Cannot find ProgressBarAbstraction.", file=sys.stderr)
        ProgressBarAbstraction = object # type: ignore # Basic fallback

# Import the INTERFACE, not the implementation
try:
    from .progress_tracker_interface import ProgressTrackerInterface
except ImportError:
    ProgressTrackerInterface = None # type: ignore

# Conditional import of CustomLogger (remain the same)
try:
    from log import CustomLogger
except ImportError:
    CustomLogger = None

# Inherit from the Abstraction
class ConsoleProgressBar(ProgressBarAbstraction):
    """
    Zeigt den Fortschritt einer Aufgabe in der Konsole an.
    Verwendet ein ProgressTrackerInterface zur Abfrage des Zustands.
    Implementiert ProgressBarAbstraction.
    """
    FILL_CHAR = '█'
    EMPTY_CHAR = '-'

    def __init__(self,
                 length: int = 50, # Console-specific parameter
                 description: str = "Fortschritt",
                 update_interval: float = 0.1,
                 logger: Optional[CustomLogger] = None):
        # Call the base class initializer
        super().__init__(description=description, update_interval=update_interval, logger=logger)
        self.length = length # Store console-specific length

        # _stop_event, _progress_thread, _current_state are handled by base class now
        # self._stop_event = threading.Event()
        # self._progress_thread: Optional[threading.Thread] = None
        # self._current_state: Dict[str, Any] = {'percentage': 0, 'current': 0, 'total': 100, 'error': None}


    # _log method is inherited from base class

    # Implement the abstract update method
    def update(self, percentage: int, current: Optional[int] = None, total: Optional[int] = None, error: Optional[Exception] = None):
        """Aktualisiert die Fortschrittsanzeige in der Konsole."""
        perc = max(0, min(100, percentage)) # Clamp percentage
        filled_length = int(self.length * perc / 100)
        bar = self.FILL_CHAR * filled_length + self.EMPTY_CHAR * (self.length - filled_length)

        # Build status string
        status_str = f"{perc}%"
        if current is not None and total is not None:
             status_str += f" ({current}/{total})"
        if error:
            # Truncate long error messages for display
            error_str = str(error).replace('\n', ' ')[:self.length]
            status_str = f" FEHLER: {error_str}"
            bar = '!' * self.length # Indicate error visually in the bar

        # Use carriage return to overwrite the line
        # Ensure output is encoded correctly, especially on Windows
        try:
            output = f'\r{self.description}: |{bar}| {status_str} '
            sys.stdout.write(output)
            sys.stdout.flush()
        except UnicodeEncodeError:
             # Fallback for environments with limited console encoding support
             output = f'\r{self.description}: [{perc}%] {status_str} '
             # Try simplified bar
             simple_bar = '#' * filled_length + '.' * (self.length - filled_length)
             output_with_bar = f'\r{self.description}: |{simple_bar}| {status_str} '
             try:
                 sys.stdout.write(output_with_bar.encode(sys.stdout.encoding or 'utf-8', errors='replace').decode(sys.stdout.encoding or 'utf-8'))
             except: # Final fallback
                 sys.stdout.write(output) # Attempt original simplified output
             sys.stdout.flush()


    # Implement the abstract _monitor_progress method
    def _monitor_progress(self, tracker: ProgressTrackerInterface):
        """Thread-Funktion, die den Tracker überwacht und die Anzeige aktualisiert."""
        if tracker is None:
             self._log("ERROR", "Kein Tracker zum Überwachen übergeben.")
             return

        last_state = None
        while not self._stop_event.is_set():
            try:
                current_state = tracker.get_state()

                # Nur aktualisieren, wenn sich etwas geändert hat (oder Fehler neu ist)
                # Update _current_state in the base class
                if current_state != last_state:
                    self._current_state = current_state # Store latest state
                    self.update(current_state.get('percentage', 0), # Use .get for safety
                                current_state.get('current'),
                                current_state.get('total'),
                                current_state.get('error'))
                    last_state = current_state

                    # Bei Fehler anhalten? Oder weiterlaufen lassen? Aktuell: Weiterlaufen
                    if current_state.get('error'):
                        pass # Bleibt aktiv, zeigt Fehler an

            except Exception as e:
                 # Fehler beim Abrufen des Tracker-Status
                 self._log("ERROR", f"Fehler beim Abrufen des Tracker-Status: {e}")
                 # Optional: Anzeige aktualisieren, um diesen Fehler anzuzeigen?
                 # Use the last known good state's percentage if available
                 self.update(self._current_state.get('percentage', 0), error=e)
                 self._stop_event.set() # Stop monitoring if tracker fails

            # Wartezeit, um CPU zu schonen
            stopped = self._stop_event.wait(self.update_interval)
            if stopped:
                break # Exit loop if stop event is set externally or internally

        # Letzte Aktualisierung nach Beendigung des Threads, um sicherzustellen,
        # dass der Endzustand (100% oder Fehler) angezeigt wird.
        # Use a final try-except block for robustness
        try:
            final_state = tracker.get_state()
            self._current_state = final_state
            self.update(final_state.get('percentage', 0),
                        final_state.get('current'),
                        final_state.get('total'),
                        final_state.get('error'))
        except Exception as e:
            self._log("ERROR", f"Fehler beim Abrufen des finalen Tracker-Status: {e}")
            # Show the last known state with this new error
            self.update(self._current_state.get('percentage', 0),
                        self._current_state.get('current'),
                        self._current_state.get('total'),
                        e) # Show the error about fetching final state


    # Implement the abstract run_with_progress method
    def run_with_progress(self, target: Callable[..., Any], args: Tuple = (), kwargs: Optional[Dict[str, Any]] = None, tracker: ProgressTrackerInterface) -> Optional[Exception]:
        """
        Führt eine Funktion 'target' aus und zeigt währenddessen den Fortschritt
        mithilfe des 'tracker' in der Konsole an.

        Args:
            target: Die auszuführende Funktion.
            args: Argumente für die target-Funktion.
            kwargs: Keyword-Argumente für die target-Funktion.
            tracker: Das ProgressTrackerInterface-Objekt, das von 'target' aktualisiert wird.

        Returns:
            Optional[Exception]: Der Fehler, der im Tracker gesetzt wurde oder während
                                 der Ausführung von 'target' aufgetreten ist, oder None bei Erfolg.
        """
        if not isinstance(tracker, ProgressTrackerInterface): # type: ignore # Check if it's a valid tracker
            raise ValueError("Ein gültiges ProgressTrackerInterface-Objekt muss übergeben werden.")
        if kwargs is None:
            kwargs = {}

        self._stop_event.clear()
        self._current_state = {'percentage': 0, 'current': 0, 'total': 100, 'error': None} # Reset state
        # Display initial state immediately
        self.update(self._current_state['percentage'])

        # Starte den Überwachungs-Thread
        self._progress_thread = threading.Thread(target=self._monitor_progress, args=(tracker,), daemon=True)
        self._progress_thread.start()

        task_exception = None
        try:
            # Führe die eigentliche Aufgabe aus
            target(*args, **kwargs)
        except Exception as e:
            task_exception = e
            # Stelle sicher, dass der Tracker den Fehler kennt, falls die Aufgabe ihn nicht selbst setzt
            # Check if tracker *interface* is available before calling methods
            if ProgressTrackerInterface is not None and isinstance(tracker, ProgressTrackerInterface):
                current_tracker_state = tracker.get_state()
                if not current_tracker_state.get('error'):
                    try:
                        tracker.set_error(e)
                        self._current_state = tracker.get_state() # Update local state cache
                    except Exception as tracker_err:
                        self._log("ERROR", f"Fehler beim Setzen des Fehlers im Tracker: {tracker_err}")

            self._log("ERROR", f"Ausnahme in der überwachten Aufgabe: {e}")

        # Signalisiere dem Überwachungs-Thread, dass er anhalten soll
        self._stop_event.set()
        if self._progress_thread and self._progress_thread.is_alive():
             # Wait briefly, but not indefinitely, for the monitor thread to make its final update
            self._progress_thread.join(timeout=self.update_interval * 3)

        # Hole den finalen Zustand vom Tracker (oder verwende den zuletzt bekannten)
        final_error = self._current_state.get('error') # Use cached state which monitor should have updated

        # Schreibe die Abschlusszeile (Erfolg oder Fehler)
        final_tracked_error = final_error
        combined_error = task_exception or final_tracked_error

        self.complete(success=(combined_error is None),
                      final_message=f"Fehler: {combined_error}" if combined_error else "Abgeschlossen.")

        return combined_error


    # Implement the abstract complete method
    def complete(self, success: bool = True, final_message: Optional[str] = None):
        """Schließt die Fortschrittsanzeige ab und gibt eine Endnachricht aus."""
        # The final update should have been done by _monitor_progress finishing
        # or run_with_progress after task completion.

        # Gehe zur nächsten Zeile nach Abschluss
        sys.stdout.write('\n')
        sys.stdout.flush()

        if final_message:
             # Print final message clearly
             log_level = "INFO" if success else "ERROR"
             message = f"{self.description}: {final_message}"
             print(message)
             self._log(log_level, final_message) # Log the core message


# --- END OF FILE console_progress_bar.py ---