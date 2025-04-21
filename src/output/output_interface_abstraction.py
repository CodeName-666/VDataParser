import sys
from abc import ABC, abstractmethod



class OutputInterfaceAbstraction(ABC):
    """
    Abstrakte Basisklasse für Ausgabemechanismen.
    Definiert das Interface, das alle konkreten Ausgabeklassen implementieren müssen.
    """
    @abstractmethod
    def write_message(self, message: str):
        """
        Schreibt eine Nachricht an das definierte Ausgabeziel.

        Args:
            message (str): Die auszugebende Nachricht.
        """
        pass # Konkrete Klassen müssen dies implementieren

    def write_separator(self, char: str = '-', length: int = 40):
        """Eine optionale Hilfsmethode für eine Trennlinie."""
        self.write_message(char * length)