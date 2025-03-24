import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QGraphicsView, QGraphicsScene,
    QGraphicsPixmapItem, QGraphicsRectItem, QGraphicsTextItem,
    QPushButton, QVBoxLayout, QHBoxLayout, QWidget, QFileDialog
)
from PySide6.QtGui import QPixmap, QPainter, QPen, QBrush, QCursor
from PySide6.QtCore import Qt, QRectF, QPointF
from PySide6.QtPdf import QPdfDocument
from PySide6.QtWidgets import QGraphicsItem

class DraggableBox(QGraphicsRectItem):
    def __init__(self, rect: QRectF, parent=None):
        super().__init__(rect, parent)
        # Ermögliche Verschieben, Auswählen, Fokussierung und sende Geometrieänderungen
        self.setFlags(QGraphicsItem.ItemIsMovable |
                      QGraphicsItem.ItemIsSelectable |
                      QGraphicsItem.ItemSendsGeometryChanges |
                      QGraphicsItem.ItemIsFocusable)
        # Erforderlich, damit Hover-Events ankommen
        self.setAcceptHoverEvents(True)
        self.setPen(QPen(Qt.black, 2))
        self.setBrush(QBrush(Qt.transparent))

        # Text, der die aktuelle Position anzeigt (als Kind-Item)
        self.posText = QGraphicsTextItem(self)
        self.updatePosText()

        # Attribute für Resizing
        self._resizeMargins = 5  # Abstand in Pixeln vom Rand, ab dem resizen möglich ist
        self._resizeEdges = {'left': False, 'right': False, 'top': False, 'bottom': False}
        self._resizing = False
        self._dragStartPos = None
        self._initialRect = self.rect()
        self._initialScenePos = self.pos()

    def updatePosText(self):
        """Aktualisiert den Text, der die aktuelle Szenenposition anzeigt."""
        pos = self.scenePos()
        self.posText.setPlainText(f"X: {int(pos.x())} | Y: {int(pos.y())}")
        # Positioniere den Text oberhalb der Box (anpassbar)
        self.posText.setPos(0, -20)

    def hoverMoveEvent(self, event):
        """Ändert den Cursor, wenn sich der Mauszeiger über den Rändern befindet."""
        pos = event.pos()  # Mausposition in Item-Koordinaten
        rect = self.rect()
        margin = self._resizeMargins
        left   = pos.x() < margin
        right  = pos.x() > rect.width() - margin
        top    = pos.y() < margin
        bottom = pos.y() > rect.height() - margin

        self._resizeEdges = {'left': left, 'right': right, 'top': top, 'bottom': bottom}

        # Cursor je nach Kante bzw. Ecke setzen:
        if (left and top) or (right and bottom):
            self.setCursor(Qt.SizeFDiagCursor)
        elif (right and top) or (left and bottom):
            self.setCursor(Qt.SizeBDiagCursor)
        elif left or right:
            self.setCursor(Qt.SizeHorCursor)
        elif top or bottom:
            self.setCursor(Qt.SizeVerCursor)
        else:
            self.setCursor(Qt.OpenHandCursor)
        super().hoverMoveEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            # Wenn der Mauszeiger an einem Rand ist, starte den Resize-Modus.
            if any(self._resizeEdges.values()):
                self._resizing = True
                self._dragStartPos = event.pos()  # in Item-Koordinaten
                self._initialRect = self.rect()
                self._initialScenePos = QPointF(self.pos())
                event.accept()
                return
            else:
                self.setCursor(Qt.ClosedHandCursor)
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._resizing:
            delta = event.pos() - self._dragStartPos  # Veränderung in lokalen Koordinaten
            newRect = QRectF(self._initialRect)
            newPos = QPointF(self._initialScenePos)
            minWidth = 20
            minHeight = 20

            # Resizing von der linken Kante:
            if self._resizeEdges['left']:
                newWidth = self._initialRect.width() - delta.x()
                if newWidth < minWidth:
                    delta_x = self._initialRect.width() - minWidth
                    newWidth = minWidth
                else:
                    delta_x = delta.x()
                newRect.setLeft(newRect.left() + delta_x)
                newRect.setWidth(newWidth)
                newPos.setX(self._initialScenePos.x() + delta_x)

            # Resizing von der rechten Kante:
            if self._resizeEdges['right']:
                newWidth = self._initialRect.width() + delta.x()
                if newWidth < minWidth:
                    newWidth = minWidth
                newRect.setWidth(newWidth)

            # Resizing von der oberen Kante:
            if self._resizeEdges['top']:
                newHeight = self._initialRect.height() - delta.y()
                if newHeight < minHeight:
                    delta_y = self._initialRect.height() - minHeight
                    newHeight = minHeight
                else:
                    delta_y = delta.y()
                newRect.setTop(newRect.top() + delta_y)
                newRect.setHeight(newHeight)
                newPos.setY(self._initialScenePos.y() + delta_y)

            # Resizing von der unteren Kante:
            if self._resizeEdges['bottom']:
                newHeight = self._initialRect.height() + delta.y()
                if newHeight < minHeight:
                    newHeight = minHeight
                newRect.setHeight(newHeight)

            # Damit die lokalen Koordinaten stets bei (0,0) beginnen,
            # transformiere das Rechteck in ein neues mit Ursprung (0,0)
            finalRect = QRectF(0, 0, newRect.width(), newRect.height())
            self.setRect(finalRect)
            self.setPos(newPos)
            self.updatePosText()
            event.accept()
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self._resizing:
            self._resizing = False
        else:
            self.setCursor(Qt.OpenHandCursor)
        super().mouseReleaseEvent(event)

    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemPositionHasChanged:
            self.updatePosText()
        return super().itemChange(change, value)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PDF Editor mit resizbaren Box-Overlays")
        self.resize(900, 700)

        # Initialisiere das PDF-Dokument
        self.pdfDocument = QPdfDocument(self)

        # QGraphicsScene und QGraphicsView für PDF und Overlays
        self.scene = QGraphicsScene(self)
        self.view = QGraphicsView(self.scene, self)
        self.view.setRenderHint(QPainter.Antialiasing)

        # Steuerelemente:
        # PDF laden, Box hinzufügen, Box löschen
        self.loadPdfButton = QPushButton("PDF laden")
        self.loadPdfButton.clicked.connect(self.load_pdf)

        self.addBoxButton = QPushButton("+")
        self.addBoxButton.clicked.connect(self.add_box)

        self.removeBoxButton = QPushButton("-")
        self.removeBoxButton.clicked.connect(self.remove_box)

        controlLayout = QHBoxLayout()
        controlLayout.addWidget(self.loadPdfButton)
        controlLayout.addWidget(self.addBoxButton)
        controlLayout.addWidget(self.removeBoxButton)

        mainLayout = QVBoxLayout()
        mainLayout.addLayout(controlLayout)
        mainLayout.addWidget(self.view)

        centralWidget = QWidget()
        centralWidget.setLayout(mainLayout)
        self.setCentralWidget(centralWidget)

    def load_pdf(self):
        """Öffnet einen Dateidialog, lädt die PDF und rendert die erste Seite."""
        fileName, _ = QFileDialog.getOpenFileName(
            self, "PDF Datei öffnen", "", "PDF Dateien (*.pdf)"
        )
        if fileName:
            status = self.pdfDocument.load(fileName)
            if status == QPdfDocument.Error.None_:
                self.load_page(0)  # Lade die erste Seite
            else:
                print("Fehler beim Laden der PDF.")

    def load_page(self, page: int):
        """Rendert die angegebene PDF-Seite und zeigt sie in der Scene an."""
        pageSizeF = self.pdfDocument.pagePointSize(page)
        pageSize = pageSizeF.toSize()
        image = self.pdfDocument.render(page, pageSize)
        if image.isNull():
            print("Fehler beim Rendern der Seite.")
            return

        pixmap = QPixmap.fromImage(image)
        self.scene.clear()  # Vorherige Inhalte entfernen
        self.pdf_item = QGraphicsPixmapItem(pixmap)
        # Den PDF-Hintergrund nicht auswählbar machen
        self.pdf_item.setFlag(QGraphicsItem.ItemIsSelectable, False)
        self.scene.addItem(self.pdf_item)
        self.scene.setSceneRect(pixmap.rect())

    def add_box(self):
        """Fügt eine neue, resizable Box in die Scene ein."""
        rect = QRectF(0, 0, 100, 50)
        box = DraggableBox(rect)
        box.setPos(50, 50)
        self.scene.addItem(box)

    def remove_box(self):
        """Löscht alle ausgewählten Boxen aus der Scene."""
        for item in self.scene.selectedItems():
            if isinstance(item, DraggableBox):
                self.scene.removeItem(item)

    def keyPressEvent(self, event):
        """Ermöglicht das Löschen von Boxen per Entf-Taste."""
        if event.key() == Qt.Key_Delete:
            self.remove_box()
        else:
            super().keyPressEvent(event)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
