import logging
import inspect
import threading
from typing import List, Dict

class OneLineData:
    """
    Speichert One-Line-Log-Daten.

    Attribute:
    -----------
    enabled : bool
        Gibt an, ob das One-Line-Logging aktiv ist.
    data : str
        Die akkumulierten Log-Daten.
    """
    def __init__(self, enabled: bool = False, data: str = "") -> None:
        self.enabled = enabled
        self.data = data


class LogHelper:
    """
    Verwaltet One-Line-Log-Daten für verschiedene Log-Typen.
    
    Intern werden Thread-Locks genutzt, um in multi-threading Umgebungen
    Race Conditions zu vermeiden.
    """
    def __init__(self) -> None:
        self._one_line_data: Dict[str, List[OneLineData]] = {
            "INFO": [],
            "WARNING": [],
            "DEBUG": [],
            "ERROR": []
        }
        self._skip_logging: Dict[str, bool] = {
            "INFO": False,
            "WARNING": False,
            "DEBUG": False,
            "ERROR": False
        }
        self._lock = threading.Lock()

    def log_new_one_line(self, log_type: str) -> None:
        """Startet ein neues One-Line-Log für den angegebenen Log-Typ."""
        with self._lock:
            self._one_line_data[log_type].append(OneLineData(enabled=True))

    def log(self, log_type: str, data: str) -> None:
        """
        Hängt Daten an das aktive One-Line-Log des angegebenen Log-Typs an.
        """
        with self._lock:
            if not self._skip_logging.get(log_type, False) and self._one_line_data[log_type]:
                self._one_line_data[log_type][-1].data += data

    def is_log_enabled(self, log_type: str) -> bool:
        """
        Überprüft, ob für den angegebenen Log-Typ One-Line-Logging aktiv ist.
        """
        with self._lock:
            if self._one_line_data[log_type]:
                return self._one_line_data[log_type][-1].enabled
            return False

    def stop_line_log(self, log_type: str) -> str:
        """
        Beendet das aktuelle One-Line-Log für den angegebenen Log-Typ
        und gibt den akkumulierten Log-Inhalt zurück.
        """
        with self._lock:
            if self._one_line_data[log_type]:
                one_line = self._one_line_data[log_type][-1]
                one_line.enabled = False
                return one_line.data
            return ""

    def delete_line_log(self, log_type: str) -> None:
        """
        Löscht das aktuell aktive One-Line-Log des angegebenen Log-Typs.
        """
        with self._lock:
            if self._one_line_data[log_type]:
                self._one_line_data[log_type].pop()

    def skip_logging(self, log_type: str, status: bool) -> None:
        """
        Setzt, ob für einen angegebenen Log-Typ das Logging übersprungen werden soll.
        """
        with self._lock:
            self._skip_logging[log_type] = status

    def is_logging_skipped(self, log_type: str) -> bool:
        """
        Gibt an, ob für den angegebenen Log-Typ das Logging derzeit übersprungen wird.
        """
        with self._lock:
            return self._skip_logging.get(log_type, False)


class CustomLogger:
    """
    Eine verbesserte Logging-Klasse, die sowohl Standard- als auch One-Line-Logging unterstützt.
    
    Die Klasse kapselt die LogHelper-Funktionalität, verwendet offizielle Logging-APIs
    und bietet Thread-Sicherheit.
    """
    def __init__(self, log_level: str = "INFO", verbose_enabled: bool = False) -> None:
        self._verbose = verbose_enabled
        self._logger = logging.getLogger(__name__)
        # Konfiguration mittels offizieller API, Level über getattr auf dem logging-Modul.
        numeric_level = getattr(logging, log_level.upper(), logging.INFO)
        logging.basicConfig(level=numeric_level, format='%(levelname)s: %(message)s')
        self._log_helper = LogHelper()
        self._level_mapping = {
            "INFO": logging.INFO,
            "WARNING": logging.WARNING,
            "DEBUG": logging.DEBUG,
            "ERROR": logging.ERROR
        }

    def indentation_depth(self) -> str:
        """
        Berechnet die Einrückung basierend auf der Tiefe des Aufrufstapels.
        Hier wird ein Offset verwendet, um interne Aufrufe herauszurechnen.
        """
        depth = max(len(inspect.stack()) - 12, 0)
        indentation_value = ".."
        return indentation_value * depth

    def skip_logging(self, log_type: str, status: bool) -> None:
        """
        Setzt für den angegebenen Log-Typ das Überspringen des Loggings.
        """
        self._log_helper.skip_logging(log_type, status)

    def _log(self, log_type: str, msg: str, on_verbose: bool = False) -> None:
        """
        Führt das Logging durch. Bei aktivem One-Line-Logging wird der Text angehängt,
        ansonsten wird der Log direkt über die entsprechende Logging-Methode ausgegeben.
        """
        if on_verbose and not self._verbose:
            return

        if not self._log_helper.is_log_enabled(log_type):
            if msg and not self._log_helper.is_logging_skipped(log_type):
                level = self._level_mapping.get(log_type, logging.INFO)
                self._logger.log(level, msg)
            self._log_helper.delete_line_log(log_type)
        else:
            self._log_helper.log(log_type, msg)

    def log_one_line(self, log_type: str, enabled: bool = True) -> None:
        """
        Schaltet das One-Line-Logging für einen bestimmten Log-Typ ein oder aus.
        Bei Deaktivierung wird der akkumulierte Log ausgegeben.
        """
        if enabled:
            self._log_helper.log_new_one_line(log_type)
        else:
            log_data = self._log_helper.stop_line_log(log_type)
            self._log(log_type, log_data)

    def debug(self, msg: str, on_verbose: bool = False) -> None:
        """Loggt eine Debug-Nachricht."""
        self._log("DEBUG", msg, on_verbose)

    def info(self, msg: str, on_verbose: bool = False) -> None:
        """Loggt eine Info-Nachricht."""
        self._log("INFO", msg, on_verbose)

    def warning(self, msg: str, on_verbose: bool = False) -> None:
        """Loggt eine Warning-Nachricht."""
        self._log("WARNING", msg, on_verbose)

    def error(self, msg: str, on_verbose: bool = False) -> None:
        """Loggt eine Error-Nachricht."""
        self._log("ERROR", msg, on_verbose)

    def verbose(self) -> bool:
        """Gibt zurück, ob der Verbose-Modus aktiviert ist."""
        return self._verbose


# Beispiel zur Nutzung:
if __name__ == "__main__":
    logger = CustomLogger(log_level="DEBUG", verbose_enabled=True)

    # Direktes Logging
    logger.info("Dies ist eine Info-Nachricht.")
    logger.debug("Dies ist eine Debug-Nachricht.", on_verbose=True)

    # One-Line Logging: Starten, fortlaufende Logs und abschließendes Logging
    logger.log_one_line("INFO", enabled=True)
    logger.info("Teil 1...", on_verbose=True)
    logger.info("Teil 2...", on_verbose=True)
    # Beende das One-Line Logging und gebe die akkumulierte Nachricht aus.
    logger.log_one_line("INFO", enabled=False)
