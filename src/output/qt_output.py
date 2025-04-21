from .output_interface import OutputInterface

from PySide6.QtWidgets import QTextEdit, QPlainTextEdit
from PySide6.QtCore import Slot # Für saubere Slots, falls nötig


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