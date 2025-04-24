# --- file_generator.py ---
from pathlib import Path
import time

# Annahme: Benötigte Objekte sind in 'objects.py' und Logger in 'log.py'
try:
    from objects import FleatMarket # Nur FleatMarket benötigt
    from log import logger
except ImportError:
    print("WARNUNG: Konnte 'objects' oder 'log' nicht importieren. Stellen Sie sicher, dass diese Module existieren.")
    # Dummy-Implementierungen
    class FleatMarket: pass # Leere Klasse reicht hier
    class Logger:
        def info(self, msg): print(f"INFO: {msg}")
        def warning(self, msg): print(f"WARN: {msg}")
        def error(self, msg): print(f"ERROR: {msg}")
        def debug(self, msg): print(f"DEBUG: {msg}")
    logger = Logger()

# Importiere alle benötigten Generatoren und Hilfsklassen
from .price_list_generator import PriceListGenerator
from .seller_data_generator import SellerDataGenerator
from .statistic_data_generator import StatisticDataGenerator
from .receive_info_pdf_generator import ReceiveInfoPdfGenerator
# Annahme: ProgressTracker und ConsoleProgressBar existieren
try:
    from .progress_tracker import ProgressTracker
    from .console_progress_bar import ConsoleProgressBar
except ImportError:
    logger.error("FEHLER: ProgressTracker oder ConsoleProgressBar nicht gefunden. Gesamtfortschritt nicht verfügbar.")
    ProgressTracker = None
    ConsoleProgressBar = None


class FileGenerator:
    """
    Orchestriert die Generierung verschiedener Dateien für einen Flohmarkt
    (Preisliste, Verkäuferdaten, Statistik, Abholbestätigung-PDF)
    und zeigt den Gesamtfortschritt an, falls die entsprechenden Klassen verfügbar sind.
    """

    def __init__(self,
                 fleat_market_data: FleatMarket,
                 output_path: str = 'output', # Standard-Ausgabeverzeichnis
                 seller_file_name: str = "kundendaten",
                 price_list_file_name: str = "preisliste",
                 statistic_file_name: str = "versand",
                 pdf_template_path_input: str = 'template/template.pdf', # Beispiel-Template-Pfad
                 pdf_output_file_name: str = 'Abholbestaetigungen.pdf' # Name der PDF-Datei
                 ) -> None:
        """
        Initialisiert den FileGenerator und alle untergeordneten Generatoren.

        Args:
            fleat_market_data (FleatMarket): Das zentrale Datenobjekt für den Flohmarkt.
            output_path (str): Das Hauptverzeichnis für alle generierten Dateien.
            seller_file_name (str): Dateiname (ohne Endung) für die Verkäuferdaten.
            price_list_file_name (str): Dateiname (ohne Endung) für die Preisliste.
            statistic_file_name (str): Dateiname (ohne Endung) für die Statistikdatei.
            pdf_template_path_input (str): Vollständiger Pfad zur PDF-Vorlagedatei.
            pdf_output_file_name (str): Dateiname (mit Endung) für die generierte PDF-Datei.
        """
        self.output_path = Path(output_path) if output_path else Path('.')
        self.fleat_market_data = fleat_market_data
        self.pdf_template_path = pdf_template_path_input
        self.pdf_output_filename = pdf_output_file_name # Behalte den vollen Namen

        # Stelle sicher, dass das Ausgabeverzeichnis existiert
        try:
            self.verify_output_path(self.output_path)
        except Exception as e:
             logger.error(f"Konnte Ausgabepfad '{self.output_path}' nicht erstellen. Fehler: {e}")
             # Entscheiden, ob hier abgebrochen werden soll
             raise RuntimeError(f"Ausgabepfad '{self.output_path}' konnte nicht erstellt werden.") from e

        # Generatoren initialisieren - übergebe das output_path als String
        output_path_str = str(self.output_path)
        self.__seller_generator = SellerDataGenerator(
            fleat_market_data, output_path_str, seller_file_name
        )
        self.__price_list_generator = PriceListGenerator(
            fleat_market_data, output_path_str, price_list_file_name
        )
        self.__statistic_generator = StatisticDataGenerator(
            fleat_market_data, output_path_str, statistic_file_name
        )
        # PDF Generator braucht Pfad zum Template und den Namen der Output-Datei
        self.__receive_info_pdf_generator = ReceiveInfoPdfGenerator(
            fleat_market_data,
            output_path_str, # Ausgabeverzeichnis
            pdf_template_path_input,
            pdf_output_file_name # Name der Zieldatei
            # Optional: coordinates hier übergeben, falls nicht Standard
        )

        # Liste der Generierungsaufgaben (Name für Logging, Instanz)
        self.generation_tasks = [
            ("Verkäuferdaten (.dat)", self.__seller_generator),
            ("Preisliste (.dat)", self.__price_list_generator),
            ("Statistikdaten (.dat)", self.__statistic_generator),
            ("Abholbestätigung (.pdf)", self.__receive_info_pdf_generator),
        ]
        self.total_steps = len(self.generation_tasks)

        # Tracker und Bar für den Gesamtfortschritt, falls verfügbar
        self.__overall_tracker = None
        self.__overall_progress_bar = None
        if ProgressTracker and ConsoleProgressBar:
             self.__overall_tracker = ProgressTracker(total=self.total_steps)
             self.__overall_progress_bar = ConsoleProgressBar(length=60, description="Gesamtfortschritt")
        else:
             logger.warning("Fortschrittsanzeige nicht initialisiert (Tracker oder Bar fehlt).")


    def verify_output_path(self, path: Path):
        """ Stellt sicher, dass der Ausgabepfad existiert. Wirft Fehler bei Problemen. """
        path.mkdir(parents=True, exist_ok=True)
        logger.debug(f"Ausgabepfad sichergestellt: {path.resolve()}")


    def generate(self):
        """
        Führt alle konfigurierten Generierungsaufgaben nacheinander aus
        und zeigt den Gesamtfortschritt an (falls Tracker/Bar verfügbar sind).
        """
        logger.info(f"Starte Gesamt-Dateigenerierung nach '{self.output_path.resolve()}'...")
        if not self.fleat_market_data:
             logger.error("Keine Flohmarktdaten übergeben. Generierung abgebrochen.")
             return

        start_time = time.time()
        global_success = True

        # Tracker zurücksetzen, falls vorhanden
        if self.__overall_tracker:
            self.__overall_tracker.reset(total=self.total_steps)
            # Initialen Stand der Bar anzeigen
            state = self.__overall_tracker.get_state()
            if self.__overall_progress_bar:
                 self.__overall_progress_bar.update(state['percentage'], state['current'], state['total'])

        for name, generator_instance in self.generation_tasks:
            logger.info(f"\n--- Starte Schritt: {name} ---")
            step_start_time = time.time()
            try:
                # Führe die generate-Methode des Generators aus
                # Übergebe den Gesamt-Tracker, damit der Generator ihn inkrementieren kann
                generator_instance.generate(overall_tracker=self.__overall_tracker)

                step_duration = time.time() - step_start_time
                logger.info(f"--- Schritt '{name}' beendet (Dauer: {step_duration:.2f}s) ---")

                # Fortschrittsanzeige aktualisieren, falls vorhanden
                if self.__overall_tracker and self.__overall_progress_bar:
                    state = self.__overall_tracker.get_state()
                    self.__overall_progress_bar.update(state['percentage'], state['current'], state['total'])

                    # Prüfe auf Fehler, die im Schritt aufgetreten sein könnten (durch tracker.set_error)
                    if state['error']:
                         logger.error(f"!! Fehler während Schritt '{name}': {state['error']}. Fortfahren...")
                         global_success = False # Markiere Gesamtprozess als fehlerhaft
                         # Hier entscheiden: Abbrechen oder weitermachen?
                         # Aktuell: Weitermachen mit nächstem Schritt

            except NotImplementedError:
                 logger.error(f"Fehler: Die 'generate'-Methode ist für '{name}' nicht implementiert.")
                 global_success = False
                 if self.__overall_tracker:
                      self.__overall_tracker.set_error(NotImplementedError(f"generate für {name} fehlt"))
                      self.__overall_tracker.increment() # Trotzdem Schritt zählen
                 if self.__overall_tracker and self.__overall_progress_bar: # Update Bar nach Fehler
                      state = self.__overall_tracker.get_state()
                      self.__overall_progress_bar.update(state['percentage'], state['current'], state['total'])

            except Exception as e:
                step_duration = time.time() - step_start_time
                logger.error(f"!! Unerwarteter FEHLER während Schritt '{name}' nach {step_duration:.2f}s: {e}", exc_info=True) # Log Traceback
                global_success = False
                if self.__overall_tracker:
                    self.__overall_tracker.set_error(e) # Fehler im Tracker speichern
                    # Sicherstellen, dass der Schritt gezählt wird, auch wenn die Generator-Methode abstürzt
                    # Check current progress vs expected progress
                    current_prog = self.__overall_tracker.current
                    expected_prog = self.generation_tasks.index((name, generator_instance)) + 1
                    if current_prog < expected_prog:
                         self.__overall_tracker.increment()
                if self.__overall_tracker and self.__overall_progress_bar: # Update Bar nach Fehler
                    state = self.__overall_tracker.get_state()
                    self.__overall_progress_bar.update(state['percentage'], state['current'], state['total'])
                # Hier entscheiden: Abbrechen oder weitermachen?
                # break # Beispiel für Abbruch


        # Gesamtprozess abschließen
        end_time = time.time()
        total_duration = end_time - start_time

        logger.info("\n========================================")
        if global_success:
            logger.info(f"Alle Generierungsschritte abgeschlossen in {total_duration:.2f} Sekunden.")
            if self.__overall_progress_bar:
                self.__overall_progress_bar.complete(success=True)
        else:
            logger.error(f"Dateigenerierung mit FEHLERN abgeschlossen nach {total_duration:.2f} Sekunden.")
            final_error = self.__overall_tracker.error if self.__overall_tracker else "Unbekannter Fehler"
            if self.__overall_progress_bar:
                 self.__overall_progress_bar.complete(success=False, final_message=f"Abgeschlossen mit Fehlern (letzter: {str(final_error)[:80]})")

        logger.info("========================================")

    # set_... Methoden sind nicht mehr nötig, da Namen im __init__ übergeben werden