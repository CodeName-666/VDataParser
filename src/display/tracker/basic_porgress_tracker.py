# --- basic_progress_tracker.py ---
import threading
from typing import Dict, Any, Optional

# Import the interface
from .progress_tracker_abstraction import ProgressTrackerAbstraction


class BasicProgressTracker(ProgressTrackerAbstraction):
    """
    Eine grundlegende, Thread-sichere Implementierung des ProgressTrackerInterface.
    Verwaltet den Zustand und bietet Methoden zur Aktualisierung und Abfrage.
    Diese Implementierung benachrichtigt nicht aktiv über Änderungen (Polling-basiert).
    """

    def __init__(self, total: int = 100):
        """
        Initialisiert den Tracker.

        Args:
            total (int): Der Gesamtwert, der 100% Fortschritt entspricht. Muss >= 0 sein.

        Raises:
            ValueError: Wenn total negativ ist.
        """
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
        """Setzt den Fortschritt zurück und optional den Gesamtwert neu."""
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
        """Erhöht den aktuellen Fortschrittswert."""
        if value < 0:
            raise ValueError(
                f"Versuch, Fortschritt um negativen Wert {value} zu erhöhen.")
        with self._lock:
            self._current += value
            # Neuberechnung, da sich current geändert hat
            self._calculate_percentage_unsafe()

    def set_progress(self, current: int) -> None:
        """Setzt den aktuellen Fortschrittswert direkt."""
        if current < 0:
            raise ValueError(
                f"Versuch, Fortschritt auf negativen Wert {current} zu setzen.")
        with self._lock:
            self._current = current
            # Neuberechnung, da sich current geändert hat
            self._calculate_percentage_unsafe()

    def set_percentage(self, percentage: int) -> None:
        """Setzt den Prozentsatz direkt (0-100). Passt 'current' näherungsweise an."""
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
        """Markiert den Tracker mit einem Fehler."""
        with self._lock:
            self._error = error
            # Optional: Setze Prozentsatz auf bestimmten Wert bei Fehler? Z.B. 100 oder 0?
            # Hängt vom Anwendungsfall ab. Aktuell bleibt er unverändert.

    def _calculate_percentage_unsafe(self) -> None:
        """
        Berechnet den Prozentsatz. Muss innerhalb eines Locks aufgerufen werden!
        """
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
        """Gibt den aktuellen Fortschrittswert zurück."""
        with self._lock:
            return self._current

    @property
    def total(self) -> int:
        """Gibt den Gesamtwert zurück, der 100% entspricht."""
        # Total ist nach Initialisierung konstant (außer bei reset), kein Lock nötig?
        # Sicherer mit Lock, falls total doch änderbar gemacht wird.
        with self._lock:
            return self._total

    @property
    def percentage(self) -> int:
        """Gibt den aktuellen Fortschritt in Prozent (0-100) zurück."""
        with self._lock:
            # Stelle sicher, dass der Wert aktuell ist, falls z.B. nur current geändert wurde
            # _calculate_percentage_unsafe() # Wird jetzt in increment/set_progress etc. aufgerufen
            return self._percentage

    @property
    def error(self) -> Optional[Exception]:
        """Gibt den aufgetretenen Fehler zurück oder None."""
        with self._lock:
            return self._error

    @property
    def has_error(self) -> bool:
        """Gibt True zurück, wenn ein Fehler aufgetreten ist."""
        with self._lock:
            return self._error is not None

    def get_state(self) -> Dict[str, Any]:
        """Gibt den aktuellen Zustand als Dictionary zurück."""
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
