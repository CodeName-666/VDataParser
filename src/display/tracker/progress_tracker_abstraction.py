# --- progress_tracker_interface.py ---
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class ProgressTrackerAbstraction(ABC):
    """
    Abstrakte Schnittstelle für einen Fortschritts-Tracker.
    Definiert die Methoden und Eigenschaften, die jede Implementierung bereitstellen muss.
    """

    @abstractmethod
    def reset(self, total: Optional[int] = None) -> None:
        """Setzt den Fortschritt zurück und optional den Gesamtwert neu."""
        pass

    @abstractmethod
    def increment(self, value: int = 1) -> None:
        """Erhöht den aktuellen Fortschrittswert."""
        pass

    @abstractmethod
    def set_progress(self, current: int) -> None:
        """Setzt den aktuellen Fortschrittswert direkt."""
        pass

    @abstractmethod
    def set_percentage(self, percentage: int) -> None:
        """Setzt den Prozentsatz direkt (0-100). Implementierungen sollten ggf. 'current' anpassen."""
        pass

    @abstractmethod
    def set_error(self, error: Exception) -> None:
        """Markiert den Tracker mit einem Fehler."""
        pass

    @property
    @abstractmethod
    def current(self) -> int:
        """Gibt den aktuellen Fortschrittswert zurück."""
        pass

    @property
    @abstractmethod
    def total(self) -> int:
        """Gibt den Gesamtwert zurück, der 100% entspricht."""
        pass

    @property
    @abstractmethod
    def percentage(self) -> int:
        """Gibt den aktuellen Fortschritt in Prozent (0-100) zurück."""
        pass

    @property
    @abstractmethod
    def error(self) -> Optional[Exception]:
        """Gibt den aufgetretenen Fehler zurück oder None."""
        pass

    @property
    @abstractmethod
    def has_error(self) -> bool:
        """Gibt True zurück, wenn ein Fehler aufgetreten ist."""
        pass

    @abstractmethod
    def get_state(self) -> Dict[str, Any]:
        """
        Gibt den aktuellen Zustand als Dictionary zurück.
        Sollte mindestens 'current', 'total', 'percentage', 'error' enthalten.
        """
        pass

    # Optional: Methode zur Benachrichtigung (Observer-Pattern).
    # Könnte hier hinzugefügt werden, wenn Implementierungen direkt benachrichtigen sollen.
    # @abstractmethod
    # def add_listener(self, listener_callback: Callable[[Dict[str, Any]], None]) -> None:
    #     pass
    #
    # @abstractmethod
    # def remove_listener(self, listener_callback: Callable[[Dict[str, Any]], None]) -> None:
    #     pass