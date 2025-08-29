import importlib
import importlib
import sys
from pathlib import Path
import types

import pytest


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))


@pytest.fixture
def facade_class(monkeypatch):
    """Provide ``MarketFacade`` with minimal Qt stubs."""

    qtcore = types.ModuleType('PySide6.QtCore')

    class QObject:  # pragma: no cover - simple stub
        pass

    class Signal:  # pragma: no cover - simple stub
        def __init__(self, *args, **kwargs):
            self._callbacks = []

        def connect(self, callback):
            self._callbacks.append(callback)

        def disconnect(self, callback):
            if callback in self._callbacks:
                self._callbacks.remove(callback)

        def emit(self, *args, **kwargs):
            for cb in list(self._callbacks):
                cb(*args, **kwargs)

    def Slot(*args, **kwargs):  # pragma: no cover - simple stub
        def decorator(func):
            return func

        return decorator

    class QThread:  # pragma: no cover - simple stub
        def __init__(self, *args, **kwargs):
            pass

        def start(self):
            pass

        def wait(self):
            pass

    class QEventLoop:  # pragma: no cover - simple stub
        def exec(self):
            pass

        def quit(self):
            pass

    qtcore.QObject = QObject
    qtcore.Signal = Signal
    qtcore.Slot = Slot
    qtcore.QThread = QThread
    qtcore.QEventLoop = QEventLoop

    pyside6 = types.ModuleType('PySide6')
    pyside6.QtCore = qtcore

    monkeypatch.setitem(sys.modules, 'PySide6', pyside6)
    monkeypatch.setitem(sys.modules, 'PySide6.QtCore', qtcore)

    module = importlib.import_module('data.market_facade')
    importlib.reload(module)
    return module.MarketFacade


class DummySignal:
    def __init__(self):
        self._callbacks = []

    def connect(self, callback):  # pragma: no cover - simple stub
        self._callbacks.append(callback)

    def disconnect(self, callback):  # pragma: no cover - simple stub
        if callback in self._callbacks:
            self._callbacks.remove(callback)

    def emit(self, *args):  # pragma: no cover - simple stub
        for cb in list(self._callbacks):
            cb(*args)


class DummyManager:
    def __init__(self):
        self.selected_db = None
        self.export_path = None

    def connect_to_db(self, name=None):  # pragma: no cover - simple stub
        self.selected_db = name

    def export_to_custom_json(self, path):  # pragma: no cover - simple stub
        self.export_path = path
        Path(path).write_text('[]', encoding='utf-8')


class DummyThread:
    def __init__(self, manager):
        self.manager = manager
        self.task_finished = DummySignal()
        self.task_error = DummySignal()

    def add_task(self, func, *args, **kwargs):  # pragma: no cover - simple stub
        try:
            result = func(self.manager, *args, **kwargs)
            self.task_finished.emit(result)
        except Exception as exc:  # pragma: no cover - simple stub
            self.task_error.emit(exc)

    def list_databases(self, prefix=None):  # pragma: no cover - simple stub
        self.add_task(lambda _m: [])

    def start(self):  # pragma: no cover - simple stub
        pass

    def stop(self):  # pragma: no cover - simple stub
        pass


def test_select_database_queues_task(facade_class):
    facade = facade_class()
    manager = DummyManager()
    facade._db_thread = DummyThread(manager)

    assert facade.select_database('foo') is True
    assert manager.selected_db == 'foo'


def test_download_market_export_reuses_thread(tmp_path, monkeypatch, facade_class):
    facade = facade_class()
    manager = DummyManager()
    thread = DummyThread(manager)
    facade._db_thread = thread

    connect_calls = []

    def fake_connect(self, *args, **kwargs):  # pragma: no cover - simple stub
        connect_calls.append(True)
        return True

    monkeypatch.setattr(facade_class, 'connect_to_mysql_server', fake_connect)

    info = {'database': 'bar'}
    out_file = tmp_path / 'out.json'
    result = []

    assert facade.download_market_export(info, str(out_file), result.append)
    assert result == [True]
    assert manager.selected_db == 'bar'
    assert manager.export_path == str(out_file)
    assert connect_calls == []
    assert facade._db_thread is thread


def test_connect_to_mysql_server_only_once(monkeypatch, facade_class):
    class DummyMySQLInterface:
        calls = 0

        def __init__(self, host, port, user, password):
            DummyMySQLInterface.calls += 1

    monkeypatch.setitem(sys.modules, 'backend.MySQLInterface', DummyMySQLInterface)

    connect_calls = []

    def dummy_connect(self, db_interface):  # pragma: no cover - simple stub
        connect_calls.append(db_interface)
        self._db_thread = object()

    monkeypatch.setattr(facade_class, 'connect_to_db', dummy_connect)

    facade = facade_class()
    assert facade.connect_to_mysql_server('h', 1, 'u', 'p') is True
    first_thread = facade._db_thread
    assert DummyMySQLInterface.calls == 1
    assert len(connect_calls) == 1

    assert facade.connect_to_mysql_server('h2', 2, 'u2', 'p2') is True
    assert facade._db_thread is first_thread
    assert DummyMySQLInterface.calls == 1
    assert len(connect_calls) == 1

