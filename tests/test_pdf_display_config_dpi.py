import importlib.util
import sys
import types
import dataclasses
from pathlib import Path

def test_dpi_getter_setter():
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

    pyside6 = types.ModuleType('PySide6')
    qtcore = types.ModuleType('PySide6.QtCore')

    class QObject:  # pragma: no cover - simple stub
        pass

    class Signal:  # pragma: no cover - simple stub
        def __init__(self, *a, **kw):
            pass

    qtcore.QObject = QObject
    qtcore.Signal = Signal
    sys.modules['PySide6'] = pyside6
    sys.modules['PySide6.QtCore'] = qtcore
    restore_pyside = True

    # stubs for dependencies used by PdfDisplayConfig
    requests_stub = types.ModuleType('requests')
    requests_stub.exceptions = types.SimpleNamespace(
        Timeout=Exception,
        RequestException=Exception,
        HTTPError=Exception,
    )
    sys.modules.setdefault('requests', requests_stub)

    objects_mod = types.ModuleType('objects')
    @dataclasses.dataclass
    class CoordinatesConfig:
        x1: float
        y1: float
        x2: float
        y2: float
        x3: float
        y3: float
        font_size: int = 12

    objects_mod.CoordinatesConfig = CoordinatesConfig
    sys.modules.setdefault('objects', objects_mod)

    # build minimal data package for relative imports
    DATA_DIR = Path(__file__).resolve().parents[1] / 'data'
    data_pkg = types.ModuleType('data')
    data_pkg.__path__ = [str(DATA_DIR)]
    sys.modules['data'] = data_pkg

    json_spec = importlib.util.spec_from_file_location('data.json_handler', DATA_DIR / 'json_handler.py')
    json_mod = importlib.util.module_from_spec(json_spec)
    assert json_spec and json_spec.loader
    sys.modules['data.json_handler'] = json_mod
    json_spec.loader.exec_module(json_mod)  # type: ignore[arg-type]

    spec = importlib.util.spec_from_file_location('data.pdf_display_config', Path(__file__).resolve().parents[1] / 'data' / 'pdf_display_config.py')
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    sys.modules['data.pdf_display_config'] = module
    spec.loader.exec_module(module)
    PdfDisplayConfig = module.PdfDisplayConfig

    cfg = PdfDisplayConfig()
    assert cfg.get_dpi() == 150
    cfg.set_dpi(200)
    assert cfg.get_dpi() == 200

    if restore_pyside:
        sys.modules.pop('PySide6.QtCore', None)
        sys.modules.pop('PySide6', None)

    sys.modules.pop('data.pdf_display_config', None)
    sys.modules.pop('data.json_handler', None)
    sys.modules.pop('data', None)
    sys.modules.pop('objects', None)
    sys.modules.pop('requests', None)
