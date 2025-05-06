from __future__ import annotations

"""Abstract base class for all file‑/data‑generators.

Shared responsibilities
~~~~~~~~~~~~~~~~~~~~~~
* Path & filename handling (`get_full_path`).
* Thin logging/echo helpers (no conditional logic scattered around).
* Optional support for a progress tracker object (only forwarded; not used
  internally).

Concrete subclasses **must** override :pymeth:`generate` and should define a
class attribute :pyattr:`FILE_SUFFIX` (eg. ``'dat'`` or ``'pdf'``).
"""

from pathlib import Path
from typing import Optional

try:
    from log import CustomLogger  # type: ignore
except ImportError:  # pragma: no cover – tests/CI
    CustomLogger = None  # type: ignore

try:
    from src.display import (
        OutputInterfaceAbstraction,                       # type: ignore
        ProgressTrackerAbstraction as _TrackerBase,       # type: ignore
    )
except ImportError:  # pragma: no cover
    OutputInterfaceAbstraction = _TrackerBase = None  # type: ignore

__all__ = ["DataGenerator"]


class DataGenerator:  # noqa: D101 – detailed docstring above
    FILE_SUFFIX: str = ""  # subclasses must override

    # ------------------------------------------------------------------
    # Construction helpers
    # ------------------------------------------------------------------
    def __init__(
        self,
        path: str | Path,
        file_name: str,
        *,
        logger: Optional[CustomLogger] = None,
        output_interface: Optional[OutputInterfaceAbstraction] = None,
    ) -> None:
        self._path = Path(path) if path else Path(".")
        self._file_name = file_name
        self._logger = logger
        self._ui = output_interface

    # ------------------------------------------------------------------
    # Logging & UI
    # ------------------------------------------------------------------
    def _log(self, level: str, msg: str) -> None:  # noqa: D401
        if not self._logger:
            return
        fn = getattr(self._logger, level, None)
        if callable(fn):
            try:
                fn(msg)
            except Exception:  # pragma: no cover – logger mis‑configured
                pass
        else:
            self._logger.info(msg)

    def _echo(self, msg: str) -> None:  # noqa: D401
        if self._ui:
            try:
                self._ui.write_message(msg)
            except Exception:  # pragma: no cover – UI mis‑configured
                pass

    def _output(self, level: str, msg: str) -> None:  # noqa: D401
        self._log(level, msg)
        if level.upper() in {"INFO", "WARNING", "ERROR", "CRITICAL"}:
            self._echo(msg)

    # ------------------------------------------------------------------
    # Path helpers
    # ------------------------------------------------------------------
    @property
    def file_name(self) -> str:  # noqa: D401
        return self._file_name

    @property
    def path(self) -> Path:  # noqa: D401
        return self._path

    def get_full_path(self) -> Path:  # noqa: D401
        if not self.FILE_SUFFIX:
            raise ValueError(
                f"{self.__class__.__name__}.FILE_SUFFIX muss definiert sein"
            )
        return self._path / f"{self._file_name}.{self.FILE_SUFFIX}"

    # ------------------------------------------------------------------
    # Abstract API
    # ------------------------------------------------------------------
    def generate(self, overall_tracker: Optional[_TrackerBase] = None) -> None:  # noqa: D401
        raise NotImplementedError("Sub‑class must implement generate()")

    def write(self, *args, **kwargs) -> None:  # noqa: D401
        """Optional hook for subclasses. Default = no‑op."""
        return None
