"""Base class providing logging and output helpers."""

from typing import overload, Optional, Any
from src.log import CustomLogger
from src.display import OutputInterfaceAbstraction


class Base:
    logger: Optional[CustomLogger] = None          # Klassen-Attr.
    output_interface: Optional[OutputInterfaceAbstraction] = None

    # ----------------------------------------------------------
    # Initialisierung
    # ----------------------------------------------------------
    def __init__(self, logger: Optional[CustomLogger] = None, output_interface: Optional[OutputInterfaceAbstraction] = None) -> None:
        """Store optional :class:`CustomLogger` and output interface on the class."""
        if logger is not None:
            Base.logger = logger
        if output_interface is not None:
            Base.output_interface = output_interface

    # ==========================================================
    # 1) LOGGEN
    # ==========================================================
    # ---------- Overload-Stubs (nur Typprüfung) ----------
    @overload
    def _log(self, level: str, message: str, on_verbose: bool = False) -> None: ...
    @overload
    def _log(self, level: str, msg: str, *, exc: Exception | None = None) -> None: ...

    # ---------- Runtime-Implementierung ----------
    def _log(
        self,
        level: str,
        *args: Any,
        on_verbose: bool = False,
        exc: Exception | None = None,
    ) -> None:
        """Internal helper to log a message using the stored logger."""
        if not self.logger:
            return

        # Zerlege Parameter
        msg: str = args[0] if args else ""
        log_fn = getattr(self.logger, level.lower(), None)

        if not callable(log_fn):
            self.logger.info(msg)          # Fallback
            return

        try:
            if exc is not None:
                log_fn(msg, exc_info=exc)  # type: ignore[arg-type]
            else:
                log_fn(msg, verbose=on_verbose)  # type: ignore[misc]
        except TypeError:
            log_fn(msg)  # type: ignore[misc]

    # ==========================================================
    # 2) AUSGABE
    # ==========================================================
    @overload
    def _output(self, message: str) -> None: ...
    @overload
    def _output(self, level: str, msg: str) -> None: ...

    def _output(self, *args: Any) -> None:
        """Write ``message`` to the output interface and optionally log it."""
        if not args:
            return
        if len(args) == 1:
            message: str = args[0]
            if self.output_interface:
                try:
                    self.output_interface.write_message(message)
                except Exception as e:
                    self._log("ERROR", f"Failed to write message: {e}")
        else:
            level, msg = args
            self._log(level, msg)
            if level.upper() in {"INFO", "WARNING", "ERROR", "CRITICAL"}:
                self._echo(level, msg)

    # ==========================================================
    # 3) ECHO
    # ==========================================================
    @overload
    def _echo(self, msg: str) -> None: ...
    @overload
    def _echo(self, prefix: str, msg: str) -> None: ...

    def _echo(self, *args: str) -> None:
        """Directly forward a message to the output interface."""
        if not self.output_interface:
            return

        if len(args) == 1:
            self.output_interface.write_message(args[0])
        else:
            prefix, msg = args
            self.output_interface.write_message(f"{prefix} {msg}")

    # ==========================================================
    # Hilfsmethode: beides gleichzeitig
    # ==========================================================
    def _output_and_log(
        self, level: str, message: str, on_verbose: bool = False
    ) -> None:
        """Log ``message`` and, for important levels, also output it."""
        self._log(level, message, on_verbose=on_verbose)
        if level.upper() in {"INFO", "WARNING", "ERROR", "CRITICAL"}:
            self._output(message)
