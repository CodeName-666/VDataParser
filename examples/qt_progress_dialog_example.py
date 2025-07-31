import sys
import time
import threading
from pathlib import Path
from PySide6.QtWidgets import QApplication

# Allow imports from repository root and src directory
sys.path.insert(0, Path(__file__).parent.parent.__str__())
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.display import BasicProgressTracker
from src.display.progress_bar.qt_progress_bar import _ProgressDialog


def example_task(dialog: _ProgressDialog, tracker: BasicProgressTracker, steps: int = 20, delay: float = 0.1) -> None:
    """Increment the tracker and update the dialog."""
    for _ in range(steps):
        time.sleep(delay)
        tracker.increment()
        # Emit progress update for the dialog
        dialog.progress_updated_signal.emit(tracker.get_state())
    # Signal that the task finished successfully
    dialog.finished_signal.emit(True)


if __name__ == "__main__":
    steps = 20
    app = QApplication(sys.argv)
    tracker = BasicProgressTracker(total=steps)
  
    dialog = _ProgressDialog("Qt Progress Dialog Example")

    task_thread = threading.Thread(target=example_task, args=(dialog, tracker, steps), daemon=True)
    task_thread.start()

    dialog.exec()
    sys.exit(app.exec())
