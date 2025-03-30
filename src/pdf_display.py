import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QGraphicsView, QGraphicsScene,
    QGraphicsPixmapItem, QGraphicsRectItem, QGraphicsTextItem,
    QPushButton, QVBoxLayout, QHBoxLayout, QWidget, QFileDialog,
    QListWidget, QListWidgetItem
)
from PySide6.QtGui import QPixmap, QPainter, QPen, QBrush, QCursor
from PySide6.QtCore import Qt, QRectF, QPointF
from PySide6.QtPdf import QPdfDocument
from PySide6.QtWidgets import QGraphicsItem


# Bestehende Klasse für ein einzelnes, resizables Rechteck
class DraggableBox(QGraphicsRectItem):
    def __init__(self, rect: QRectF, parent=None):
        super().__init__(rect, parent)
        self.setFlags(QGraphicsItem.ItemIsMovable |
                      QGraphicsItem.ItemIsSelectable |
                      QGraphicsItem.ItemSendsGeometryChanges |
                      QGraphicsItem.ItemIsFocusable)
        self.setAcceptHoverEvents(True)
        self.setPen(QPen(Qt.black, 2))
        self.setBrush(QBrush(Qt.transparent))
        self.posText = QGraphicsTextItem(self)
        self.updatePosText()
        self._resizeMargins = 5
        self._resizeEdges = {'left': False, 'right': False, 'top': False, 'bottom': False}
        self._resizing = False
        self._dragStartPos = None
        self._initialRect = self.rect()
        self._initialScenePos = self.pos()

    def updatePosText(self):
        pos = self.scenePos()
        self.posText.setPlainText(f"X: {int(pos.x())} | Y: {int(pos.y())}")
        self.posText.setPos(0, -20)

    def hoverMoveEvent(self, event):
        pos = event.pos()
        rect = self.rect()
        margin = self._resizeMargins
        left   = pos.x() < margin
        right  = pos.x() > rect.width() - margin
        top    = pos.y() < margin
        bottom = pos.y() > rect.height() - margin
        self._resizeEdges = {'left': left, 'right': right, 'top': top, 'bottom': bottom}
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
            if any(self._resizeEdges.values()):
                self._resizing = True
                self._dragStartPos = event.pos()
                self._initialRect = self.rect()
                self._initialScenePos = QPointF(self.pos())
                event.accept()
                return
            else:
                self.setCursor(Qt.ClosedHandCursor)
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._resizing:
            delta = event.pos() - self._dragStartPos
            newRect = QRectF(self._initialRect)
            newPos = QPointF(self._initialScenePos)
            minWidth = 20
            minHeight = 20

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

            if self._resizeEdges['right']:
                newWidth = self._initialRect.width() + delta.x()
                if newWidth < minWidth:
                    newWidth = minWidth
                newRect.setWidth(newWidth)

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

            if self._resizeEdges['bottom']:
                newHeight = self._initialRect.height() + delta.y()
                if newHeight < minHeight:
                    newHeight = minHeight
                newRect.setHeight(newHeight)

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

# Neue Klasse, die immer zusammengehörige Rechtecke (ein Paar) erstellt
# Neue Klasse, die immer zusammengehörige Rechtecke (ein Paar) erstellt
class BoxPair:
    _id_counter = 1

    def __init__(self, scene, startPos=QPointF(50, 50)):
        self.id = BoxPair._id_counter
        BoxPair._id_counter += 1
        rect = QRectF(0, 0, 100, 50)
        # Erstes Rechteck (rot)
        self.box1 = DraggableBox(rect)
        self.box1.setPos(startPos)
        self.box1.setBrush(QBrush(Qt.red))
        # Zweites Rechteck (blau), leicht versetzt
        offset = QPointF(120, 0)
        self.box2 = DraggableBox(rect)
        self.box2.setPos(startPos + offset)
        self.box2.setBrush(QBrush(Qt.blue))
        # Beide Rechtecke in die Scene einfügen
        scene.addItem(self.box1)
        scene.addItem(self.box2)
        self.scene = scene

    def remove_from_scene(self):
        self.scene.removeItem(self.box1)
        self.scene.removeItem(self.box2)

    def __str__(self):
        return f"BoxPair {self.id}"


# Hauptfenster mit erweiterter UI
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PDF Editor mit resizbaren Box-Overlays")
        self.resize(900, 700)

        self.pdfDocument = QPdfDocument(self)
        self.scene = QGraphicsScene(self)
        self.view = QGraphicsView(self.scene, self)
        self.view.setRenderHint(QPainter.Antialiasing)

        # Liste, in der die BoxPairs verwaltet werden
        self.boxPairs = []

        # Seitenmenü mit Steuerungselementen und Liste
        self.sideMenu = QWidget()
        sideLayout = QVBoxLayout()

        self.loadPdfButton = QPushButton("PDF laden")
        self.loadPdfButton.clicked.connect(self.load_pdf)

        self.addBoxPairButton = QPushButton("+")
        self.addBoxPairButton.clicked.connect(self.add_box_pair)

        self.removeBoxPairButton = QPushButton("-")
        self.removeBoxPairButton.clicked.connect(self.remove_box_pair)

        # Liste zur Anzeige der erstellten BoxPairs
        self.boxPairListWidget = QListWidget()

        sideLayout.addWidget(self.loadPdfButton)
        sideLayout.addWidget(self.addBoxPairButton)
        sideLayout.addWidget(self.removeBoxPairButton)
        sideLayout.addWidget(self.boxPairListWidget)
        sideLayout.addStretch()
        self.sideMenu.setLayout(sideLayout)

        # Hauptlayout: PDF-View links, Seitenmenü rechts
        mainLayout = QHBoxLayout()
        mainLayout.addWidget(self.view, stretch=3)
        mainLayout.addWidget(self.sideMenu, stretch=1)

        centralWidget = QWidget()
        centralWidget.setLayout(mainLayout)
        self.setCentralWidget(centralWidget)

    def load_pdf(self):
        fileName, _ = QFileDialog.getOpenFileName(
            self, "PDF Datei öffnen", "", "PDF Dateien (*.pdf)"
        )
        if fileName:
            status = self.pdfDocument.load(fileName)
            if status == QPdfDocument.Error.None_:
                self.load_page(0)
            else:
                print("Fehler beim Laden der PDF.")

    def load_page(self, page: int):
        pageSizeF = self.pdfDocument.pagePointSize(page)
        pageSize = pageSizeF.toSize()
        image = self.pdfDocument.render(page, pageSize)
        if image.isNull():
            print("Fehler beim Rendern der Seite.")
            return
        pixmap = QPixmap.fromImage(image)
        self.scene.clear()
        self.pdf_item = QGraphicsPixmapItem(pixmap)
        self.pdf_item.setFlag(QGraphicsItem.ItemIsSelectable, False)
        self.scene.addItem(self.pdf_item)
        self.scene.setSceneRect(pixmap.rect())
        # Bestehende BoxPairs erneut hinzufügen
        for pair in self.boxPairs:
            self.scene.addItem(pair.box1)
            self.scene.addItem(pair.box2)

    def add_box_pair(self):
        # Erstelle ein neues BoxPair, füge es der Scene und der Liste hinzu
        newPair = BoxPair(self.scene, QPointF(50, 50))
        self.boxPairs.append(newPair)
        listItem = QListWidgetItem(str(newPair))
        listItem.setData(Qt.UserRole, newPair)
        self.boxPairListWidget.addItem(listItem)

    def remove_box_pair(self):
        # Entferne das ausgewählte BoxPair
        selectedItems = self.boxPairListWidget.selectedItems()
        for item in selectedItems:
            boxPair = item.data(Qt.UserRole)
            if boxPair in self.boxPairs:
                boxPair.remove_from_scene()
                self.boxPairs.remove(boxPair)
            row = self.boxPairListWidget.row(item)
            self.boxPairListWidget.takeItem(row)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Delete:
            self.remove_box_pair()
        else:
            super().keyPressEvent(event)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
