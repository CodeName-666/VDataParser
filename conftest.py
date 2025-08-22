"""Provide minimal PySide6 stubs so tests can run without the real dependency."""

import sys
import types


pyside6 = types.ModuleType("PySide6")
qtcore = types.ModuleType("PySide6.QtCore")
qtwidgets = types.ModuleType("PySide6.QtWidgets")


class QObject:  # pragma: no cover - test stub
    pass


class Signal:  # pragma: no cover - test stub
    def __init__(self, *a, **k):
        pass

    def connect(self, *a, **k):
        pass

    def emit(self, *a, **k):
        pass


def Slot(*a, **k):  # pragma: no cover - test stub
    def decorator(func):
        return func

    return decorator


class QFileDialog:  # pragma: no cover - test stub
    @staticmethod
    def getExistingDirectory(*a, **k):
        return ""


class QMessageBox:  # pragma: no cover - test stub
    Yes = 1
    No = 0
    Question = 0

    def setIcon(self, *a, **k):
        pass

    def setWindowTitle(self, *a, **k):
        pass

    def setText(self, *a, **k):
        pass

    def setStandardButtons(self, *a, **k):
        pass

    def setDefaultButton(self, *a, **k):
        pass

    def exec(self):
        return self.Yes


qtcore.QObject = QObject
qtcore.Signal = Signal
qtcore.Slot = Slot
class QThread:  # pragma: no cover - test stub
    def start(self, *a, **k):
        pass


qtcore.QThread = QThread
class QWidget:  # pragma: no cover - test stub
    pass


class QApplication:  # pragma: no cover - test stub
    def __init__(self, *a, **k):
        pass


qtwidgets.QFileDialog = QFileDialog
qtwidgets.QMessageBox = QMessageBox
qtwidgets.QWidget = QWidget
qtwidgets.QApplication = QApplication
pyside6.QtCore = qtcore
pyside6.QtWidgets = qtwidgets

sys.modules.setdefault("PySide6", pyside6)
sys.modules.setdefault("PySide6.QtCore", qtcore)
sys.modules.setdefault("PySide6.QtWidgets", qtwidgets)


def pytest_ignore_collect(collection_path, config):  # pragma: no cover - test helper
    return "test_code" in str(collection_path)

