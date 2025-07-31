from __future__ import annotations

from PySide6.QtCore import QThread
from src.generator.file_generator import FileGenerator


class GeneratorWorker(QThread):
    """Run a ``FileGenerator`` method in a separate thread."""

    def __init__(self, generator: FileGenerator, method: str) -> None:
        super().__init__()
        self._generator = generator
        self._method = method

    def run(self) -> None:
        getattr(self._generator, self._method)()
