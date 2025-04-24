# --- progress_tracker.py ---
import threading
from typing import Dict, Any, Optional

class ProgressTracker:
    """
    Verwaltet den Zustand eines Fortschritts (z.B. für eine Aufgabe oder einen Gesamtprozess).
    Ist Thread-sicher.
    """
    def __init__(self, total: int = 100):
        """
        Initialisiert den Tracker.

        Args:
            total (int): Der Gesamtwert, der 100% Fortschritt entspricht.
        """
        if total < 0:
             raise ValueError("Total muss nicht-negativ sein.")
        self.total = total
        self._lock = threading.Lock()
        self._current = 0
        self._percentage = 0
        self._error: Optional[Exception] = None # Speichert den Fehler, falls einer auftritt

    def reset(self, total: Optional[int] = None) -> None:
        """Setzt den Fortschritt zurück."""
        with self._lock:
            self._current = 0
            self._percentage = 0
            self._error = None
            if total is not None:
                if total < 0:
                     # Optional: Fehler werfen oder loggen statt stillschweigend zu ignorieren
                     print(f"Warnung: Versuch, total auf ungültigen Wert {total} zu setzen. Ignoriert.")
                else:
                     self.total = total
            # Neuberechnung des Prozentsatzes nach Reset
            self._calculate_percentage_unsafe()


    def increment(self, value: int = 1) -> None:
        """Erhöht den aktuellen Fortschrittswert und berechnet den Prozentsatz neu."""
        if value < 0:
            # Optional: Fehler werfen oder Warnung ausgeben
            print(f"Warnung: Versuch, Fortschritt um negativen Wert {value} zu erhöhen. Ignoriert.")
            return
        with self._lock:
            # Stelle sicher, dass current nicht über total steigt (optional, je nach Anwendungsfall)
            # self._current = min(self.total, self._current + value)
            self._current += value # Erlaube Überschreitung, Prozentsatz wird auf 100 begrenzt
            self._calculate_percentage_unsafe()

    def set_progress(self, current: int) -> None:
        """Setzt den aktuellen Fortschrittswert direkt und berechnet den Prozentsatz neu."""
        if current < 0:
            # Optional: Fehler werfen oder Warnung ausgeben
            print(f"Warnung: Versuch, Fortschritt auf negativen Wert {current} zu setzen. Ignoriert.")
            return
        with self._lock:
            # self._current = min(self.total, current) # Optional: Begrenzen
            self._current = current
            self._calculate_percentage_unsafe()

    def set_percentage(self, percentage: int) -> None:
        """Setzt den Prozentsatz direkt (0-100)."""
        with self._lock:
            if 0 <= percentage <= 100:
                self._percentage = percentage
                # Passe _current an (kann bei Rundung ungenau sein, aber gibt Richtung vor)
                if self.total > 0:
                   self._current = int(self.total * percentage / 100)
                elif percentage == 100 :
                   self._current = 1 # Setze auf 1, wenn total 0 ist und 100% erreicht wird
                else:
                   self._current = 0

            else:
                 print(f"Warnung: Versuch, Prozentsatz auf ungültigen Wert {percentage} zu setzen. Ignoriert.")


    def set_error(self, error: Exception) -> None:
        """Markiert den Tracker mit einem Fehler."""
        with self._lock:
            self._error = error

    def _calculate_percentage_unsafe(self) -> None:
        """
        Berechnet den Prozentsatz basierend auf dem aktuellen Wert und dem Gesamtwert.
        Muss innerhalb eines Locks aufgerufen werden!
        """
        if self.total > 0:
            # Stelle sicher, dass der Prozentsatz nicht über 100 geht, auch wenn current > total ist
            self._percentage = min(100, int((self._current / self.total) * 100))
        else:
            # Wenn total 0 ist: 100% wenn current > 0, sonst 0%
            self._percentage = 100 if self._current > 0 else 0

    @property
    def current(self) -> int:
        """Gibt den aktuellen Fortschrittswert zurück."""
        with self._lock:
            return self._current

    @property
    def percentage(self) -> int:
        """Gibt den aktuellen Fortschritt in Prozent zurück."""
        with self._lock:
            # Stelle sicher, dass der Wert aktuell ist, falls set_percentage verwendet wurde
            # und danach current geändert wurde (obwohl das nicht der primäre Weg ist)
            # self._calculate_percentage_unsafe() # Normalerweise nicht nötig hier
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

    @property
    def lock(self) -> threading.Lock:
        """Gibt das Lock-Objekt zurück (für externe Synchronisation, falls nötig)."""
        return self._lock

    def get_state(self) -> Dict[str, Any]:
        """Gibt den aktuellen Zustand als Dictionary zurück."""
        with self._lock:
            # Stelle sicher, dass der Prozentsatz aktuell ist vor der Rückgabe
            self._calculate_percentage_unsafe()
            return {
                'current': self._current,
                'total': self.total,
                'percentage': self._percentage,
                'error': self._error
            }