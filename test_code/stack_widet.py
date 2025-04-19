from PySide6.QtWidgets import QApplication, QMainWindow, QStackedWidget, QWidget, QVBoxLayout, QPushButton

class Page1(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout()
        btn = QPushButton("Wechsel zu Seite 2")
        btn.clicked.connect(self.go_to_page2)
        layout.addWidget(btn)
        self.setLayout(layout)

    def go_to_page2(self):
        # Signal an MainWindow senden, um die Seite zu wechseln (z.B. über einen Callback oder ein Signal)
        self.parent().setCurrentIndex(1)

class Page2(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout()
        btn = QPushButton("Wechsel zu Seite 1")
        btn.clicked.connect(self.go_to_page1)
        layout.addWidget(btn)
        self.setLayout(layout)

    def go_to_page1(self):
        self.parent().setCurrentIndex(0)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("QStackedWidget Beispiel")
        
        # QStackedWidget erstellen
        self.stack = QStackedWidget()
        
        # Seiten erstellen und hinzufügen
        self.page1 = Page1(self.stack)
        self.page2 = Page2(self.stack)
        self.stack.addWidget(self.page1)
        self.stack.addWidget(self.page2)
        
        # Das QStackedWidget als zentrales Widget setzen
        self.setCentralWidget(self.stack)

if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())
