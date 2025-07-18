"""Qt based output widget helper."""

from .output_interface_abstraction import OutputInterfaceAbstraction
from PySide6.QtWidgets import (
    QTextEdit,
    QPlainTextEdit,
    QTableWidget,
    QTableWidgetItem,
    QListWidget,
    QListWidgetItem,
    QStyle,
)
from PySide6.QtCore import Slot


class QtOutput(OutputInterfaceAbstraction):
    """Send messages to a Qt text or table widget."""

    def __init__(
        self,
        output_widget: QTextEdit | QPlainTextEdit | QTableWidget | QListWidget,
    ) -> None:
        """Store the widget that receives output."""
        if not isinstance(
            output_widget,
            (QTextEdit, QPlainTextEdit, QTableWidget, QListWidget),
        ):
            raise TypeError(
                "output_widget must be a QTextEdit, QPlainTextEdit, QTableWidget or QListWidget instance."
            )
        self.output_widget = output_widget

    # @Slot(str)
    def write_message(self, message: str) -> None:
        """Append ``message`` to the underlying widget."""
        if isinstance(self.output_widget, QListWidget):
            level = ""
            text = message
            parts = message.split(" ", 1)
            if parts and parts[0] in {"INFO", "WARNING", "ERROR", "CRITICAL"}:
                level = parts[0]
                text = parts[1] if len(parts) > 1 else ""

            icon = None
            if level == "INFO":
                icon = self.output_widget.style().standardIcon(QStyle.SP_MessageBoxInformation)
            elif level == "WARNING":
                icon = self.output_widget.style().standardIcon(QStyle.SP_MessageBoxWarning)
            elif level in {"ERROR", "CRITICAL"}:
                icon = self.output_widget.style().standardIcon(QStyle.SP_MessageBoxCritical)

            item = QListWidgetItem(text)
            if icon is not None:
                item.setIcon(icon)
            self.output_widget.addItem(item)
            self.output_widget.scrollToBottom()
        elif isinstance(self.output_widget, QTableWidget):
            level = ""
            text = message
            parts = message.split(" ", 1)
            if parts and parts[0] in {"INFO", "WARNING", "ERROR", "CRITICAL"}:
                level = parts[0]
                text = parts[1] if len(parts) > 1 else ""
            row = self.output_widget.rowCount()
            self.output_widget.insertRow(row)

            item_level = QTableWidgetItem(level[:1])
            icon = None
            if level == "INFO":
                icon = self.output_widget.style().standardIcon(QStyle.SP_MessageBoxInformation)
            elif level == "WARNING":
                icon = self.output_widget.style().standardIcon(QStyle.SP_MessageBoxWarning)
            elif level in {"ERROR", "CRITICAL"}:
                icon = self.output_widget.style().standardIcon(QStyle.SP_MessageBoxCritical)
            if icon is not None:
                item_level.setIcon(icon)
            self.output_widget.setItem(row, 0, item_level)
            self.output_widget.setItem(row, 1, QTableWidgetItem(text))
            self.output_widget.scrollToBottom()
        elif isinstance(self.output_widget, QPlainTextEdit):
            self.output_widget.appendPlainText(message)
        else:
            self.output_widget.append(message)
