import importlib.util
from pathlib import Path
import sys
import types
import dataclasses


def test_coordinate_list_generation():
    # Inject src directory
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))

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

    requests_stub = types.ModuleType('requests')
    requests_stub.exceptions = types.SimpleNamespace(
        Timeout=Exception,
        RequestException=Exception,
        HTTPError=Exception,
    )
    sys.modules.setdefault('requests', requests_stub)

    # build minimal data package for relative imports
    DATA_DIR = Path(__file__).resolve().parents[1] / 'src' / 'data'
    data_pkg = types.ModuleType('data')
    data_pkg.__path__ = [str(DATA_DIR)]
    sys.modules['data'] = data_pkg

    json_spec = importlib.util.spec_from_file_location('data.json_handler', DATA_DIR / 'json_handler.py')
    json_mod = importlib.util.module_from_spec(json_spec)
    assert json_spec and json_spec.loader
    sys.modules['data.json_handler'] = json_mod
    json_spec.loader.exec_module(json_mod)  # type: ignore[arg-type]

    spec = importlib.util.spec_from_file_location('data.pdf_display_config', DATA_DIR / 'pdf_display_config.py')
    pdf_mod = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    sys.modules['data.pdf_display_config'] = pdf_mod
    spec.loader.exec_module(pdf_mod)  # type: ignore[arg-type]
    PdfDisplayConfig = pdf_mod.PdfDisplayConfig

    config_data = {
        "pdf_path": "",
        "pdf_name": "",
        "output_path": "",
        "output_name": "",
        "boxPairs": [
            {
                "id": 1,
                "box1": {"label": "A", "x": 1, "y": 2, "width": 0, "height": 0},
                "box2": {"label": "B", "x": 3, "y": 4, "width": 0, "height": 0},
            },
            {
                "id": 2,
                "box1": {"label": "C", "x": 5, "y": 6, "width": 0, "height": 0},
                "box2": {"label": "D", "x": 7, "y": 8, "width": 0, "height": 0},
            },
        ],
        "singleBoxes": [
            {"label": "S1", "x": 10, "y": 11, "width": 0, "height": 0, "id": 1},
            {"label": "S3", "x": 12, "y": 13, "width": 0, "height": 0, "id": 3},
        ],
    }

    cfg = PdfDisplayConfig(config_data)
    coords_list = cfg.convert_json_to_coordinate_list()

    assert len(coords_list) == 3

    c1, c2, c3 = coords_list

    assert (c1.x1, c1.y1, c1.x2, c1.y2, c1.x3, c1.y3) == (1, 8, 3, 10, 10, 17)
    assert (c2.x1, c2.y1, c2.x2, c2.y2, c2.x3, c2.y3) == (5, 12, 7, 14, 0, 0)
    assert (c3.x1, c3.y1, c3.x2, c3.y2, c3.x3, c3.y3) == (0, 0, 0, 0, 12, 19)

    if restore_pyside:
        sys.modules.pop('PySide6.QtCore', None)
        sys.modules.pop('PySide6', None)

    sys.modules.pop('data.pdf_display_config', None)
    sys.modules.pop('data.json_handler', None)
    sys.modules.pop('data', None)
    sys.modules.pop('objects', None)
    sys.modules.pop('requests', None)
