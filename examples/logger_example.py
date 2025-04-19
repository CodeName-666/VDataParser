import sys
from pathlib import Path
import logging

sys.path.insert(0, Path(__file__).parent.parent.__str__())
from src.log.logger import CustomLogger



def example_2():
    # --- Beispiel für die Verwendung des 'handler'-Parameters ---

    print("\n--- Beispiel: Logging in eine Datei mittels benutzerdefiniertem Handler ---")

    # 1. Logdatei definieren
    log_filename = "app_activity.log"

    # 2. Einen FileHandler erstellen und konfigurieren
    try:
        # mode='w' überschreibt die Datei bei jedem Start, 'a' hängt an
        file_handler = logging.FileHandler(log_filename, mode='w', encoding='utf-8')

        # Optional: Setze ein Level speziell für diesen Handler
        # Nur Nachrichten dieses Levels oder höher werden vom Handler verarbeitet
        file_handler.setLevel(logging.DEBUG)

        # Hinweis: CustomLogger wird seinen eigenen Formatter auf diesen Handler anwenden,
        # basierend auf den 'log_format' und 'date_format' Parametern, die an
        # CustomLogger übergeben werden. Wenn du einen *anderen* Formatter *nur* für
        # diese Datei willst, müsstest du die CustomLogger-Klasse anpassen oder
        # den Formatter *nach* der Initialisierung von CustomLogger setzen.

    except IOError as e:
        print(f"Fehler beim Erstellen des FileHandlers für '{log_filename}': {e}")
        # Fallback oder Fehlerbehandlung
        file_handler = None

    # 3. CustomLogger mit dem FileHandler initialisieren
    if file_handler:
        # Wir können hier ein spezifisches Format für die Datei definieren
        file_logger = CustomLogger(
            name="FileLogger",
            log_level="DEBUG",  # Logger-Level (Handler-Level kann restriktiver sein)
            handler=file_handler, # Den erstellten Handler übergeben
            log_format='%(asctime)s [%(levelname)-8s] %(name)s: %(message)s', # Format für die Datei
            date_format='%Y-%m-%d %H:%M:%S'
        )

        # 4. Nachrichten loggen - diese gehen jetzt in die Datei
        print(f"-> Nachrichten werden jetzt in die Datei '{log_filename}' geschrieben.")
        file_logger.info("Programm gestartet.")
        file_logger.debug("Debugging-Information: Initialisierung abgeschlossen.")

        # One-Line Logging geht auch in die Datei
        file_logger.one_line_log("INFO", start=True)
        file_logger.info("Verarbeite Daten... ")
        for i in range(3):
            file_logger.info(f"Schritt {i+1} ")
            # Simuliere Arbeit
            # time.sleep(0.1)
        file_logger.info("fertig.")
        file_logger.one_line_log("INFO", start=False) # Schreibt die gesammelte Zeile in die Datei

        file_logger.warning("Ein potenzielles Problem wurde entdeckt.")
        file_logger.error("Ein Fehler ist aufgetreten!", on_verbose=False) # Geht immer in die Datei

        print(f"-> Überprüfe den Inhalt der Datei '{log_filename}'.")

        # 5. Wichtig: Schließe den Handler, um sicherzustellen, dass alle Daten geschrieben werden
        # In einer echten Anwendung geschieht dies oft beim Beenden des Programms.
        file_handler.close()
        # oder global für alle Standard-Handler: logging.shutdown()

        # Optional: Logdatei nach dem Beispiel wieder löschen
        # try:
        #     os.remove(log_filename)
        #     print(f"-> Logdatei '{log_filename}' wurde aufgeräumt.")
        # except OSError as e:
        #     print(f"Fehler beim Löschen der Logdatei '{log_filename}': {e}")

    else:
        print("-> Konnte keinen FileHandler erstellen. Das Datei-Logging-Beispiel wird übersprungen.")

    print("\n--- Beispiel Ende ---")

    # Zum Vergleich: Ein Logger ohne spezifischen Handler (loggt auf die Konsole)
    print("\n--- Beispiel: Standard-Konsolen-Logging ---")
    console_logger = CustomLogger(name="ConsoleLogger", log_level="INFO")
    console_logger.info("Diese Nachricht geht auf die Konsole.")
    console_logger.debug("Diese Debug-Nachricht wird NICHT auf der Konsole erscheinen (Level INFO).")



def example_1():
    # Create logger instance - verbosity enabled, level DEBUG
    # Uses the default console handler and format
    logger = CustomLogger(name="MyTestApp", log_level="DEBUG", verbose_enabled=True)

    print("--- Standard Logging ---")
    logger.info("This is a standard info message.")
    logger.debug("This is a standard debug message.") # Will show because level is DEBUG
    logger.info("This verbose info message WILL appear.", on_verbose=True)

    # Test verbose disabled
    logger_non_verbose = CustomLogger(name="QuietApp", log_level="INFO", verbose_enabled=False)
    logger_non_verbose.info("This info message WILL appear.")
    logger_non_verbose.info("This verbose info message WILL NOT appear.", on_verbose=True)
    logger_non_verbose.debug("This debug message WILL NOT appear (level INFO).")


    print("\n--- One-Line Logging ---")
    logger.one_line_log("INFO", start=True)
    logger.info("Processing item 1...") # Appended
    logger.info("Item 1 done. ")        # Appended
    logger.info("Processing item 2...") # Appended
    logger.debug("This is a debug message during one-line INFO - logs separately.")
    logger.info("Item 2 done.")         # Appended
    logger.one_line_log("INFO", start=False) # Stops and logs the accumulated INFO message

    print("\n--- Nested One-Line Logging ---")
    logger.one_line_log("DEBUG", start=True) # Outer debug session
    logger.debug("Outer part 1...")
    logger.one_line_log("DEBUG", start=True) # Inner debug session
    logger.debug("Inner part A...")
    logger.debug("Inner part B...")
    logger.one_line_log("DEBUG", start=False) # Stop inner session -> logs "Inner part A...Inner part B..."
    logger.debug("Outer part 2...")
    logger.one_line_log("DEBUG", start=False) # Stop outer session -> logs "Outer part 1...Outer part 2..."


    print("\n--- Skipping Logging ---")
    logger.skip_logging("INFO", True)
    logger.info("This INFO message will be skipped.")
    logger.one_line_log("INFO", start=True)
    logger.info("This part of one-line INFO will be skipped...")
    logger.info("...and this part too.")
    logger.one_line_log("INFO", start=False) # Stops, but logging is skipped, so nothing appears
    logger.warning("This WARNING message is NOT skipped.")
    logger.skip_logging("INFO", False) # Re-enable INFO logging
    logger.info("This INFO message appears again.")


    print("\n--- Invalid Log Type Handling ---")
   
    # This part correctly demonstrates the handling of invalid types via the public API:
    try:
        # Attempt to use an invalid type with a public method that accepts log_type
        logger.one_line_log("WRONG_TYPE", start=True)
    except ValueError as e:
         # The logger itself should log an error message internally due to the try/except
         # block within one_line_log. Catching it here is optional for demonstration.
         print(f"Caught expected ValueError in example block: {e}")
    # You could also test skip_logging:
    logger.skip_logging("ANOTHER_BAD_TYPE", True) # This will also log an error internally





    # --- Example Usage ---
if __name__ == "__main__":
    #Comment in to execute example 1
    example_1()
    #Comment in to execute example 2
    #example_2()