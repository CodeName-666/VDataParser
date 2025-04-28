import threading
import time

class ProgressBar:
    """
    Eine wiederverwendbare Klasse zur Anzeige eines Fortschrittsbalkens in der Konsole,
    inklusive Threading-Logik zur automatischen Aktualisierung des Fortschritts.

    Beispiel:
        def long_running_task(progress):
            # Hier wird progress['current'] und progress['percentage'] während der Verarbeitung aktualisiert.
            for i in range(1, 101):
                time.sleep(0.05)
                with progress['lock']:
                    progress['current'] = i
                    progress['percentage'] = i
        progress_bar = ProgressBar(length=50)
        error = progress_bar.run_with_progress(target=long_running_task, args=())
    """
    
    def __init__(self, length: int = 50, update_interval: float = 0.1) -> None:
        """
        Initialisiert den ProgressBar.
        
        Args:
            length (int): Die Länge des Fortschrittsbalkens.
            update_interval (float): Zeit in Sekunden zwischen den Aktualisierungen.
        """
        self.length = length
        self.update_interval = update_interval
        self.progress = {
            'lock': threading.Lock(),
            'current': 0,
            'percentage': 0,
            'error': False
        }

    def update(self, percentage: int) -> None:
        """
        Aktualisiert den Fortschrittsbalken in der Konsole.
        
        Args:
            percentage (int): Aktueller Fortschritt in Prozent.
        """
        filled_length = int(self.length * percentage // 100)
        bar = '#' * filled_length + '-' * (self.length - filled_length)
        print(f'\r>> Progress: |{bar}| {percentage}% Complete', end='')

    def complete(self) -> None:
        """
        Zeigt den abgeschlossenen Fortschrittsbalken an und beendet die Ausgabe mit einem Zeilenumbruch.
        """
        self.update(100)
        print()

    def run_with_progress(self, target, args=()) -> bool:
        """
        Führt die übergebene Funktion in einem separaten Thread aus und überwacht den Fortschritt.
        
        Args:
            target (Callable): Die Funktion, die ausgeführt werden soll. Diese muss als letzten Parameter
                               das progress-Dictionary erwarten.
            args (tuple): Argumente für die Ziel-Funktion (ohne das progress-Dictionary).
        
        Returns:
            bool: Den Fehlerstatus; True, wenn ein Fehler auftrat, sonst False.
        """
        # Erweitere die Argumente um das progress dictionary
        new_args = args + (self.progress,)
        thread = threading.Thread(target=target, args=new_args)
        thread.start()
        
        # Überwache den Fortschritt, solange der Thread läuft
        while thread.is_alive():
            with self.progress['lock']:
                percentage = self.progress['percentage']
            self.update(percentage)
            time.sleep(self.update_interval)
        
        self.complete()
        return self.progress['error']
