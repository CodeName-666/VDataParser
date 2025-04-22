import sys
import time # Für Demo-Zwecke
from PySide6.QtWidgets import QApplication, QWidget
from PySide6.QtCore import QThread, Signal, Slot

# Annahme: pyside6-uic output_ui.ui -o ui_output.py wurde ausgeführt
from output_window_ui import Ui_OutputWindow

class Worker(QThread):
    """ Simuliert eine langlaufende Aufgabe mit Ausgaben """
    progress_update = Signal(int)
    log_message = Signal(str)
    finished = Signal()

    def run(self):
        total_steps = 100
        for i in range(total_steps + 1):
            time.sleep(0.05) # Simuliert Arbeit
            message = f"Schritt {i} von {total_steps} abgeschlossen."
            self.log_message.emit(message)
            percentage = int((i / total_steps) * 100)
            self.progress_update.emit(percentage)
        self.log_message.emit("--- Vorgang beendet ---")
        self.finished.emit()


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.ui = Ui_OutputWindow()
        self.ui.setupUi(self)

        self.worker = Worker()
        self.worker.log_message.connect(self.append_log)
        self.worker.progress_update.connect(self.update_progress)
        self.worker.finished.connect(self.on_worker_finished)

        # Starte den Worker, wenn das Fenster angezeigt wird (oder durch einen Button etc.)
        # Hier starten wir es direkt zur Demonstration
        self.worker.start()

    @Slot(str)
    def append_log(self, message):
        self.ui.logOutputTextEdit.appendPlainText(message) # Fügt Text hinzu und scrollt automatisch

    @Slot(int)
    def update_progress(self, value):
        self.ui.progressBar.setValue(value)

    @Slot()
    def on_worker_finished(self):
        print("Worker hat seine Arbeit beendet.")
        # Hier könnten z.B. Buttons wieder aktiviert werden

    def closeEvent(self, event):
        # Sicherstellen, dass der Thread beendet wird, wenn das Fenster geschlossen wird
        if self.worker.isRunning():
            print("Warte auf Worker-Beendigung...")
            self.worker.quit() # Signal zum Beenden senden (wenn run() einen Event Loop hätte)
            self.worker.wait() # Warten bis der Thread wirklich beendet ist
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())