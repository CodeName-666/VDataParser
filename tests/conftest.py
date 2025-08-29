import sys
import types

# Global PySide6 stubs to avoid ImportErrors when Qt is missing
qtcore = types.ModuleType("PySide6.QtCore")
qtwidgets = types.ModuleType("PySide6.QtWidgets")
qtgui = types.ModuleType("PySide6.QtGui")
qtcharts = types.ModuleType("PySide6.QtCharts")
qtpdf = types.ModuleType("PySide6.QtPdf")


class QObject:  # pragma: no cover - simple stub
    pass


class Signal:  # pragma: no cover - simple stub
    def __init__(self, *args, **kwargs):
        pass

    def connect(self, *args, **kwargs):
        pass

    def emit(self, *args, **kwargs):
        pass


def Slot(*args, **kwargs):  # pragma: no cover - simple stub
    def decorator(func):
        return func

    return decorator


class QThread:  # pragma: no cover - simple stub
    def start(self):
        pass

    def wait(self):
        pass


class QEventLoop:  # pragma: no cover - simple stub
    def exec(self):
        pass

    def quit(self):
        pass


class QCoreApplication:  # pragma: no cover - simple stub
    def __init__(self, *args, **kwargs):
        pass

    def exec(self):  # pragma: no cover - simple stub
        return 0


class QDate:  # pragma: no cover - simple stub
    pass


class QDateTime:  # pragma: no cover - simple stub
    pass


class QLocale:  # pragma: no cover - simple stub
    pass


class QTimer:  # pragma: no cover - simple stub
    def start(self):
        pass

    def stop(self):
        pass


class _Qt:  # pragma: no cover - simple stub
    transparent = 0

    def __getattr__(self, name):  # pragma: no cover - simple stub
        return 0


Qt = _Qt()


class QMetaObject:  # pragma: no cover - simple stub
    pass


class QFileDialog:  # pragma: no cover - simple stub
    pass


class QApplication:  # pragma: no cover - simple stub
    def __init__(self, *args, **kwargs):
        pass

    def exec(self):  # pragma: no cover - simple stub
        return 0


class QWidget:  # pragma: no cover - simple stub
    pass


class QDialog:  # pragma: no cover - simple stub
    pass


class QMainWindow:  # pragma: no cover - simple stub
    pass


class QMessageBox:  # pragma: no cover - simple stub
    pass


class QFont:  # pragma: no cover - simple stub
    Bold = 0

    def __init__(self, *args, **kwargs):
        pass


qtcore.QObject = QObject
qtcore.Signal = Signal
qtcore.Slot = Slot
qtcore.QThread = QThread
qtcore.QEventLoop = QEventLoop
qtcore.QCoreApplication = QCoreApplication
qtcore.QDate = QDate
qtcore.QDateTime = QDateTime
qtcore.QLocale = QLocale
qtcore.QTimer = QTimer
qtcore.Qt = Qt
qtcore.QMetaObject = QMetaObject

qtwidgets.QApplication = QApplication
qtwidgets.QWidget = QWidget
qtwidgets.QDialog = QDialog
qtwidgets.QMainWindow = QMainWindow
qtwidgets.QMessageBox = QMessageBox
qtwidgets.QFileDialog = QFileDialog
qtgui.QFont = QFont

pyside6 = types.ModuleType("PySide6")
pyside6.QtCore = qtcore
pyside6.QtWidgets = qtwidgets
pyside6.QtGui = qtgui
pyside6.QtCharts = qtcharts
pyside6.QtPdf = qtpdf

sys.modules.setdefault("PySide6", pyside6)
sys.modules.setdefault("PySide6.QtCore", qtcore)
sys.modules.setdefault("PySide6.QtWidgets", qtwidgets)
sys.modules.setdefault("PySide6.QtGui", qtgui)
sys.modules.setdefault("PySide6.QtCharts", qtcharts)
sys.modules.setdefault("PySide6.QtPdf", qtpdf)


def _qtcore_getattr(name):  # pragma: no cover - simple stub
    cls = type(name, (), {"__init__": lambda self, *a, **k: None})
    setattr(qtcore, name, cls)
    return cls


def _qtwidgets_getattr(name):  # pragma: no cover - simple stub
    cls = type(name, (), {"__init__": lambda self, *a, **k: None})
    setattr(qtwidgets, name, cls)
    return cls


qtcore.__getattr__ = _qtcore_getattr
qtwidgets.__getattr__ = _qtwidgets_getattr
qtgui.__getattr__ = _qtwidgets_getattr
qtcharts.__getattr__ = _qtwidgets_getattr
qtpdf.__getattr__ = _qtwidgets_getattr
