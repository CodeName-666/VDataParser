"""Qt based output widget helper."""

from .output_interface_abstraction import OutputInterfaceAbstraction
from PySide6.QtWidgets import QTextEdit, QPlainTextEdit
from PySide6.QtCore import Slot


class QtOutput(OutputInterfaceAbstraction):
    """Send messages to a ``QTextEdit`` or ``QPlainTextEdit`` widget."""

    def __init__(self, output_widget: QTextEdit | QPlainTextEdit):
        """Store the widget that receives output."""
        if not isinstance(output_widget, (QTextEdit, QPlainTextEdit)):
            raise TypeError(
                "output_widget must be a QTextEdit or QPlainTextEdit instance."
            )
        self.output_widget = output_widget

    # @Slot(str)
    def write_message(self, message: str) -> None:
        """Append ``message`` to the underlying widget."""
        if isinstance(self.output_widget, QPlainTextEdit):
            self.output_widget.appendPlainText(message)
        else:
            self.output_widget.append(message)
