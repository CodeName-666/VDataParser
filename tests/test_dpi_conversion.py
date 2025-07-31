import importlib.util
import sys
import types
import dataclasses
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

# minimal stubs for heavy dependencies
sys.modules.setdefault(
    'display',
    types.SimpleNamespace(
        ProgressTrackerAbstraction=object,
        ConsoleProgressBar=object,
        OutputInterfaceAbstraction=object,
        BasicProgressTracker=object,
    ),
)
sys.modules.setdefault('log', types.SimpleNamespace(CustomLogger=object, LogType=str))

pypdf = types.ModuleType('pypdf')
pypdf.PdfReader = object
pypdf.PdfWriter = object
pypdf.PageObject = object
sys.modules.setdefault('pypdf', pypdf)

reportlab = types.ModuleType('reportlab')
sys.modules.setdefault('reportlab', reportlab)
sys.modules.setdefault('reportlab.pdfgen', types.ModuleType('reportlab.pdfgen'))
canvas_mod = types.ModuleType('reportlab.pdfgen.canvas')
canvas_mod.Canvas = object
sys.modules.setdefault('reportlab.pdfgen.canvas', canvas_mod)
lib_mod = types.ModuleType('reportlab.lib')
pagesizes = types.ModuleType('reportlab.lib.pagesizes')
pagesizes.letter = (0, 0)
pagesizes.landscape = lambda size: size
units = types.ModuleType('reportlab.lib.units')
units.mm = 1
colors = types.ModuleType('reportlab.lib.colors')
colors.black = object()
lib_mod.pagesizes = pagesizes
lib_mod.units = units
lib_mod.colors = colors
sys.modules.setdefault('reportlab.lib', lib_mod)
sys.modules['reportlab.lib.pagesizes'] = pagesizes
sys.modules['reportlab.lib.units'] = units
sys.modules['reportlab.lib.colors'] = colors

# minimal requests stub for json_handler
requests_stub = types.ModuleType('requests')
requests_stub.exceptions = types.SimpleNamespace(
    Timeout=Exception,
    RequestException=Exception,
    HTTPError=Exception,
)
sys.modules.setdefault('requests', requests_stub)

# build minimal generator package for relative imports
GEN_DIR = Path(__file__).resolve().parents[1] / 'generator'
gen_pkg = types.ModuleType('generator')
gen_pkg.__path__ = [str(GEN_DIR)]
sys.modules['generator'] = gen_pkg

# minimal DataGenerator stub to satisfy relative import
data_gen_stub = types.ModuleType('generator.data_generator')
class _StubDG:
    FILE_SUFFIX = ''

    def __init__(self, *a, **k):
        pass

    def generate(self, overall_tracker=None):
        pass

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
sys.modules['objects'] = objects_mod

data_gen_stub.DataGenerator = _StubDG
sys.modules['generator.data_generator'] = data_gen_stub

spec = importlib.util.spec_from_file_location(
    'generator.receive_info_pdf_generator',
    GEN_DIR / 'receive_info_pdf_generator.py'
)
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
sys.modules['generator.receive_info_pdf_generator'] = module
spec.loader.exec_module(module)

def test_from_display_coords_with_custom_dpi():
    cfg = CoordinatesConfig(100, 100, 200, 200, 300, 300, 12)
    res = module.ReceiveInfoPdfGenerator._from_display_coords(cfg, 400, dpi=200)

    assert res.x1 == 100 * 72 / 200
    assert res.y1 == 400 - 100 * 72 / 200
    assert res.x2 == 200 * 72 / 200
    assert res.y2 == 400 - 200 * 72 / 200
    assert res.x3 == 300 * 72 / 200
    assert res.y3 == 400 - 300 * 72 / 200
