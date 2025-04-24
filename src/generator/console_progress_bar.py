# --- console_progress_bar.py ---
import sys
import time
import threading
from typing import Callable, Tuple, Any, Optional, Dict
# Annahme: ProgressTracker ist im selben Verzeichnis oder PYTHONPATH bekannt
from .progress_tracker import ProgressTracker

class ConsoleProgressBar:
    """
    Zeigt den Fortschritt eines ProgressTracker-Objekts in der Konsole an.
    Kann eine Aufgabe in einem separaten Thread ausführen und deren Fortschritt überwachen.
    """

    def __init__(self, length: int = 50, update_interval: float = 0.1, description: str = "Progress"):
        """
        Initialisiert die Konsolen-Fortschrittsanzeige.

        Args:
            length (int): Die Länge des Balkens in Zeichen. Muss positiv sein.
            update_interval (float): Zeit in Sekunden zwischen den Aktualisierungen bei `run_with_progress`.
            description (str): Eine Beschreibung, die vor dem Balken angezeigt wird.
        """
        if length <= 0:
            raise ValueError("Länge des Fortschrittsbalkens muss positiv sein.")
        self.length = length
        self.update_interval = max(0.01, update_interval) # Mindestintervall
        self.description = description
        self._last_len = 0 # Für sauberes Überschreiben der Zeile

    def update(self, percentage: int, current: Optional[int] = None, total: Optional[int] = None) -> None:
        """
        Aktualisiert die Fortschrittsanzeige in der Konsole.

        Args:
            percentage (int): Aktueller Fortschritt in Prozent (0-100).
            current (Optional[int]): Aktueller Wert (optional, für detailliertere Anzeige).
            total (Optional[int]): Gesamtwert (optional, für detailliertere Anzeige).
        """
        percentage = max(0, min(100, percentage)) # Clamp percentage
        filled_length = int(self.length * percentage // 100)
        bar = '#' * filled_length + '-' * (self.length - filled_length)

        count_str = ""
        if current is not None and total is not None and total > 0:
             count_str = f" ({current}/{total})"
        elif current is not None:
             count_str = f" ({current})"


        # Erstelle den String für die Ausgabe
        output_str = f'>> {self.description}: |{bar}| {percentage}% Complete{count_str}'

        # Berechne, wie viele Leerzeichen zum Überschreiben der alten Zeile benötigt werden
        clear_len = self._last_len - len(output_str)
        clear_str = ' ' * clear_len if clear_len > 0 else ''

        # Schreibe mit \r an den Anfang, dann den neuen String, dann Leerzeichen zum Löschen, dann flush
        sys.stdout.write(f'\r{output_str}{clear_str}')
        sys.stdout.flush()

        # Speichere die Länge der aktuellen Ausgabe für den nächsten Update-Aufruf
        self._last_len = len(output_str)


    def complete(self, success: bool = True, final_message: Optional[str] = None) -> None:
        """
        Zeigt den abgeschlossenen Fortschrittsbalken an (100% oder Fehler)
        und beendet mit Zeilenumbruch.

        Args:
            success (bool): Ob die Aufgabe erfolgreich war. Beeinflusst das Aussehen.
            final_message (Optional[str]): Eine optionale Nachricht, die nach dem Balken angezeigt wird.
        """
        if success:
            self.update(100) # Zeige 100%
            message = final_message if final_message else "Done."
        else:
            # Rote Farbe (ANSI Escape Code) - funktioniert nicht in allen Terminals
            # red_start = "\033[91m"
            # red_end = "\033[0m"
            filled_length = self.length
            bar = '!' * filled_length # Fehlerindikator
            # Error String bauen
            error_str = f'>> {self.description}: |{bar}| Failed!'
            clear_len = self._last_len - len(error_str)
            clear_str = ' ' * clear_len if clear_len > 0 else ''
            # Schreibe Fehlerindikator
            sys.stdout.write(f'\r{error_str}{clear_str}')
            sys.stdout.flush()
            self._last_len = len(error_str) # Update last length for potential next message
            message = final_message if final_message else "Error occurred."

        print(f" {message}") # Neue Zeile am Ende und ggf. Abschlussnachricht


    def run_with_progress(self,
                          target: Callable[..., None],
                          args: Tuple = (),
                          kwargs: Optional[Dict[str, Any]] = None, # Hinzugefügt für Keyword-Argumente
                          tracker: Optional[ProgressTracker] = None) -> Optional[Exception]:
        """
        Führt die übergebene Funktion in einem separaten Thread aus und überwacht den Fortschritt
        mithilfe eines ProgressTracker-Objekts.

        Args:
            target (Callable): Die Funktion, die ausgeführt werden soll.
            args (tuple): Positionsargumente für die Ziel-Funktion.
            kwargs (Optional[Dict[str, Any]]): Keyword-Argumente für die Ziel-Funktion.
            tracker (Optional[ProgressTracker]): Der Tracker, der den Fortschritt verwaltet.
                                                 Wenn None, wird ein neuer Standard-Tracker erstellt.

        Returns:
            Optional[Exception]: Der Fehler, der im Tracker gespeichert wurde, oder None bei Erfolg.
        """
        if tracker is None:
            # Erstelle einen Standard-Tracker. Die Ziel-Funktion muss ihn nicht kennen.
            # Nützlich, wenn der Fortschritt nur von außen (z.B. Zeit) geschätzt wird.
            tracker = ProgressTracker(total=1) # Minimaler Tracker

        if kwargs is None:
            kwargs = {}

        # Konvention: Wenn die target-Funktion ein 'tracker' Keyword-Argument akzeptiert,
        # übergeben wir unseren Tracker. Das erlaubt der Funktion, den Fortschritt aktiv zu melden.
        # Hier prüfen wir nicht explizit die Signatur, sondern übergeben es einfach,
        # wenn die Funktion es verwenden *könnte*.
        # Alternativ könnte man `inspect.signature` verwenden.
        # kwargs['progress_tracker'] = tracker # Beispiel, falls die Funktion 'progress_tracker' heißt

        thread = threading.Thread(target=target, args=args, kwargs=kwargs, daemon=True) # Daemon, damit Programm endet
        thread.start()

        error_occurred = False
        while thread.is_alive():
            state = tracker.get_state()
            self.update(state['percentage'], state['current'], state['total'])
            if state['error'] is not None:
                error_occurred = True
                break # Bei Fehler Überwachung abbrechen
            time.sleep(self.update_interval)

        thread.join() # Warte auf jeden Fall auf Thread-Ende

        # Finale Anzeige basierend auf dem Tracker-Status holen
        final_state = tracker.get_state()
        final_error = final_state['error']

        if final_error:
            # Fehler ist bereits im Tracker gesetzt
             self.complete(success=False, final_message=f"Error: {str(final_error)[:100]}") # Gekürzte Fehlermeldung
             return final_error
        elif error_occurred:
            # Fehler wurde während des Laufs erkannt, aber nicht explizit im Tracker gesetzt? (Sollte nicht passieren)
            self.complete(success=False, final_message="Task interrupted or failed.")
            return RuntimeError("Task failed without explicit error in tracker.")
        else:
            # Stelle sicher, dass 100% angezeigt wird
            self.update(100, final_state['total'], final_state['total'])
            self.complete(success=True)
            return None