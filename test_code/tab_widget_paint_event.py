from PySide6.QtWidgets import QApplication, QWidget, QTabWidget, QTabBar, QVBoxLayout
from PySide6.QtGui import QPainter, QColor, QFont
from PySide6.QtCore import Qt

class CustomTabWidget(QTabWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        # Store the chosen shape; use QTabWidget.TabShape enum values
        self._tab_shape = QTabWidget.TabShape.Rounded

    def paintEvent(self, event):
        painter = QPainter(self)
        # Enable antialiasing
        painter.setRenderHint(QPainter.Antialiasing)

        # Draw each tab using the tabBar method
        tab_bar = self.tabBar()
        for i in range(self.count()):
            tab_rect = tab_bar.tabRect(i)
            if self._tab_shape == QTabWidget.TabShape.Rounded:
                painter.setBrush(QColor(200, 500, 200))
                painter.drawRoundedRect(tab_rect, 5, 5)
            elif self._tab_shape == QTabWidget.TabShape.Triangular:
                # Custom triangular tab drawing
                points = [
                    tab_rect.topLeft(),
                    tab_rect.topRight(),
                    tab_rect.bottomLeft(),
                ]
                painter.setBrush(QColor(150, 200, 150))
                painter.drawPolygon(points)

            painter.setPen(QColor(0, 0, 0))
            painter.setFont(QFont("Arial", 10))
            painter.drawText(tab_rect, Qt.AlignmentFlag.AlignCenter, tab_bar.tabText(i))

        # Paint content background
        content_rect = self.contentsRect()
        painter.fillRect(content_rect, QColor(20, 240, 240))

        # Call base implementation to draw child widgets
        super().paintEvent(event)

    def setTabShape(self, shape: QTabWidget.TabShape):
        self._tab_shape = shape
        self.update()


class Example(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("QTabWidget PaintEvent Example (PySide6)")
        self.setGeometry(300, 300, 400, 300)

        layout = QVBoxLayout(self)
        self.tab_widget = CustomTabWidget()
        # Add sample tabs
        self.tab_widget.addTab(QWidget(), "Tab 1")
        self.tab_widget.addTab(QWidget(), "Tab 2")
        self.tab_widget.addTab(QWidget(), "Tab 3")

        # Set initial shape
        self.tab_widget.setTabShape(QTabWidget.TabShape.Rounded)
        layout.addWidget(self.tab_widget)
        self.setLayout(layout)


if __name__ == "__main__":
    app = QApplication([])
    example = Example()
    example.show()
    app.exec()
