# --- progress_bar_abstraction.py ---
import abc
from typing import Optional, Callable, Any, Dict, Tuple
import threading

# Import the INTERFACE, not the implementation
try:
    from ..tracker.progress_tracker_abstraction import ProgressTrackerAbstraction
except ImportError:
    ProgressTrackerInterface = None # type: ignore

# Conditional import of CustomLogger
try:
    from log import CustomLogger
except ImportError:
    CustomLogger = None

class ProgressBarAbstraction(abc.ABC):
    """
    Abstrakte Basisklasse für Fortschrittsanzeigen.
    Definiert die gemeinsame Schnittstelle für verschiedene Implementierungen
    (z.B. Konsole, Qt GUI).
    """

    def __init__(self,
                 description: str = "Fortschritt",
                 update_interval: float = 0.1,
                 logger: Optional[CustomLogger] = None):
        """
        Initialisiert die Basis-Progressbar.

        Args:
            description: Eine Beschreibung der Aufgabe.
            update_interval: Das Intervall in Sekunden, in dem der Fortschritt abgefragt wird.
            logger: Ein optionales CustomLogger-Objekt für die Protokollierung.
        """
        self.description = description
        self.update_interval = update_interval
        self.logger = logger
        self._stop_event = threading.Event()
        self._progress_thread: Optional[threading.Thread] = None
        # Store the latest known state, useful for subclasses
        self._current_state: Dict[str, Any] = {'percentage': 0, 'current': 0, 'total': 100, 'error': None}


    def _log(self, level: str, message: str):
        """Helper zum Loggen von Nachrichten, falls ein Logger vorhanden ist."""
        if self.logger:
             log_method = getattr(self.logger, level.lower(), None)
             if log_method: log_method(f"{self.__class__.__name__}: {message}")
             elif level.upper() == "ERROR":
                 print(f"ERROR: {self.__class__.__name__}: {message}", file=sys.stderr) # Fallback for errors
             # else:
             #    print(f"{level}: {self.__class__.__name__}: {message}") # Optional: Fallback for other levels

    @abc.abstractmethod
    def update(self, percentage: int, current: Optional[int] = None, total: Optional[int] = None, error: Optional[Exception] = None):
        """
        Aktualisiert die Anzeige mit dem gegebenen Fortschrittsstatus.
        Diese Methode muss von Unterklassen implementiert werden.

        Args:
            percentage: Der Fortschritt in Prozent (0-100).
            current: Der aktuelle Wert (optional).
            total: Der Gesamtwert (optional).
            error: Ein aufgetretener Fehler (optional).
        """
        pass

    @abc.abstractmethod
    def _monitor_progress(self, tracker: ProgressTrackerAbstraction):
        """
        Interne Methode (normalerweise in einem Thread ausgeführt), die den
        Status vom Tracker abfragt und die `update`-Methode aufruft.
        Muss von Unterklassen implementiert werden, um die spezifische
        Update-Logik (z.B. GUI-Thread-Sicherheit) zu handhaben.
        """
        pass

    @abc.abstractmethod
    def run_with_progress(self, target: Callable[..., Any], args: Tuple = (), kwargs: Optional[Dict[str, Any]] = None, tracker: ProgressTrackerAbstraction) -> Optional[Exception]:
        """
        Führt die `target`-Funktion aus und zeigt währenddessen den Fortschritt an.

        Args:
            target: Die auszuführende Funktion.
            args: Argumente für die target-Funktion.
            kwargs: Keyword-Argumente für die target-Funktion.
            tracker: Das ProgressTrackerInterface-Objekt, das von 'target' aktualisiert wird.

        Returns:
            Optional[Exception]: Der Fehler, der im Tracker gesetzt wurde oder während
                                 der Ausführung von 'target' aufgetreten ist, oder None bei Erfolg.
        """
        pass

    @abc.abstractmethod
    def complete(self, success: bool = True, final_message: Optional[str] = None):
        """
        Schließt die Fortschrittsanzeige ab.
        Muss von Unterklassen implementiert werden (z.B. um eine letzte Nachricht
        anzuzeigen, die GUI zu schließen oder eine neue Zeile in der Konsole auszugeben).

        Args:
            success: Ob die Aufgabe erfolgreich abgeschlossen wurde.
            final_message: Eine optionale Abschlussnachricht.
        """
        pass

# --- END OF FILE progress_bar_abstraction.py ---