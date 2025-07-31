import sys
import time
from pathlib import Path
from PySide6.QtWidgets import QApplication

# Allow imports from repository root and src directory
sys.path.insert(0, Path(__file__).parent.parent.__str__())
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.display import BasicProgressTracker, QtProgressBar


def example_task(tracker: BasicProgressTracker, steps: int = 20, delay: float = 0.1) -> None:
    """Simple function that increments ``tracker`` ``steps`` times."""
    for _ in range(steps):
        time.sleep(delay)
        tracker.increment()


if __name__ == "__main__":
    steps = 20
    app = QApplication(sys.argv)
    tracker = BasicProgressTracker(total=steps)
    bar = QtProgressBar(description="Qt Progress Example")

    # Start the example task while showing the Qt progress dialog
    bar.run_with_progress(example_task, args=(tracker, steps), tracker=tracker)

    sys.exit(app.exec())
