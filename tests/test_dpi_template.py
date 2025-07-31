import importlib.util
import sys
import types
import dataclasses
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.modules.pop('objects', None)
sys.modules.pop('PySide6', None)
sys.modules.pop('PySide6.QtCore', None)
sys.modules.pop('PySide6.QtWidgets', None)
import objects  # reload real package


def test_overlay_page_uses_template_dimensions(tmp_path):

    modified = {}
    def _store(name, module):
        modified[name] = sys.modules.get(name)
        sys.modules[name] = module

    # minimal stubs for display and log
    _store(
        'display',
        types.SimpleNamespace(
            ProgressTrackerAbstraction=object,
            ConsoleProgressBar=object,
            OutputInterfaceAbstraction=object,
            BasicProgressTracker=object,
        ),
    )
    _store('log', types.SimpleNamespace(CustomLogger=object, LogType=str))

    # stub pypdf
    class StubPage:
        def __init__(self, w, h):
            self.mediabox = types.SimpleNamespace(width=w, height=h)

    class StubPdfReader:
        def __init__(self, *a, **k):
            self._pages = [StubPage(595, 842)]

        @property
        def pages(self):
            return self._pages

    pypdf_mod = types.ModuleType('pypdf')
    pypdf_mod.PdfReader = StubPdfReader
    pypdf_mod.PdfWriter = object
    pypdf_mod.PageObject = StubPage
    _store('pypdf', pypdf_mod)

    # stub reportlab
    captured = {}
    class StubCanvas:
        def __init__(self, stream, pagesize=(0, 0)):
            captured['size'] = pagesize
        def setFillColor(self, *a, **kw):
            pass
        def setFont(self, *a, **kw):
            pass
        def drawString(self, *a, **kw):
            pass
        def save(self):
            pass

    reportlab_mod = types.ModuleType('reportlab')
    _store('reportlab', reportlab_mod)
    _store('reportlab.pdfgen', types.ModuleType('reportlab.pdfgen'))
    canvas_mod = types.ModuleType('reportlab.pdfgen.canvas')
    canvas_mod.Canvas = StubCanvas
    _store('reportlab.pdfgen.canvas', canvas_mod)

    units_mod = types.ModuleType('reportlab.lib.units')
    units_mod.mm = 1
    colors_mod = types.ModuleType('reportlab.lib.colors')
    colors_mod.black = object()
    lib_mod = types.ModuleType('reportlab.lib')
    lib_mod.units = units_mod
    lib_mod.colors = colors_mod
    _store('reportlab.lib', lib_mod)
    _store('reportlab.lib.units', units_mod)
    _store('reportlab.lib.colors', colors_mod)

    # objects stub with CoordinatesConfig
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
    _store('objects', objects_mod)

    # build minimal generator package for relative imports
    GEN_DIR = Path(__file__).resolve().parents[1] / 'generator'
    gen_pkg = types.ModuleType('generator')
    gen_pkg.__path__ = [str(GEN_DIR)]
    _store('generator', gen_pkg)

    data_gen_stub = types.ModuleType('generator.data_generator')
    class _StubDG:
        FILE_SUFFIX = ''
        def __init__(self, *a, **k):
            pass
        def generate(self, overall_tracker=None):
            pass
    data_gen_stub.DataGenerator = _StubDG
    _store('generator.data_generator', data_gen_stub)

    spec = importlib.util.spec_from_file_location(
        'generator.receive_info_pdf_generator',
        GEN_DIR / 'receive_info_pdf_generator.py'
    )
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    _store('generator.receive_info_pdf_generator', module)
    spec.loader.exec_module(module)

    try:
        gen = module.ReceiveInfoPdfGenerator(None, pdf_template='dummy.pdf', path=tmp_path)
        gen._template_bytes = lambda: b'dummy'
        gen.coordinates = [CoordinatesConfig(0, 0, 0, 0, 0, 0)]

        calls = {}
        orig_conv = module.ReceiveInfoPdfGenerator._from_display_coords
        def patched(cfg, page_h, *, dpi=module.ReceiveInfoPdfGenerator.DEFAULT_DISPLAY_DPI):
            calls['page_h'] = page_h
            return orig_conv(cfg, page_h, dpi=dpi)
        module.ReceiveInfoPdfGenerator._from_display_coords = staticmethod(patched)

        gen._overlay_page([('A', 'B', 'C')])

        assert captured['size'] == (595, 842)
        assert calls['page_h'] == 842
    finally:
        for name, mod in modified.items():
            if mod is None:
                sys.modules.pop(name, None)
            else:
                sys.modules[name] = mod
