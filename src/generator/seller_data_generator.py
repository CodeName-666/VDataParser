# --- seller_data_generator.py ---
from pathlib import Path
from typing import List, Optional
import time # Behalten für explizite Pausen, falls gewünscht und sinnvoll

# Annahme: Benötigte Objekte sind in 'objects.py' und Logger in 'log.py'
try:
    from objects import FleatMarket, Seller # Beispielnamen, bitte anpassen!
    from log import logger # Beispielnamen, bitte anpassen!
except ImportError:
    print("WARNUNG: Konnte 'objects' oder 'log' nicht importieren. Stellen Sie sicher, dass diese Module existieren.")
    # Dummy-Implementierungen
    class FleatMarket:
        def get_main_number_data_list(self): return []
        def get_seller_data(self, index): raise IndexError
    class Seller:
        vorname = "Unbekannt"
        nachname = "Unbekannt"
    class Logger:
        def info(self, msg): print(f"INFO: {msg}")
        def warning(self, msg): print(f"WARN: {msg}")
        def error(self, msg): print(f"ERROR: {msg}")
        def debug(self, msg): print(f"DEBUG: {msg}")
        def log_one_line(self, level, flag): pass # Dummy
    logger = Logger()

from .data_generator import DataGenerator
# Annahme: ProgressTracker existiert im selben Verzeichnis oder im PYTHONPATH
try:
    from .progress_tracker import ProgressTracker
except ImportError:
    ProgressTracker = None


class SellerDataGenerator(DataGenerator):
    """
    Generates seller data file ('kundendaten.dat').
    Format: "main_number","B",article_quantity,article_total_count
    """

    FILE_SUFFIX = 'dat'

    def __init__(self, fleat_market_data: FleatMarket, path: str = '', file_name: str = 'kundendaten') -> None:
        """
        Initializes the SellerDataGenerator.

        Args:
            fleat_market_data: The flea market data object.
            path: The output directory path.
            file_name: The name of the output file (without suffix). Default is 'kundendaten'.
        """
        super().__init__(path, file_name)
        self.__fleat_market_data: FleatMarket = fleat_market_data

    def __create_entry(self, main_number: int, article_quantity: int, article_total_value: float) -> str:
        """ Creates a formatted entry for the seller data file. """
        # Format total value with dot as decimal separator, two decimal places
        # Konvertiere zu Cent für die Ausgabe oder formatiere als Euro-String?
        # Annahme: Es soll als Ganzzahl/Float in die Datei? -> Besser als String formatieren.
        # Hier wird angenommen, dass es als Zahl (ggf. Float) in die Datei soll. Anpassen falls nötig.
        # Beispiel: article_total_value = 12.34
        # return f'"{main_number}","B",{article_quantity},{article_total_value:.2f}\n'.replace('.',',') # Komma als Dezimal?
        return f'"{main_number}","B",{article_quantity},{article_total_value}\n' # Direkt als Zahl


    def __write(self, output_data: List[str]):
        """ Writes the generated seller data entries to the file. """
        if not output_data:
            logger.info("Keine Verkäuferdaten zum Schreiben vorhanden.")
            return

        full_path = self.get_full_path()
        try:
            full_path.parent.mkdir(parents=True, exist_ok=True)
            with open(full_path, 'w', encoding='utf-8') as file: # Specify encoding
                file.writelines(output_data)
            logger.info(f"Verkäuferdaten erfolgreich geschrieben: {full_path}")
        except IOError as e:
            logger.error(f"Fehler beim Schreiben der Verkäuferdaten nach {full_path}: {e}")
        except Exception as e:
            logger.error(f"Unerwarteter Fehler beim Schreiben der Verkäuferdaten: {e}")


    def generate(self, overall_tracker: Optional[ProgressTracker] = None):
        """
        Generates seller data, logs information, writes the file,
        and updates the overall progress tracker if provided.
        """
        output_data: List[str] = []
        valid_cnt = 0
        invalid_cnt = 0
        processed_count = 0

        logger.info(f"Starte Erstellung der Verkäuferliste ({self.file_name}.{self.FILE_SUFFIX}):\n" +
                    "      ========================")
        # time.sleep(1) # Kurze Pause für Lesbarkeit, kann entfernt werden

        try:
            all_main_numbers_data = self.__fleat_market_data.get_main_number_data_list()
            total_items = len(all_main_numbers_data)
        except AttributeError:
             logger.error("FleatMarket Objekt hat keine Methode 'get_main_number_data_list'. Breche Verkäuferdaten-Generierung ab.")
             if overall_tracker:
                 overall_tracker.set_error(AttributeError("Fehlende Methode in FleatMarket"))
                 overall_tracker.increment()
             return
        except Exception as e:
             logger.error(f"Fehler beim Abrufen der Hauptnummern-Daten: {e}")
             if overall_tracker:
                 overall_tracker.set_error(e)
                 overall_tracker.increment()
             return


        for index, main_number_data in enumerate(all_main_numbers_data):
            processed_count += 1
            # Optional: Internen Fortschritt loggen/anzeigen
            # logger.debug(f"Verarbeite Eintrag {processed_count}/{total_items}...")

            # Prüfe Datenobjekt
            if not all([hasattr(main_number_data, 'is_valid'),
                        hasattr(main_number_data, 'get_main_number'),
                        hasattr(main_number_data, 'get_article_quantity'),
                        hasattr(main_number_data, 'get_article_total')]): # Name der Methode prüfen! War 'get_article_total_count' oder 'get_article_total'?
                 logger.warning(f"Unerwartetes Datenobjekt bei Index {index}. Übersprungen.")
                 invalid_cnt += 1
                 continue

            main_number_val = main_number_data.get_main_number() # Hole Wert hier

            # Versuche Verkäuferdaten zu holen
            first_name = "Unbekannt"
            second_name = "Unbekannt"
            try:
                seller: Seller = self.__fleat_market_data.get_seller_data(index)
                if hasattr(seller, 'vorname') and hasattr(seller, 'nachname'):
                     first_name = seller.vorname
                     second_name = seller.nachname
                else:
                     logger.warning(f"Seller-Objekt für Index {index} hat nicht 'vorname'/'nachname'.")
            except IndexError:
                logger.error(f"Fehler: Kein Verkäufer für Index {index} (Hauptnummer {main_number_val}) gefunden.")
                # Zähle dies als ungültig, da Daten unvollständig sind
                invalid_cnt += 1
                # Hier entscheiden: Eintrag trotzdem erstellen oder überspringen?
                # Überspringen ist sicherer, wenn Verkäuferinfo fehlt.
                continue
            except AttributeError:
                 logger.error("FleatMarket Objekt hat keine Methode 'get_seller_data'.")
                 # Schwerwiegender Fehler, evtl. abbrechen? Hier nur Log.
                 invalid_cnt += total_items - processed_count + 1 # Rest als ungültig markieren
                 break # Schleife abbrechen
            except Exception as e:
                 logger.error(f"Unerwarteter Fehler beim Holen von Verkäuferdaten für Index {index}: {e}")
                 invalid_cnt += 1
                 continue # Nächsten Eintrag versuchen


            # logger.log_one_line("INFO",True) # Könnte mit Progressbar interferieren

            if main_number_data.is_valid():
                try:
                    m_n = int(main_number_val)
                    # Annahme: quantity ist int, total ist float/Decimal
                    a_q = int(main_number_data.get_article_quantity())
                    a_t_val = main_number_data.get_article_total() # War 'get_article_total_count'? -> Anpassen!
                    a_t = float(a_t_val) if a_t_val is not None else 0.0

                    entry = self.__create_entry(m_n, a_q, a_t)
                    output_data.append(entry)
                    valid_cnt += 1
                    # Log-Level DEBUG oder INFO, je nach gewünschter Detailtiefe
                    logger.debug(f">> Verkäufer-Eintrag (OK) <<\n" +
                                f"      {first_name}, {second_name}:\n" +
                                f"           >> Stammnummer: {m_n}\n" +
                                f"           >> Anzahl Artikel: {a_q}\n" +
                                f"           >> Gesamt Wert: {a_t:.2f} EUR\n") # Annahme: a_t ist Euro-Betrag

                except (ValueError, TypeError) as e:
                     logger.error(f"Fehler bei Konvertierung der Daten für Hauptnummer {main_number_val}: {e}")
                     invalid_cnt += 1
                except Exception as e:
                     logger.error(f"Unerwarteter Fehler bei gültigem Eintrag {main_number_val}: {e}")
                     invalid_cnt += 1

            else:
                # Ungültiger Haupteintrag
                invalid_cnt += 1
                m_n_str = str(main_number_val)
                a_q_val = main_number_data.get_article_quantity()
                a_t_val = main_number_data.get_article_total() # Ggf. anpassen

                a_q_str = str(a_q_val) if a_q_val is not None else "N/A"
                a_t_str = f"{float(a_t_val):.2f} EUR" if a_t_val is not None else "N/A"

                # Fehlerdetails ermitteln (optional)
                # reasons = []
                # if a_q_val == 0: reasons.append("Anzahl=0")
                # if a_t_val == 0: reasons.append("Wert=0")
                # reason_str = f" ({', '.join(asons)})" if reasons else ""

                logger.warning(f">> Verkäufer-Eintrag (UNGÜLTIG) <<\n" +
                             f"      {first_name}, {second_name}:\n" +
                             f"           >> Stammnummer: {m_n_str}\n" +
                             f"           >> Anzahl Artikel: {a_q_str}\n" +
                             f"           >> Gesamt Wert: {a_t_str}\n")

            # logger.log_one_line("INFO",False) # Könnte mit Progressbar interferieren
            # time.sleep(0.05) # Sehr kurze Pause, fast vernachlässigbar, ggf. entfernen

        # time.sleep(0.5) # Kurze Pause vor dem Schreiben
        self.__write(output_data)
        logger.info(f"Verkäuferliste abgeschlossen: \n"+
                     "      ========================\n" +
                    f"          --> Gültige Einträge: {valid_cnt}\n" +
                    f"          --> Ungültige/Übersprungene Einträge: {invalid_cnt}\n")
        # time.sleep(1) # Pause nach Abschluss

        # Melde Abschluss dieser Aufgabe an den Gesamt-Tracker
        if overall_tracker and isinstance(overall_tracker, ProgressTracker):
            overall_tracker.increment()
        elif overall_tracker:
             logger.warning("overall_tracker wurde übergeben, ist aber kein ProgressTracker.")