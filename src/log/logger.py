from __future__ import annotations

"""A compact yet powerful replacement for *CustomLogger*.

Key features
~~~~~~~~~~~~
* Thread‑safe *one‑line* aggregation with full nesting support.
* Fine‑grained *skip* control per log level.
* Regular convenience methods (`debug`, `info`, `warning`, `error`, `critical`).
* Fully self‑contained: does **not** tamper with the global `logging` config.
"""

import logging
import threading
from typing import Dict, List, Final, Optional, Tuple

# ---------------------------------------------------------------------------
# Shared constants & aliases
# ---------------------------------------------------------------------------
LEVELS: Final[Tuple[str, ...]] = ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL")
LogType = str

# ---------------------------------------------------------------------------
# One‑line helper (stack based / thread safe)
# ---------------------------------------------------------------------------
class _OneLineSession:  # noqa: D101 – tiny helper class
    __slots__ = ("_parts",)

    def __init__(self) -> None:
        self._parts: List[str] = []

    def append(self, msg: str) -> None:  # noqa: D401
        self._parts.append(msg)

    def flush(self) -> str:  # noqa: D401 – returns and clears
        out = "".join(self._parts)
        self._parts.clear()
        return out


class _OneLineManager:  # noqa: D101 – encapsulates state per logger
    def __init__(self) -> None:
        self._stacks: Dict[LogType, List[_OneLineSession]] = {lvl: [] for lvl in LEVELS}
        self._skip: Dict[LogType, bool] = {lvl: False for lvl in LEVELS}
        self._lock = threading.Lock()

    # Validation -------------------------------------------------------
    @staticmethod
    def _check_level(level: LogType) -> None:  # noqa: D401
        if level not in LEVELS:
            raise ValueError(f"Ungültiges Log‑Level: {level}. Erlaubt: {LEVELS}")

    # Public API -------------------------------------------------------
    def begin(self, level: LogType):
        self._check_level(level)
        with self._lock:
            self._stacks[level].append(_OneLineSession())

    def append(self, level: LogType, msg: str):
        self._check_level(level)
        with self._lock:
            if not self._skip[level] and self._stacks[level]:
                self._stacks[level][-1].append(msg)

    def end(self, level: LogType) -> str:
        self._check_level(level)
        with self._lock:
            return self._stacks[level].pop().flush() if self._stacks[level] else ""

    # Skip control -----------------------------------------------------
    def set_skip(self, level: LogType, state: bool):
        self._check_level(level)
        with self._lock:
            self._skip[level] = state

    def is_skipped(self, level: LogType) -> bool:
        self._check_level(level)
        with self._lock:
            return self._skip[level]


# ---------------------------------------------------------------------------
# CustomLogger
# ---------------------------------------------------------------------------
class CustomLogger:  # noqa: D101 – see module docstring
    _LEVEL_MAP = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL,
    }

    # ------------------------------------------------------------------
    def __init__(self, name: str = __name__,*, level: str = "INFO", verbose: bool = False,
                fmt: str = "%(asctime)s %(levelname)s %(message)s",
                datefmt: str = "%Y-%m-%d %H:%M:%S", handler: Optional[logging.Handler] = None):
       
        self._verbose = verbose
        self._ol = _OneLineManager()

        self._lg = logging.getLogger(name)
        self._lg.propagate = False
        self._lg.setLevel(self._LEVEL_MAP.get(level.upper(), logging.INFO))

        if handler is None:
            handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter(fmt, datefmt=datefmt))
        if not self._lg.handlers:
            self._lg.addHandler(handler)

    # ------------------------------------------------------------------
    # Public helpers
    # ------------------------------------------------------------------
    def set_level(self, level: str):  # noqa: D401
        self._lg.setLevel(self._LEVEL_MAP.get(level.upper(), logging.INFO))

    def skip_logging(self, level: LogType, state: bool):  # noqa: D401
        try:
            self._ol.set_skip(level, state)
        except ValueError as err:
            self.error(f"Skip‑Fehler: {err}")

    # One‑line interface ----------------------------------------------
    def one_line_log(self, level: LogType, start: bool):  # noqa: D401
        try:
            if start:
                self._ol.begin(level)
            else:
                msg = self._ol.end(level)
                if msg and not self._ol.is_skipped(level):
                    self._lg.log(self._LEVEL_MAP[level], msg)
        except ValueError as err:
            self.error(f"One‑line‑Fehler: {err}")

    # ------------------------------------------------------------------
    # Core log dispatcher
    # ------------------------------------------------------------------
    def _dispatch(self, level: LogType, msg: str, *, verbose: bool):  # noqa: D401
        if verbose and not self._verbose:
            return
        if self._ol.is_skipped(level):
            return
        if self._ol._stacks[level]:  # active one‑line
            self._ol.append(level, msg)
        else:
            self._lg.log(self._LEVEL_MAP[level], msg)

    # ------------------------------------------------------------------
    # Convenience wrappers
    # ------------------------------------------------------------------
    def debug(self, msg: str, *, verbose: bool = False):
        self._dispatch("DEBUG", msg, verbose=verbose)

    def info(self, msg: str, *, verbose: bool = False):
        self._dispatch("INFO", msg, verbose=verbose)

    def warning(self, msg: str, *, verbose: bool = False):
        self._dispatch("WARNING", msg, verbose=verbose)

    def error(self, msg: str, *, verbose: bool = False):
        self._dispatch("ERROR", msg, verbose=verbose)

    def critical(self, msg: str, *, verbose: bool = False):
        """Logs a *critical* message (new convenience wrapper)."""
        self._dispatch("CRITICAL", msg, verbose=verbose)

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------
    @property
    def verbose(self) -> bool:  # noqa: D401
        return self._verbose
