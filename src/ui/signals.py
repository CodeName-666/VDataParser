class Signal:
    """A simple signal implementation."""
    def __init__(self):
        self._subscribers = []

    def connect(self, func):
        if func not in self._subscribers:
            self._subscribers.append(func)

    def emit(self, *args, **kwargs):
        for func in self._subscribers:
            try:
                func(*args, **kwargs)
            except Exception:
                pass

status_info = Signal()
