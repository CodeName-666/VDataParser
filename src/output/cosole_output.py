from .output_interface import OutputInterface


class ConsoleOutput(OutputInterface):
    """
    Implementierung von OutputInterface für die Standard-Konsolenausgabe (print).
    """
    def write_message(self, message: str):
        """Gibt die Nachricht auf der Konsole aus."""
        print(message)