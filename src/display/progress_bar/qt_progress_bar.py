# --- qt_progress_bar.py ---
import sys
import threading
import time
from typing import Optional, Callable, Dict, Any, Tuple


from PySide6.QtWidgets import (QApplication, QDialog, QProgressBar, QLabel,
                               QVBoxLayout, QWidget, QPushButton)
from PySide6.QtCore import Qt, Signal, Slot, QMetaObject, Q_ARG
from PySide6.QtCore import QThread

from .progress_bar_abstraction import ProgressBarAbstraction
from ..tracker.progress_tracker_abstraction import ProgressTrackerAbstraction
from log import CustomLogger


# --- Qt Progress Dialog Widget ---
class _ProgressDialog(QDialog):
    """Internal QDialog to display the progress."""
    # Signal to emit progress updates from the monitor thread to the GUI thread
    # Carries a dictionary with the state keys ('percentage', 'current', 'total', 'error')
    progress_updated_signal = Signal(dict)
    # Signal to indicate the task/monitoring is finished
    finished_signal = Signal(bool)  # True for success, False for error

    def __init__(self, description: str, parent: Optional[QWidget] = None):
        super().__init__(parent)

        self.description_text = description
        self.setWindowTitle(f"{description} - Fortschritt")
        # Make the dialog modal so it blocks interaction with parent windows
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.setMinimumWidth(400)

        # --- Widgets ---
        self.description_label = QLabel(description)
        self.description_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)  # Percentage is shown in status label

        self.status_label = QLabel("Initialisiere...")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Optional Cancel Button (requires logic in tracker/target task)
        # self.cancel_button = QPushButton("Abbrechen")
        # self.cancel_button.clicked.connect(self.request_cancel) # Need cancel logic

        # --- Layout ---
        layout = QVBoxLayout(self)
        layout.addWidget(self.description_label)
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.status_label)
        # layout.addWidget(self.cancel_button)

        # --- Connections ---
        self.progress_updated_signal.connect(self._handle_progress_update_slot)
        self.finished_signal.connect(self._handle_finished_slot)

        self._error_occurred = False

    @Slot(dict)
    def _handle_progress_update_slot(self, state: Dict[str, Any]):
        """Updates the GUI widgets based on the received state."""
        if not isinstance(state, dict):
            return  # Basic validation

        percentage = state.get('percentage', 0)
        current = state.get('current')
        total = state.get('total')
        error = state.get('error')

        # Update Progress Bar
        self.progress_bar.setValue(max(0, min(100, percentage)))

        # Update Status Label
        status_text = f"{percentage}%"
        if current is not None and total is not None:
            status_text += f" ({current}/{total})"

        if error:
            error_str = str(error).replace('\n', ' ')
            # Simple error indication in status label
            status_text = f"FEHLER: {error_str}"
            # Optional: Change style for error
            self.status_label.setStyleSheet("color: red;")
            self.progress_bar.setStyleSheet("QProgressBar::chunk { background-color: red; }")
            self._error_occurred = True
        elif self._error_occurred:
            # Reset style if error is cleared (unlikely but possible)
            self.status_label.setStyleSheet("")
            self.progress_bar.setStyleSheet("")
            self._error_occurred = False

        self.status_label.setText(status_text)

        # Update window title dynamically? Maybe too distracting.
        # self.setWindowTitle(f"{self.description_text} ({percentage}%)")

    @Slot(bool)
    def _handle_finished_slot(self, success: bool):
        """Closes the dialog when the task/monitoring finishes."""
        if success:
            self.accept()  # Closes the dialog with QDialog.Accepted status
        else:
            self.reject()  # Closes the dialog with QDialog.Rejected status

    # Placeholder for cancel logic if a cancel button is added
    # def request_cancel(self):
    #     print("Cancel requested (implement logic in tracker/task)")
    #     # This should ideally signal the tracker/target task to stop
    #     # For now, we could just close the dialog, but the task might continue
    #     # self.reject()


# --- Main Qt Progress Bar Controller Class ---
class QtProgressBar(ProgressBarAbstraction):
    """
    Zeigt den Fortschritt einer Aufgabe in einem Qt-Dialogfenster an.
    Verwendet ein ProgressTrackerInterface zur Abfrage des Zustands.
    Implementiert ProgressBarAbstraction.

    Stellt sicher, dass GUI-Updates im Qt-Hauptthread erfolgen.
    """

    def __init__(self,
                 description: str = "Fortschritt",
                 update_interval: float = 0.1,
                 logger: Optional[CustomLogger] = None,
                 parent_widget: Optional[QWidget] = None):
        """
        Initialisiert die Qt-Fortschrittsanzeige.

        Args:
            description: Eine Beschreibung der Aufgabe.
            update_interval: Das Intervall in Sekunden, in dem der Fortschritt abgefragt wird.
            logger: Ein optionales CustomLogger-Objekt für die Protokollierung.
            parent_widget: Das übergeordnete Qt-Widget (optional).
        """
        super().__init__(description=description, update_interval=update_interval, logger=logger)

        # Create the dialog instance (but don't show it yet)
        self._dialog = _ProgressDialog(description, parent=parent_widget)
        self._task_thread: Optional[threading.Thread] = None
        self._task_exception: Optional[Exception] = None

    # Implement abstract update (primarily for interface compliance, GUI uses signals)

    def update(self, percentage: int, current: Optional[int] = None, total: Optional[int] = None, error: Optional[Exception] = None):
        """
        Aktualisiert den internen Zustand und löst *potenziell* ein Signal aus.
        Normalerweise wird das Update durch das Signal vom Monitor-Thread getriggert.
        Diese Methode ist für direkte Aufrufe weniger relevant im Qt-Kontext.
        """
        new_state = {
            'percentage': percentage,
            'current': current,
            'total': total,
            'error': error
        }
        # Update internal state cache
        self._current_state = new_state
        # Emit signal to update GUI (ensure it happens in GUI thread)
        # This might be redundant if _monitor_progress always emits, but provides a way
        # to manually trigger an update if needed.
        self._dialog.progress_updated_signal.emit(new_state)

    # Implement the abstract _monitor_progress method

    def _monitor_progress(self, tracker: ProgressTrackerAbstraction):
        """
        Thread-Funktion, die den Tracker überwacht und Signale zur
        Aktualisierung der GUI aussendet. Läuft in einem separaten Thread.
        """
        if tracker is None:
            self._log("ERROR", "Kein Tracker zum Überwachen übergeben.")
            # Signal finish with error state?
            self._safe_emit_finish(success=False)
            return

        last_state = None
        is_finished = False

        while not self._stop_event.is_set():
            try:
                current_state = tracker.get_state()
                self._current_state = current_state  # Update cache

                # Nur Signal senden, wenn sich etwas geändert hat
                if current_state != last_state:
                    # Emit signal - Qt handles marshalling to the GUI thread
                    self._dialog.progress_updated_signal.emit(current_state)
                    last_state = current_state

                # Prüfen, ob die Aufgabe abgeschlossen ist (100% oder Fehler)
                is_error = current_state.get('error') is not None
                is_complete = current_state.get('percentage', 0) >= 100

                if is_error or is_complete:
                    is_finished = True
                    self._stop_event.set()  # Signal loop to stop
                    break  # Exit monitoring loop

            except Exception as e:
                # Fehler beim Abrufen des Tracker-Status
                self._log("ERROR", f"Fehler beim Abrufen des Tracker-Status: {e}")
                # Update state with this error and emit
                self._current_state['error'] = e
                self._dialog.progress_updated_signal.emit(self._current_state)
                is_finished = True  # Treat tracker failure as finished
                self._stop_event.set()
                break

            # Wartezeit, um CPU zu schonen
            stopped = self._stop_event.wait(self.update_interval)
            if stopped and not is_finished:  # Stopped externally before completion?
                self._log("INFO", "Monitor-Thread extern gestoppt.")
                # Get final state one last time if possible
                try:
                    final_state = tracker.get_state()
                    self._current_state = final_state
                    self._dialog.progress_updated_signal.emit(final_state)
                except Exception as e_final:
                    self._log("ERROR", f"Fehler beim Abrufen des finalen Status nach Stopp: {e_final}")
                    if not self._current_state.get('error'):  # Avoid overwriting existing error
                        self._current_state['error'] = e_final
                        self._dialog.progress_updated_signal.emit(self._current_state)
                is_finished = True  # Mark as finished regardless of success

        # --- End of monitoring loop ---

        # Ensure the final state is emitted if loop exited normally
        if not self._stop_event.is_set():  # Should be set if finished, but check just in case
            try:
                final_state = tracker.get_state()
                self._current_state = final_state
                # Emit final state only if different from last emitted state
                if final_state != last_state:
                    self._dialog.progress_updated_signal.emit(final_state)
            except Exception as e:
                self._log("ERROR", f"Fehler beim Abrufen des finalen Tracker-Status (Ende): {e}")
                if not self._current_state.get('error'):
                    self._current_state['error'] = e
                    self._dialog.progress_updated_signal.emit(self._current_state)

        # Determine success based on the final known state
        final_success = self._current_state.get('error') is None
        # Signal the dialog to close itself (must be done safely in GUI thread)
        self._safe_emit_finish(final_success)

    def _safe_emit_finish(self, success: bool):
        """ Safely emits the finished signal using QMetaObject.invokeMethod if needed. """
        # This ensures the signal is emitted/processed in the GUI thread,
        # which can then safely close the dialog.
        if QThread.currentThread() != self._dialog.thread():
            QMetaObject.invokeMethod(
                self._dialog,
                "finished_signal",  # The signal name as string
                Qt.ConnectionType.QueuedConnection,  # Ensure it goes through event loop
                Q_ARG(bool, success)  # Argument for the signal
            )
        else:
            self._dialog.finished_signal.emit(success)  # Already in GUI thread

    def _run_target_task(self, target: Callable[..., Any], args: Tuple, kwargs: Dict[str, Any], tracker: ProgressTrackerAbstraction):
        """Wrapper function to run the target task in a separate thread."""
        self._task_exception = None  # Reset before task starts
        try:
            target(*args, **kwargs)
        except Exception as e:
            self._task_exception = e
            # Ensure tracker knows about the error if it doesn't already
            if ProgressTrackerAbstraction is not None and isinstance(tracker, ProgressTrackerAbstraction):
                current_tracker_state = {}
                try:
                    current_tracker_state = tracker.get_state()
                except Exception as tracker_get_err:
                    self._log("ERROR", f"Fehler beim Abrufen des Tracker-Status nach Task-Exception: {tracker_get_err}")

                if not current_tracker_state.get('error'):
                    try:
                        tracker.set_error(e)
                        self._current_state = tracker.get_state()  # Update cache
                        # Emit the error state immediately if possible
                        self._dialog.progress_updated_signal.emit(self._current_state)
                    except Exception as tracker_set_err:
                        self._log(
                            "ERROR", f"Fehler beim Setzen des Fehlers im Tracker nach Task-Exception: {tracker_set_err}")

            self._log("ERROR", f"Ausnahme in der überwachten Aufgabe: {e}")
        finally:
            # Ensure the monitor thread knows to stop, even if target finishes quickly
            # or without reaching 100%/error state explicitly.
            self._stop_event.set()

    # Implement the abstract run_with_progress method

    def run_with_progress(self, target: Callable[..., Any], args: Tuple = (), kwargs: Optional[Dict[str, Any]] = None, tracker: ProgressTrackerAbstraction = None) -> Optional[Exception]:
        """
        Führt die `target`-Funktion in einem separaten Thread aus und zeigt
        den Fortschritt in einem modalen Qt-Dialog an.

        Args:
            target: Die auszuführende Funktion.
            args: Argumente für die target-Funktion.
            kwargs: Keyword-Argumente für die target-Funktion.
            tracker: Das ProgressTrackerInterface-Objekt, das von 'target' aktualisiert wird.

        Returns:
            Optional[Exception]: Der Fehler, der im Tracker gesetzt wurde oder während
                                 der Ausführung von 'target' aufgetreten ist, oder None bei Erfolg.
        """

        if not isinstance(tracker, ProgressTrackerAbstraction):  # type: ignore
            raise ValueError("Ein gültiges ProgressTrackerInterface-Objekt muss übergeben werden.")
        if kwargs is None:
            kwargs = {}

        self._stop_event.clear()
        self._task_exception = None  # Clear previous task exception
        self._current_state = {'percentage': 0, 'current': 0, 'total': 100, 'error': None}  # Reset state

        # Ensure the dialog reflects the initial state before showing
        self._dialog._handle_progress_update_slot(self._current_state)
        self._dialog._error_occurred = False  # Reset error styling
        self._dialog.status_label.setStyleSheet("")
        self._dialog.progress_bar.setStyleSheet("")

        # --- Setup Threads ---
        # 1. Monitor Thread: Polls tracker, emits signals for GUI update
        self._progress_thread = threading.Thread(target=self._monitor_progress, args=(tracker,), daemon=True)

        # 2. Task Thread: Runs the actual target function
        self._task_thread = threading.Thread(
            target=self._run_target_task,
            args=(target, args, kwargs, tracker),
            daemon=True
        )

        # --- Start Threads ---
        self._progress_thread.start()
        self._task_thread.start()

        # --- Show Dialog Modally ---
        # This blocks the *calling* thread until the dialog is closed
        # (via accept() or reject(), triggered by finished_signal)
        # The Qt event loop keeps running, processing signals.
        dialog_result = self._dialog.exec()  # Returns QDialog.Accepted or QDialog.Rejected

        # --- Cleanup after Dialog Closes ---
        # Ensure threads are finished (they should be signaled by _monitor_progress or _run_target_task)
        self._stop_event.set()  # Make sure stop is signaled if not already
        if self._task_thread and self._task_thread.is_alive():
            self._task_thread.join(timeout=1.0)  # Wait briefly for task thread
        if self._progress_thread and self._progress_thread.is_alive():
            self._progress_thread.join(timeout=self.update_interval * 3)  # Wait briefly for monitor

        # --- Determine Final Result ---
        final_tracker_error = self._current_state.get('error')
        combined_error = self._task_exception or final_tracker_error

        # Log completion status
        self.complete(success=(combined_error is None),
                      final_message=f"Fehler: {combined_error}" if combined_error else "Abgeschlossen.")

        return combined_error

    # Implement the abstract complete method

    def complete(self, success: bool = True, final_message: Optional[str] = None):
        """Schließt die Fortschrittsanzeige ab (Dialog wurde bereits geschlossen). Loggt die Endnachricht."""
        # The dialog is already closed by the time this is called in run_with_progress.
        # This method mainly serves for logging the final outcome.
        if final_message:
            log_level = "INFO" if success else "ERROR"
            self._log(log_level, final_message)
        # Optional: Could show a final message box here, but might be redundant if error was shown in dialog.
        # if not success and final_message:
        #    from PySide6.QtWidgets import QMessageBox
        #    QMessageBox.warning(self._dialog.parent(), "Aufgabe beendet", final_message)
        # elif success and final_message:
        #    from PySide6.QtWidgets import QMessageBox
        #    QMessageBox.information(self._dialog.parent(), "Aufgabe beendet", final_message)


# --- END OF FILE qt_progress_bar.py ---
