import sys
import os
import json
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QGraphicsScene, QGraphicsPixmapItem,
    QFileDialog, QListWidget, QListWidgetItem, QPushButton, QGraphicsView,
    QGraphicsItem, QGraphicsTextItem, QGraphicsRectItem, QWidget
)
from PySide6.QtGui import QPixmap, QPainter, QPen, QBrush, QCursor
from PySide6.QtCore import Qt, QRectF, QPointF, Signal
from PySide6.QtPdf import QPdfDocument

# Importiere die konvertierte UI-Klasse
from .generated import PdfDisplayUi
from .base_ui import BaseUi


class DraggableBox(QGraphicsRectItem):
    def __init__(self, rect: QRectF, label="", parent=None):
        super().__init__(rect, parent)
        self.setFlags(
            QGraphicsItem.ItemIsMovable |
            QGraphicsItem.ItemIsSelectable |
            QGraphicsItem.ItemSendsGeometryChanges |
            QGraphicsItem.ItemIsFocusable
        )
        self.setAcceptHoverEvents(True)
        self.setPen(QPen(Qt.black, 2))  # Standard-Pen (wird ggf. überschrieben)
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
        self.box1 = DraggableBox(rect, label=f"USR{self.id}")
        self.box1.setPos(startPos)
        self.box1.setPen(QPen(Qt.red, 2))
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
        if self.id not in BoxPair._free_ids:
            BoxPair._free_ids.append(self.id)

    def __str__(self):
        return f"BoxPair {self.id}"


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


class PdfDisplay(BaseUi):

    on_exit_button_clicked: Signal = None

    def __init__(self, parent=None):
        super().__init__(parent)
        # Verwende die konvertierte UI-Klasse
        self.ui = PdfDisplayUi()
        self.ui.setupUi(self)
        
        # Zugriff auf Widgets (die Namen entsprechen denen in der .ui-Datei)
        self.graphicsView = self.ui.graphicsView
        self.btnLoadPDF = self.ui.btnLoadPDF
        self.btnAddBoxPair = self.ui.btnAddBoxPair
        self.btnRemoveBoxPair = self.ui.btnRemoveBoxPair
        self.btnZoomIn = self.ui.btnZoomIn
        self.btnZoomOut = self.ui.btnZoomOut
        self.btnAddSingleBox = self.ui.btnAddSingleBox
        self.btnSave = self.ui.btnSave
        self.btnLoad = self.ui.btnLoad
        self.listBoxPairs = self.ui.listBoxPairs
        
        self.on_exit_button_clicked = self.ui.btnClosePDF.clicked

        # Signale verbinden
        self.btnLoadPDF.clicked.connect(self.load_pdf)
        self.btnAddBoxPair.clicked.connect(self.add_box_pair)
        self.btnRemoveBoxPair.clicked.connect(self.remove_selected_item)
        self.btnZoomIn.clicked.connect(self.zoom_in)
        self.btnZoomOut.clicked.connect(self.zoom_out)
        self.btnAddSingleBox.clicked.connect(self.add_single_box)
        self.btnSave.clicked.connect(self.save_state)
        self.btnLoad.clicked.connect(self.load_state)
        
        self.scene = QGraphicsScene(self)
        self.graphicsView.setScene(self.scene)
        self.graphicsView.setRenderHint(QPainter.Antialiasing)
        self.pdfDocument = QPdfDocument(self)
        self.boxPairs = []
        self.singleBoxes = []
        self.pdfPath = ""  # Speichert den zuletzt geladenen PDF-Pfad

    def load_pdf(self):
        fileName, _ = QFileDialog.getOpenFileName(
            self, "PDF Datei öffnen", "", "PDF Dateien (*.pdf)"
        )
        if fileName:
            self.pdfPath = fileName
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
        # Entferne nur das alte PDF-Item, nicht die Boxen
        if hasattr(self, "pdf_item") and self.pdf_item is not None:
            self.scene.removeItem(self.pdf_item)
        self.pdf_item = QGraphicsPixmapItem(pixmap)
        self.pdf_item.setFlag(QGraphicsItem.ItemIsSelectable, False)
        self.scene.addItem(self.pdf_item)
        self.scene.setSceneRect(pixmap.rect())
        # Füge alle Boxen wieder hinzu
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
        self.graphicsView.scale(1 / 1.2, 1 / 1.2)

    def save_state(self):
        data = {}
        data["pdf_path"] = self.pdfPath
        data["pdf_name"] = os.path.basename(self.pdfPath)
        data["boxPairs"] = []
        for pair in self.boxPairs:
            usr_box = pair.box1
            nr_box = pair.box2
            usr_data = {
                "name": usr_box.label,
                "x": usr_box.scenePos().x(),
                "y": usr_box.scenePos().y(),
                "width": usr_box.rect().width(),
                "height": usr_box.rect().height()
            }
            nr_data = {
                "name": nr_box.label,
                "x": nr_box.scenePos().x(),
                "y": nr_box.scenePos().y(),
                "width": nr_box.rect().width(),
                "height": nr_box.rect().height()
            }
            pair_data = {"id": pair.id, "USR": usr_data, "NR": nr_data}
            data["boxPairs"].append(pair_data)
        data["singleBoxes"] = []
        for single in self.singleBoxes:
            single_data = {
                "id": single.id,
                "name": single.label,
                "x": single.scenePos().x(),
                "y": single.scenePos().y(),
                "width": single.rect().width(),
                "height": single.rect().height()
            }
            data["singleBoxes"].append(single_data)
        fileName, _ = QFileDialog.getSaveFileName(
            self, "Datei speichern", "", "JSON Dateien (*.json)"
        )
        if fileName:
            with open(fileName, "w") as f:
                json.dump(data, f, indent=4)
            print("Daten gespeichert.")

    def load_state(self):
        fileName, _ = QFileDialog.getOpenFileName(
            self, "Datei laden", "", "JSON Dateien (*.json)"
        )
        if fileName:
            with open(fileName, "r") as f:
                data = json.load(f)
            pdf_path = data.get("pdf_path", "")
            if pdf_path:
                self.pdfPath = pdf_path
                status = self.pdfDocument.load(pdf_path)
                if status != QPdfDocument.Error.None_:
                    print("Fehler beim Laden der PDF.")
                    return
            for pair in self.boxPairs:
                pair.remove_from_scene()
            self.boxPairs.clear()
            for single in self.singleBoxes:
                single.remove_from_scene()
            self.singleBoxes.clear()
            self.listBoxPairs.clear()
            max_pair_id = 0
            for pair_data in data.get("boxPairs", []):
                newPair = BoxPair(self.scene, QPointF(0, 0))
                newPair.id = pair_data["id"]
                usr = pair_data["USR"]
                nr = pair_data["NR"]
                newPair.box1.label = usr["name"]
                newPair.box1.setPos(QPointF(usr["x"], usr["y"]))
                newPair.box1.setRect(QRectF(0, 0, usr["width"], usr["height"]))
                newPair.box1.updatePosText()
                newPair.box2.label = nr["name"]
                newPair.box2.setPos(QPointF(nr["x"], nr["y"]))
                newPair.box2.setRect(QRectF(0, 0, nr["width"], nr["height"]))
                newPair.box2.updatePosText()
                self.boxPairs.append(newPair)
                listItem = QListWidgetItem(str(newPair))
                listItem.setData(Qt.UserRole, newPair)
                self.listBoxPairs.addItem(listItem)
                max_pair_id = max(max_pair_id, newPair.id)
            BoxPair._next_id = max_pair_id + 1
            BoxPair._free_ids = []
            max_single_id = 0
            for single_data in data.get("singleBoxes", []):
                rect = QRectF(0, 0, single_data["width"], single_data["height"])
                newSingle = SingleBox(rect)
                newSingle.id = single_data["id"]
                newSingle.label = single_data["name"]
                newSingle.setPos(QPointF(single_data["x"], single_data["y"]))
                newSingle.setRect(QRectF(0, 0, single_data["width"], single_data["height"]))
                newSingle.updatePosText()
                self.singleBoxes.append(newSingle)
                listItem = QListWidgetItem(f"BoxSingle {newSingle.id}")
                listItem.setData(Qt.UserRole, newSingle)
                self.listBoxPairs.addItem(listItem)
                max_single_id = max(max_single_id, newSingle.id)
            SingleBox._next_id = max_single_id + 1
            SingleBox._free_ids = []
            self.load_page(0)
            print("Daten geladen.")

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Delete:
            self.remove_selected_item()
        else:
            super().keyPressEvent(event)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = PdfDisplay()
    window.show()
    sys.exit(app.exec())
