from PySide6.QtCore import Qt, QTimer, Slot, QPoint
from PySide6.QtWidgets import (
    QStatusBar,
    QLabel,
    QWidget,
    QSizePolicy,
    QListWidget,
    QListWidgetItem,
    QVBoxLayout,
)
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QStyle


class StatusBar(QStatusBar):
    """Custom status bar with message queue and connection indicator."""

    def __init__(self, parent: QWidget | None = None) -> None:
        """Initialise labels, LED and internal timers.

        Parameters
        ----------
        parent:
            Optional parent widget.
        """
        super().__init__(parent)
        self.setObjectName("statusbar")
        self.setSizeGripEnabled(True)

        # Info-Label für Statusnachrichten
        self.info_label = QLabel()
        self.info_label.setText("")  # Leer initial
        self.info_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.info_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

        # Message history
        self._message_history: list[tuple[str, str]] = []
        self._history_limit = 10

        # Platzhalter, um Widgets auseinander zu schieben
        self.horizontalSpacer = QWidget()
        self.horizontalSpacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

        # Connection Label und LED
        self.connection_label = QLabel()
        self.connection_label.setText("Disconnected")

        self.status_led = QLabel()
        self.status_led.setFixedSize(12, 12)
        self.status_led.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.set_led_color("red")

        # Widgets zur StatusBar hinzufügen
        self.addWidget(self.info_label)
        self.addWidget(self.horizontalSpacer)
        self.addPermanentWidget(self.connection_label)
        self.addPermanentWidget(self.status_led)

        # Verantwortlich für Datenbank-Status (nur Beispiel)
        QTimer.singleShot(3000, self.set_connected)

        # Queue und Timer für sequentielle Anzeige von Nachrichten
        self._message_queue: list[tuple[str, str]] = []
        self._message_timer = QTimer(self)
        self._message_timer.setSingleShot(True)
        self._message_timer.timeout.connect(self._show_next_message)

        # Popup for message history
        self._history_popup: QWidget | None = None
        self.info_label.mousePressEvent = self._on_info_label_clicked

    def set_led_color(self, color: str) -> None:
        """Change the LED color of the connection indicator.

        Parameters
        ----------
        color:
            Name of the CSS color to apply.
        """
        self.status_led.setStyleSheet(
            f"""
            QLabel {{
                background-color: {color};
                border-radius: 6px;
                border: 1px solid black;
            }}
            """
        )

    def set_connected(self) -> None:
        """Switch the indicator to the connected state."""
        self.connection_label.setText("Verbindung: Aktiv")
        self.set_led_color("green")
        # Inform the user about the new connection
        self.post_message("Datenbank verbunden")

    def _add_to_history(self, message: str, level: str) -> None:
        """Store ``message`` in the internal history list."""
        self._message_history.append((message, level))
        if len(self._message_history) > self._history_limit:
            self._message_history.pop(0)

    def _enqueue_message(self, message: str, level: str) -> None:
        """Add ``message`` to the queue and trigger display if idle."""
        self._add_to_history(message, level)
        self._message_queue.append((message, level))
        if not self._message_timer.isActive():
            self._show_next_message()

    @Slot(str, str)
    def handle_status(self, level: str, message: str) -> None:
        """General entry point for status messages.

        Parameters
        ----------
        level:
            Severity level of the message (``info``, ``warning`` or ``error``).
        message:
            The human readable text.
        """
        level = level.lower()
        if level == "warning":
            self.post_warning(message)
        elif level == "error":
            self.post_error(message)
        else:
            self.post_message(message)

    @Slot(str)
    def post_message(self, message: str) -> None:
        """Add an informational message to the queue."""
        self._enqueue_message(message, "info")

    @Slot(str)
    def post_warning(self, message: str) -> None:
        """Add a warning message to the queue."""
        self._enqueue_message(message, "warning")

    @Slot(str)
    def post_error(self, message: str) -> None:
        """Add an error message to the queue."""
        self._enqueue_message(message, "error")

    def _show_next_message(self) -> None:
        """Display the next queued message if available."""
        if self._message_queue:
            text, _level = self._message_queue.pop(0)
            self.info_label.setText(text)
            self._message_timer.start(3000)
        else:
            self.info_label.setText("")

    def _on_info_label_clicked(self, event) -> None:
        """Open the history popup when the label is clicked.

        Parameters
        ----------
        event:
            Mouse event triggering the handler.
        """
        self._show_history_popup()
        if event:
            event.accept()

    def _show_history_popup(self) -> None:
        """Display a popup with the last messages that were shown."""
        if self._history_popup is None:
            self._history_popup = QWidget(self, Qt.Popup)
            layout = QVBoxLayout(self._history_popup)
            self._history_list = QListWidget(self._history_popup)
            layout.addWidget(self._history_list)
            self._history_popup.setLayout(layout)

        self._history_list.clear()
        icon_map = {
            "info": self.style().standardIcon(QStyle.SP_MessageBoxInformation),
            "warning": self.style().standardIcon(QStyle.SP_MessageBoxWarning),
            "error": self.style().standardIcon(QStyle.SP_MessageBoxCritical),
        }
        for text, level in reversed(self._message_history):
            item = QListWidgetItem(icon_map.get(level, QIcon()), text)
            self._history_list.addItem(item)

        self._history_popup.adjustSize()
        height = self._history_popup.height()
        pos = self.info_label.mapToGlobal(QPoint(0, -height))
        self._history_popup.move(pos)
        self._history_popup.show()
