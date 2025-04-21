import sys
from abc import ABC, abstractmethod

# Optional: Nur importieren, wenn Qt tatsächlich verwendet wird oder für Type Hinting
try:
    from PySide6.QtWidgets import QTextEdit, QPlainTextEdit, QApplication, QMainWindow, QVBoxLayout, QWidget
    from PySide6.QtCore import Slot # Für saubere Slots, falls nötig
    QT_AVAILABLE = True
except ImportError:
    QTextEdit = None # Dummy-Typ für Type Hinting, falls Qt nicht da ist
    QPlainTextEdit = None
    QT_AVAILABLE = False

# 1. Das "Interface" (Abstrakte Basisklasse)
# ------------------------------------------
class OutputInterface(ABC):
    """
    Abstrakte Basisklasse für Ausgabemechanismen.
    Definiert das Interface, das alle konkreten Ausgabeklassen implementieren müssen.
    """
    @abstractmethod
    def write_message(self, message: str):
        """
        Schreibt eine Nachricht an das definierte Ausgabeziel.

        Args:
            message (str): Die auszugebende Nachricht.
        """
        pass # Konkrete Klassen müssen dies implementieren

    def write_separator(self, char: str = '-', length: int = 40):
        """Eine optionale Hilfsmethode für eine Trennlinie."""
        self.write_message(char * length)


# 2. Konkrete Implementierungen
# ------------------------------------------

class ConsoleOutput(OutputInterface):
    """
    Implementierung von OutputInterface für die Standard-Konsolenausgabe (print).
    """
    def write_message(self, message: str):
        """Gibt die Nachricht auf der Konsole aus."""
        print(message)


if QT_AVAILABLE: # Definiere die QtOutput-Klasse nur, wenn PySide6 installiert ist
    class QtOutput(OutputInterface):
        """
        Implementierung von OutputInterface für die Ausgabe in ein Qt-Widget
        (z.B. QTextEdit oder QPlainTextEdit).
        """
        def __init__(self, output_widget: QTextEdit | QPlainTextEdit):
            """
            Initialisiert die QtOutput-Klasse.

            Args:
                output_widget (QTextEdit | QPlainTextEdit): Das Qt-Widget,
                                                            in das geschrieben werden soll.

            Raises:
                TypeError: Wenn das übergebene Widget nicht vom erwarteten Typ ist.
                RuntimeError: Wenn PySide6 nicht verfügbar ist.
            """
            if not QT_AVAILABLE:
                 raise RuntimeError("PySide6 ist nicht installiert oder konnte nicht importiert werden.")

            if not isinstance(output_widget, (QTextEdit, QPlainTextEdit)):
                raise TypeError("output_widget muss eine Instanz von QTextEdit oder QPlainTextEdit sein.")
            self.output_widget = output_widget

        # @Slot(str) # Kann als Slot deklariert werden, wenn von Qt-Signalen aufgerufen
        def write_message(self, message: str):
            """Fügt die Nachricht dem Qt-Widget hinzu."""
            # Wichtig: UI-Updates sollten immer im Main-GUI-Thread erfolgen.
            # Wenn diese Methode aus einem anderen Thread aufgerufen wird,
            # muss ein Signal-Slot-Mechanismus verwendet werden, um den
            # Aufruf sicher an den GUI-Thread zu übergeben.
            # Für dieses Beispiel gehen wir davon aus, dass der Aufruf sicher ist
            # oder direkt im GUI-Thread erfolgt.
            if isinstance(self.output_widget, QPlainTextEdit):
                 self.output_widget.appendPlainText(message) # Effizienter für viele Zeilen
            elif isinstance(self.output_widget, QTextEdit):
                 self.output_widget.append(message) # Unterstützt auch Rich Text


# 3. Beispiel für die Verwendung
# ------------------------------------------

class ApplicationLogic:
    """
    Eine Beispielklasse, die Ausgaben tätigen muss, aber nicht weiß wohin.
    Sie erhält einen Output Handler über Dependency Injection.
    """
    def __init__(self, output_handler: OutputInterface):
        """
        Initialisiert die Logik mit einem Output Handler.

        Args:
            output_handler (OutputInterface): Eine Instanz, die das OutputInterface implementiert.
        """
        if not isinstance(output_handler, OutputInterface):
             raise TypeError("output_handler muss eine Instanz sein, die OutputInterface implementiert.")
        self.output = output_handler

    def perform_action(self, action_name: str):
        """Führt eine Aktion aus und gibt Statusmeldungen aus."""
        self.output.write_message(f"Starte Aktion: '{action_name}'...")
        # Simulierte Arbeit
        import time
        time.sleep(0.5)
        self.output.write_message(f"Aktion '{action_name}' zur Hälfte abgeschlossen.")
        time.sleep(0.5)
        self.output.write_message(f"Aktion '{action_name}' erfolgreich beendet.")
        self.output.write_separator()


# 4. Hauptprogramm / Setup - Entscheidet, welcher Output Handler verwendet wird
# ------------------------------------------------------------------------------

if __name__ == "__main__":

    # --- Szenario 1: Konsolenausgabe ---
    print("--- Starte Konsolen-Szenario ---")
    console_handler = ConsoleOutput()
    app_logic_console = ApplicationLogic(output_handler=console_handler)
    app_logic_console.perform_action("Daten verarbeiten")
    app_logic_console.perform_action("Bericht erstellen")
    print("--- Konsolen-Szenario beendet ---\n")


    # --- Szenario 2: Qt GUI Ausgabe (nur wenn Qt verfügbar ist) ---
    if QT_AVAILABLE:
        print("--- Starte Qt GUI-Szenario ---")

        # Eine minimale Qt-Anwendung zum Testen
        class MinimalApp(QMainWindow):
            def __init__(self):
                super().__init__()
                self.setWindowTitle("Qt Output Beispiel")
                self.setGeometry(100, 100, 500, 300)

                central_widget = QWidget()
                self.setCentralWidget(central_widget)
                layout = QVBoxLayout(central_widget)

                self.log_output_area = QPlainTextEdit() # Oder QTextEdit()
                self.log_output_area.setReadOnly(True)
                layout.addWidget(self.log_output_area)

                # Erstelle den QtOutput Handler und übergebe das Widget
                qt_handler = QtOutput(self.log_output_area)

                # Erstelle die Anwendungslogik mit dem Qt Handler
                self.app_logic_gui = ApplicationLogic(output_handler=qt_handler)

                # Führe Aktionen aus (könnte auch durch Button-Klicks etc. getriggert werden)
                self.do_work()

            def do_work(self):
                # Hier wird die Logik aufgerufen, die dann ins GUI schreibt
                 self.app_logic_gui.perform_action("GUI Daten laden")
                 self.app_logic_gui.perform_action("Ansicht aktualisieren")


        qt_app = QApplication(sys.argv)
        main_window = MinimalApp()
        main_window.show()

        print("Qt Fenster geöffnet. Schließe das Fenster, um fortzufahren...")
        exit_code = qt_app.exec()
        print(f"--- Qt GUI-Szenario beendet (Exit Code: {exit_code}) ---")

    else:
        print("--- Qt GUI-Szenario übersprungen (PySide6 nicht verfügbar) ---")