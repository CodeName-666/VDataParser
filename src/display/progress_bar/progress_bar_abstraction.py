# --- progress_bar_abstraction.py ---
import abc
from typing import Optional, Callable, Any, Dict, Tuple
import threading

# Import the INTERFACE, not the implementation
try:
    from ..tracker.progress_tracker_abstraction import ProgressTrackerAbstraction
except ImportError:
    ProgressTrackerInterface = None  # type: ignore

# Conditional import of CustomLogger
try:
    from src.log import CustomLogger
except ImportError:
    CustomLogger = None


class ProgressBarAbstraction(abc.ABC):
    """Abstract base class for visual progress bars."""

    def __init__(
        self,
        description: str = "Progress",
        update_interval: float = 0.1,
        logger: Optional[CustomLogger] = None,
    ) -> None:
        """Initialise the base progress bar."""
        self.description = description
        self.update_interval = update_interval
        self.logger = logger
        self._stop_event = threading.Event()
        self._progress_thread: Optional[threading.Thread] = None
        # Store the latest known state, useful for subclasses
        self._current_state: Dict[str, Any] = {'percentage': 0, 'current': 0, 'total': 100, 'error': None}

    def _log(self, level: str, message: str) -> None:
        """Helper to log ``message`` if a logger was supplied."""
        if self.logger:
            log_method = getattr(self.logger, level.lower(), None)
            if log_method:
                log_method(f"{self.__class__.__name__}: {message}")
            elif level.upper() == "ERROR":
                print(f"ERROR: {self.__class__.__name__}: {message}", file=sys.stderr)  # Fallback for errors
            # else:
            #    print(f"{level}: {self.__class__.__name__}: {message}") # Optional: Fallback for other levels

    @abc.abstractmethod
    def update(
        self,
        percentage: int,
        current: Optional[int] = None,
        total: Optional[int] = None,
        error: Optional[Exception] = None,
    ) -> None:
        """Update the visual representation with ``percentage`` and status."""
        raise NotImplementedError

    @abc.abstractmethod
    def _monitor_progress(self, tracker: ProgressTrackerAbstraction) -> None:
        """Internal helper watching ``tracker`` and calling :meth:`update`."""
        raise NotImplementedError

    @abc.abstractmethod
    def run_with_progress(
        self,
        target: Callable[..., Any],
        args: Tuple = (),
        kwargs: Optional[Dict[str, Any]] = None,
        tracker: ProgressTrackerAbstraction | None = None,
    ) -> Optional[Exception]:
        """Execute ``target`` while displaying progress."""
        raise NotImplementedError

    @abc.abstractmethod
    def complete(self, success: bool = True, final_message: Optional[str] = None) -> None:
        """Finalize the display and optionally show ``final_message``."""
        raise NotImplementedError

# --- END OF FILE progress_bar_abstraction.py ---
