import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QGraphicsScene, QGraphicsPixmapItem,
    QFileDialog, QListWidget, QListWidgetItem, QPushButton, QGraphicsView,
    QGraphicsItem, QGraphicsTextItem, QGraphicsRectItem
)
from PySide6.QtGui import QPixmap, QPainter, QPen, QBrush, QCursor
from PySide6.QtCore import Qt, QRectF, QPointF, QFile
from PySide6.QtPdf import QPdfDocument
from PySide6.QtUiTools import QUiLoader

# Basis-Klasse für ein resizables Rechteck
class DraggableBox(QGraphicsRectItem):
    def __init__(self, rect: QRectF, label="", parent=None):
        super().__init__(rect, parent)
        self.setFlags(QGraphicsItem.ItemIsMovable |
                      QGraphicsItem.ItemIsSelectable |
                      QGraphicsItem.ItemSendsGeometryChanges |
                      QGraphicsItem.ItemIsFocusable)
        self.setAcceptHoverEvents(True)
        self.setPen(QPen(Qt.black, 2))  # Standard-Pen, wird ggf. überschrieben
        self.setBrush(QBrush(Qt.transparent))
        self.label = label
        self.posText = QGraphicsTextItem(self)
        self.updatePosText()
        self._resizeMargins = 5
        self._resizeEdges = {'left': False, 'right': False, 'top': False, 'bottom': False}
        self._resizing = False
        self._dragStartPos = None
        self._initialRect = self.rect()
        self._initialScenePos = self.pos()

    def updatePosText(self):
        # Zeigt das statische Label an, falls gesetzt, ansonsten Koordinaten
        if self.label:
            self.posText.setPlainText(self.label)
        else:
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

# BoxPair: Erstellt ein Paar zusammengehöriger Boxen
class BoxPair:
    _next_id = 1
    _free_ids = []
    
    def __init__(self, scene, startPos=QPointF(50, 50)):
        if BoxPair._free_ids:
            self.id = min(BoxPair._free_ids)
            BoxPair._free_ids.remove(self.id)
        else:
            self.id = BoxPair._next_id
            BoxPair._next_id += 1

        rect = QRectF(0, 0, 100, 50)
        # Erstes Rechteck: roter Rahmen, Label "USR<id>"
        self.box1 = DraggableBox(rect, label=f"USR{self.id}")
        self.box1.setPos(startPos)
        self.box1.setPen(QPen(Qt.red, 2))
        # Zweites Rechteck: blauer Rahmen, Label "NR<id>" – leicht versetzt
        offset = QPointF(120, 0)
        self.box2 = DraggableBox(rect, label=f"NR{self.id}")
        self.box2.setPos(startPos + offset)
        self.box2.setPen(QPen(Qt.blue, 2))
        scene.addItem(self.box1)
        scene.addItem(self.box2)
        self.scene = scene

    def remove_from_scene(self):
        self.scene.removeItem(self.box1)
        self.scene.removeItem(self.box2)
        # Den verwendeten Index wieder freigeben
        if self.id not in BoxPair._free_ids:
            BoxPair._free_ids.append(self.id)

    def __str__(self):
        return f"BoxPair {self.id}"

# SingleBox: Erstellt eine einzelne Box mit grünem Rahmen und Label "DATE<id>"
class SingleBox(DraggableBox):
    _next_id = 1
    _free_ids = []
    
    def __init__(self, rect: QRectF, parent=None):
        if SingleBox._free_ids:
            self.id = min(SingleBox._free_ids)
            SingleBox._free_ids.remove(self.id)
        else:
            self.id = SingleBox._next_id
            SingleBox._next_id += 1
        label = f"DATE{self.id}"
        super().__init__(rect, label, parent)
        self.setPen(QPen(Qt.green, 2))

    def remove_from_scene(self):
        if self.scene():
            self.scene().removeItem(self)
        if self.id not in SingleBox._free_ids:
            SingleBox._free_ids.append(self.id)

# MainWindow: Lädt die UI aus der .ui-Datei und implementiert die Logik
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        loader = QUiLoader()
        ui_file = QFile("src/pdf_display.ui")
        ui_file.open(QFile.ReadOnly)
        self.ui = loader.load(ui_file, self)
        ui_file.close()
        self.setCentralWidget(self.ui)
        
        # Widgets aus der UI
        self.graphicsView = self.ui.findChild(QGraphicsView, "graphicsView")
        self.btnLoadPDF = self.ui.findChild(QPushButton, "btnLoadPDF")
        self.btnAddBoxPair = self.ui.findChild(QPushButton, "btnAddBoxPair")
        self.btnRemoveBoxPair = self.ui.findChild(QPushButton, "btnRemoveBoxPair")
        self.btnZoomIn = self.ui.findChild(QPushButton, "btnZoomIn")
        self.btnZoomOut = self.ui.findChild(QPushButton, "btnZoomOut")
        self.btnAddSingleBox = self.ui.findChild(QPushButton, "btnAddSingleBox")
        self.listBoxPairs = self.ui.findChild(QListWidget, "listBoxPairs")
        
        # Signale verbinden
        self.btnLoadPDF.clicked.connect(self.load_pdf)
        self.btnAddBoxPair.clicked.connect(self.add_box_pair)
        self.btnRemoveBoxPair.clicked.connect(self.remove_selected_item)
        self.btnZoomIn.clicked.connect(self.zoom_in)
        self.btnZoomOut.clicked.connect(self.zoom_out)
        self.btnAddSingleBox.clicked.connect(self.add_single_box)
        
        # Scene und PDF-Dokument initialisieren
        self.scene = QGraphicsScene(self)
        self.graphicsView.setScene(self.scene)
        self.graphicsView.setRenderHint(QPainter.Antialiasing)
        self.pdfDocument = QPdfDocument(self)
        self.boxPairs = []
        self.singleBoxes = []

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
        # Vorhandene BoxPairs und SingleBoxes wieder hinzufügen
        for pair in self.boxPairs:
            self.scene.addItem(pair.box1)
            self.scene.addItem(pair.box2)
        for single in self.singleBoxes:
            self.scene.addItem(single)

    def add_box_pair(self):
        newPair = BoxPair(self.scene, QPointF(50, 50))
        self.boxPairs.append(newPair)
        listItem = QListWidgetItem(str(newPair))
        listItem.setData(Qt.UserRole, newPair)
        self.listBoxPairs.addItem(listItem)

    def add_single_box(self):
        rect = QRectF(0, 0, 100, 50)
        newSingle = SingleBox(rect)
        newSingle.setPos(QPointF(50, 50))
        self.scene.addItem(newSingle)
        self.singleBoxes.append(newSingle)
        listItem = QListWidgetItem(f"BoxSingle {newSingle.id}")
        listItem.setData(Qt.UserRole, newSingle)
        self.listBoxPairs.addItem(listItem)

    def remove_selected_item(self):
        selectedItems = self.listBoxPairs.selectedItems()
        for item in selectedItems:
            obj = item.data(Qt.UserRole)
            if isinstance(obj, BoxPair):
                obj.remove_from_scene()
                self.boxPairs.remove(obj)
            elif isinstance(obj, SingleBox):
                obj.remove_from_scene()
                self.singleBoxes.remove(obj)
            row = self.listBoxPairs.row(item)
            self.listBoxPairs.takeItem(row)

    def zoom_in(self):
        self.graphicsView.scale(1.2, 1.2)

    def zoom_out(self):
        self.graphicsView.scale(1/1.2, 1/1.2)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Delete:
            self.remove_selected_item()
        else:
            super().keyPressEvent(event)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
