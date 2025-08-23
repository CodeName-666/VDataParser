from __future__ import annotations

"""Threaded wrapper around :class:`AdvancedDBManager` to offload database operations.

The thread processes tasks sequentially from an internal queue. Each task is a
callable that receives an ``AdvancedDBManager`` instance and can perform any
operation with it. Results and errors are communicated via Qt signals so the UI
can react without blocking the main thread.
"""

from PySide6.QtCore import QThread, Signal
import queue
import threading
from typing import Any, Callable, Tuple

from .advance_db_connector import AdvancedDBManager


class AdvancedDBManagerThread(QThread):
    """Execute ``AdvancedDBManager`` tasks in a dedicated thread."""

    task_finished = Signal(object)
    """Emitted when a task finished successfully with its result."""

    task_error = Signal(Exception)
    """Emitted when a task raised an exception."""

    def __init__(self, db_interface: Any, parent: QThread | None = None) -> None:
        """Initialise the thread with a database interface.

        Parameters
        ----------
        db_interface:
            Concrete database interface used to create the :class:`AdvancedDBManager`.
        parent:
            Optional Qt parent.
        """
        super().__init__(parent)
        self._db_interface = db_interface
        self._tasks: "queue.Queue[Tuple[Callable[..., Any], tuple, dict]]" = queue.Queue()
        self._stop_event = threading.Event()

    def run(self) -> None:  # pragma: no cover - thread loop
        """Process queued tasks until :meth:`stop` is called."""
        manager = AdvancedDBManager(self._db_interface)
        manager.connect()
        try:
            while not self._stop_event.is_set():
                try:
                    func, args, kwargs = self._tasks.get(timeout=0.1)
                except queue.Empty:
                    continue
                try:
                    result = func(manager, *args, **kwargs)
                    self.task_finished.emit(result)
                except Exception as exc:  # pragma: no cover - error path
                    self.task_error.emit(exc)
        finally:
            manager.disconnect()

    def add_task(self, func: Callable[..., Any], *args: Any, **kwargs: Any) -> None:
        """Queue a callable to be executed in the thread."""
        self._tasks.put((func, args, kwargs))

    def stop(self) -> None:
        """Signal the thread to stop and wait for its termination."""
        self._stop_event.set()
        self.wait()
