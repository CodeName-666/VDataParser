"""Console based output implementation."""

from .output_interface_abstraction import OutputInterfaceAbstraction


class ConsoleOutput(OutputInterfaceAbstraction):
    """Emit messages using the built‑in :func:`print`."""

    def write_message(self, message: str) -> None:
        """Write ``message`` to ``stdout``."""
        print(message)
