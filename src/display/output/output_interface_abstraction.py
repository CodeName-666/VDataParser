"""Abstract base definitions for text output destinations."""

import sys
from abc import ABC, abstractmethod


class OutputInterfaceAbstraction(ABC):
    """Contract for objects capable of printing messages."""

    @abstractmethod
    def write_message(self, message: str) -> None:
        """Write ``message`` to the configured output channel."""

    def write_separator(self, char: str = "-", length: int = 40) -> None:
        """Output ``length`` repetitions of ``char`` as a separator line."""
        self.write_message(char * length)