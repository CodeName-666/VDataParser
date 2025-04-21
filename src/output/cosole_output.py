from .output_interface_abstraction import OutputInterfaceAbstraction


class ConsoleOutput(OutputInterfaceAbstraction):
    """
    Implementierung von OutputInterface für die Standard-Konsolenausgabe (print).
    """
    def write_message(self, message: str):
        """Gibt die Nachricht auf der Konsole aus."""
        print(message)