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
from time import monotonic
from typing import Any, Callable, Tuple

from .advance_db_connector import AdvancedDBManager


class AdvancedDBManagerThread(QThread):
    """Execute ``AdvancedDBManager`` tasks in a dedicated thread."""

    task_finished = Signal(object)
    """Emitted when a task finished successfully with its result."""

    task_error = Signal(Exception)
    """Emitted when a task raised an exception."""

    connected = Signal()
    """Forwarded when the underlying manager connected."""

    disconnected = Signal()
    """Forwarded when the manager disconnected or the thread stops."""

    connecting = Signal()
    """Forwarded when a connection attempt starts."""

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

        # Forward connection state signals to the outside
        manager.connected.connect(self.connected)
        manager.disconnected.connect(self.disconnected)
        manager.connecting.connect(self.connecting)

        manager.connect()
        last_check = monotonic()
        try:
            while not self._stop_event.is_set():
                try:
                    func, args, kwargs = self._tasks.get(timeout=0.1)
                except queue.Empty:
                    func = None
                if func is not None:
                    try:
                        result = func(manager, *args, **kwargs)
                        self.task_finished.emit(result)
                    except Exception as exc:  # pragma: no cover - error path
                        self.task_error.emit(exc)
                if monotonic() - last_check >= 10:
                    manager._check_connection()
                    last_check = monotonic()
        finally:
            manager.disconnect()

    def add_task(self, func: Callable[..., Any], *args: Any, **kwargs: Any) -> None:
        """Queue a callable to be executed in the thread."""
        self._tasks.put((func, args, kwargs))

    def list_databases(self, prefix: str | None = None) -> None:
        """Queue a task to list databases via the manager.

        The resulting list or any raised exception is emitted through the
        ``task_finished`` or ``task_error`` signal respectively.
        """
        self.add_task(lambda mgr: mgr.list_databases(prefix))

    def stop(self) -> None:
        """Signal the thread to stop and wait for its termination."""
        self._stop_event.set()
        self.wait()
