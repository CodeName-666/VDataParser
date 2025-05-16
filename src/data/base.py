from typing import Optional
from log import CustomLogger
from display import OutputInterfaceAbstraction


class Base:


    logger: Optional[CustomLogger]
    output_interface: Optional[OutputInterfaceAbstraction]

    def __init__(self, logger: Optional[CustomLogger] = None,
                 output_interface: Optional[OutputInterfaceAbstraction] = None):
        if logger is not None:
            Base.logger = logger

        if output_interface is not None:
            Base.output_interface = output_interface
  

    def _log(self, level: str, message: str, on_verbose: bool = False) -> None:
        """ Helper method for conditional logging ONLY. """
        if self.logger:
            log_method = getattr(self.logger, level.lower(), None)
            if log_method and callable(log_method):
                try:
                    if level.lower() in ["debug", "info", "warning", "error"]:
                        log_method(message, verbose=on_verbose)
                    else:
                        log_method(message)
                except Exception as e:
                    import sys
                    print(f"LOGGING FAILED ({level}): {message} | Error: {e}", file=sys.stderr)

    def _log(self, level: str, msg: str, *, exc: Exception | None = None) -> None:
        if not self.logger:
            return

        fn = getattr(self.logger, level, None)
        if callable(fn):
            try:
                fn(msg, exc_info=exc)  # type: ignore[arg-type]
            except TypeError:
                fn(msg)  # type: ignore[misc]
        else:
            self.logger.info(msg)

    def _output(self, message: str) -> None:
        """ Helper method to write ONLY to the output interface. """
        if self.output_interface:
            try:
                self.output_interface.write_message(message)
            except Exception as e:
                # Log error if output fails? Or just print?
                self._log("ERROR", f"Failed to write message to output interface: {e}")
                # Or print to stderr as a last resort
                # import sys
                # print(f"OUTPUT INTERFACE FAILED: {message} | Error: {e}", file=sys.stderr)

    def _output_and_log(self, level: str, message: str, on_verbose: bool = False) -> None:
        """
        Helper method for sending messages to BOTH logger and output interface.
        Typically used for INFO, WARNING, ERROR level messages relevant to the user.
        """
        # Log first
        self._log(level, message, on_verbose)

        # Then output to user interface (usually only for non-debug levels)
        if level.upper() in ["INFO", "WARNING", "ERROR", "CRITICAL"]:
            self._output(message)  # Send the same message to the user output


    def _echo(self, msg: str) -> None:  # noqa: D401
        if self.output_interface:
            try:
                self.output_interface.write_message(msg)
            except Exception:  # pragma: no cover
                pass

    def _echo(self, prefix: str, msg: str) -> None:
        if self.output_interface:
            self.output_interface.write_message(f"{prefix} {msg}")
    
    

    