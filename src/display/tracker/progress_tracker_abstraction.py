# --- progress_tracker_interface.py ---
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional


class ProgressTrackerAbstraction(ABC):
    """Interface for objects tracking progress state."""

    @abstractmethod
    def reset(self, total: Optional[int] = None) -> None:
        """Reset the tracker and optionally set `total`."""
        pass

    @abstractmethod
    def increment(self, value: int = 1) -> None:
        """Increase the current progress value."""
        pass

    @abstractmethod
    def set_progress(self, current: int) -> None:
        """Directly set the current progress value."""
        pass

    @abstractmethod
    def set_percentage(self, percentage: int) -> None:
        """Set the completion percentage (0-100). Implementations may adjust 'current' accordingly."""
        pass

    @abstractmethod
    def set_error(self, error: Exception) -> None:
        """Store `error` as the failure state."""
        pass

    @property
    @abstractmethod
    def current(self) -> int:
        """Return the current progress value."""
        pass

    @property
    @abstractmethod
    def total(self) -> int:
        """Return the total value representing 100%."""
        pass

    @property
    @abstractmethod
    def percentage(self) -> int:
        """Return progress as a percentage."""
        pass

    @property
    @abstractmethod
    def error(self) -> Optional[Exception]:
        """Return the stored error or `None`."""
        pass

    @property
    @abstractmethod
    def has_error(self) -> bool:
        """Return `True` if an error occurred."""
        pass

    @abstractmethod
    def get_state(self) -> Dict[str, Any]:
        """
        Return a state dictionary containing at least `current`, `total`, `percentage` and `error`.
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
