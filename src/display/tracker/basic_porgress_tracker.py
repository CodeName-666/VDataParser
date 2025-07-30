# --- basic_progress_tracker.py ---
import threading
from typing import Dict, Any, Optional

# Import the interface
from .progress_tracker_abstraction import ProgressTrackerAbstraction


class BasicProgressTracker(ProgressTrackerAbstraction):
    """Thread safe tracker storing progress state locally."""

    def __init__(self, total: int = 100):
        """Initialise the tracker with ``total`` steps."""
        if total < 0:
            raise ValueError("Total muss nicht-negativ sein.")
        self._total = total
        self._lock = threading.Lock()
        self._current = 0
        self._percentage = 0
        self._error: Optional[Exception] = None

        # Initial percentage calculation
        self._calculate_percentage_unsafe()

    def reset(self, total: Optional[int] = None) -> None:
        """Reset progress and optionally set a new ``total`` value."""
        with self._lock:
            self._current = 0
            self._error = None
            if total is not None:
                if total < 0:
                    # Statt print -> Fehler werfen für ungültige Eingaben
                    raise ValueError(
                        f"Versuch, total auf ungültigen negativen Wert {total} zu setzen.")
                self._total = total
            # Neuberechnung des Prozentsatzes nach Reset
            self._calculate_percentage_unsafe()

    def increment(self, value: int = 1) -> None:
        """Increase progress by ``value``."""
        if value < 0:
            raise ValueError(
                f"Versuch, Fortschritt um negativen Wert {value} zu erhöhen.")
        with self._lock:
            self._current += value
            # Neuberechnung, da sich current geändert hat
            self._calculate_percentage_unsafe()

    def set_progress(self, current: int) -> None:
        """Directly set the current progress value."""
        if current < 0:
            raise ValueError(
                f"Versuch, Fortschritt auf negativen Wert {current} zu setzen.")
        with self._lock:
            self._current = current
            # Neuberechnung, da sich current geändert hat
            self._calculate_percentage_unsafe()

    def set_percentage(self, percentage: int) -> None:
        """Set the completion percentage (0-100)."""
        if not (0 <= percentage <= 100):
            raise ValueError(
                f"Versuch, Prozentsatz auf ungültigen Wert {percentage} zu setzen (muss 0-100 sein).")
        with self._lock:
            self._percentage = percentage
            # Passe _current an (kann bei Rundung ungenau sein)
            if self._total > 0:
                # Berechne den neuen 'current' Wert basierend auf dem Prozentsatz
                self._current = int(round(self._total * percentage / 100.0))
            elif percentage == 100:
                # Wenn total 0 ist, aber 100% erreicht, setzen wir current auf etwas > 0 (z.B. 1)
                # um den Zustand "abgeschlossen" darzustellen.
                # Wenn total 0, dann 1, sonst total
                self._current = 1 if self._total == 0 else self._total
            else:  # percentage < 100 und total = 0
                self._current = 0
            # Stelle sicher, dass die Berechnung konsistent ist (kann Rundungsfehler korrigieren)
            self._calculate_percentage_unsafe()

    def set_error(self, error: Exception) -> None:
        """Store ``error`` and mark progress as failed."""
        with self._lock:
            self._error = error
            # Optional: Setze Prozentsatz auf bestimmten Wert bei Fehler? Z.B. 100 oder 0?
            # Hängt vom Anwendungsfall ab. Aktuell bleibt er unverändert.

    def _calculate_percentage_unsafe(self) -> None:
        """Recompute the percentage. Caller must hold the lock."""
        if self._total > 0:
            # Begrenze Prozentsatz auf 0-100
            perc = (self._current / self._total) * 100
            # Runden statt nur int()
            self._percentage = max(0, min(100, int(round(perc))))
        else:
            # Wenn total 0 ist: 100% wenn current > 0 (oder == total, was 0 ist), sonst 0%
            # Oder: Immer 100% wenn total 0 ist? Konvention: 100% nur wenn Arbeit getan (current > 0).
            self._percentage = 100 if self._current > 0 else 0

    @property
    def current(self) -> int:
        """Return the current progress value."""
        with self._lock:
            return self._current

    @property
    def total(self) -> int:
        """Return the maximum progress value."""
        # Total ist nach Initialisierung konstant (außer bei reset), kein Lock nötig?
        # Sicherer mit Lock, falls total doch änderbar gemacht wird.
        with self._lock:
            return self._total

    @property
    def percentage(self) -> int:
        """Return progress as percentage (0‑100)."""
        with self._lock:
            # Stelle sicher, dass der Wert aktuell ist, falls z.B. nur current geändert wurde
            # _calculate_percentage_unsafe() # Wird jetzt in increment/set_progress etc. aufgerufen
            return self._percentage

    @property
    def error(self) -> Optional[Exception]:
        """Return the stored error if any."""
        with self._lock:
            return self._error

    @property
    def has_error(self) -> bool:
        """Return ``True`` if an error was set."""
        with self._lock:
            return self._error is not None

    def get_state(self) -> Dict[str, Any]:
        """Return the current state as a dictionary."""
        with self._lock:
            # Stelle sicher, dass % aktuell ist (obwohl es durch andere Methoden aktuell sein sollte)
            # self._calculate_percentage_unsafe() # Normalerweise nicht nötig, da in settern/increment aufgerufen
            return {
                'current': self._current,
                'total': self._total,
                'percentage': self._percentage,
                'error': self._error
            }

    # Kein Lock-Property nach außen geben, Kapselung wahren.
    # Interne Verwendung ist ok.

    # Keine Listener-Methoden in dieser Basisimplementierung.
