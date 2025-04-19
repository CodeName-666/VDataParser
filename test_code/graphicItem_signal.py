import sys
import os
import json
from PySide6.QtWidgets import (
    QApplication, QWidget, QGraphicsScene, QGraphicsPixmapItem,
    QFileDialog, QListWidgetItem, QMessageBox, QGraphicsView, # <--- Added here
    QGraphicsItem, QGraphicsTextItem, QGraphicsRectItem # Other items might be here
)
from PySide6.QtGui import QPixmap, QPainter, QPen, QBrush, QColor
from PySide6.QtCore import Qt, QRectF, QPointF, Signal, Slot, QSize, QObject
from PySide6.QtPdf import QPdfDocument


# --- Graphics Items ---
class DraggableBox(QGraphicsRectItem, QObject):
    """ A draggable and resizable rectangle item for the graphics scene. """
    geometryChangedByUser: Signal = Signal()
   
    def __init__(self, rect: QRectF, label="", parent=None):
        QGraphicsRectItem.__init__(self, rect, parent)
        QObject.__init__(self)
        
        self.setFlags(
            QGraphicsItem.ItemIsMovable |
            QGraphicsItem.ItemIsSelectable |
            QGraphicsItem.ItemSendsGeometryChanges | # Needed for itemChange
            QGraphicsItem.ItemIsFocusable
        )
         # Signal emitted when the geometry (pos or size) is chan



if __name__ == '__main__':
    rect = QRectF(0, 0, 100, 100)
    box = DraggableBox(rect, "test")

    box.geometryChangedByUser.emit()

