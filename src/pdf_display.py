# -*- coding: utf-8 -*-

import sys
import os
import json
from PySide6.QtWidgets import (
    QApplication, QWidget, QGraphicsScene, QGraphicsPixmapItem,
    QFileDialog, QListWidgetItem, QMessageBox, QGraphicsView, # Added QGraphicsView
    QGraphicsItem, QGraphicsTextItem, QGraphicsRectItem, QAbstractItemView, # Added QAbstractItemView for selection mode enum
    QItemSelectionModel # Added for list selection mode
)
from PySide6.QtGui import QPixmap, QPainter, QPen, QBrush, QColor, QCursor
from PySide6.QtCore import Qt, QRectF, QPointF, Signal, Slot, QSize # Added QSize

# Use QtPdf module
from PySide6.QtPdf import QPdfDocument

# Importiere die konvertierte UI-Klasse (Annahme: Name und Pfad sind korrekt)
# Falls PdfDisplayUi in derselben Datei wie PdfDisplay ist:
# from <current_module> import PdfDisplayUi
# Falls in einem Unterordner 'generated':
# Example assumes it's in a subfolder 'generated' relative to this file
try:
    from .generated import PdfDisplayUi
except ImportError:
    # Fallback if not run as part of a package, adjust as needed
    from generated import PdfDisplayUi

# Importiere die Basisklasse (Annahme: Pfad ist korrekt)
# Example assumes it's in a subfolder 'base' relative to this file
try:
    from .base_ui import BaseUi
except ImportError:
     # Fallback if not run as part of a package, assume BaseUi is just QWidget for now
     # Replace this with your actual BaseUi import if needed
     print("Warning: Could not import BaseUi, using QWidget as fallback.")
     BaseUi = QWidget


# --- Konstanten ---
BOX_BORDER_PEN = QPen(QColor("black"), 2)
BOX_BRUSH = QBrush(Qt.transparent)
RESIZE_MARGIN = 5
MIN_BOX_WIDTH = 20
MIN_BOX_HEIGHT = 20
BOX_PAIR_COLOR_1 = QColor("red")
BOX_PAIR_COLOR_2 = QColor("blue")
SINGLE_BOX_COLOR = QColor("green")
DEFAULT_BOX_WIDTH = 100
DEFAULT_BOX_HEIGHT = 50
BOX_PAIR_LABEL_1_PREFIX = "USR"
BOX_PAIR_LABEL_2_PREFIX = "NR"
SINGLE_BOX_LABEL_PREFIX = "DATE"
LIST_ITEM_DATA_ROLE = Qt.UserRole


# --- ID Management (Helper Class) ---
class ItemIdManager:
    """Manages unique IDs for items, allowing reuse."""
    def __init__(self):
        self._next_id = 1
        self._free_ids = set() # Use set for faster removal checks

    def get_new_id(self):
        if self._free_ids:
            new_id = min(self._free_ids)
            self._free_ids.remove(new_id)
        else:
            new_id = self._next_id
            self._next_id += 1
        return new_id

    def release_id(self, item_id):
        if item_id < self._next_id and item_id not in self._free_ids:
             self._free_ids.add(item_id)

    def reset(self, max_known_id=0):
        self._next_id = max_known_id + 1
        self._free_ids.clear()

    def get_highest_known_id(self):
        return self._next_id -1


# --- Graphics Items ---
class DraggableBox(QGraphicsRectItem):
    """ A draggable and resizable rectangle item for the graphics scene. """
    # Signal emitted when the geometry (pos or size) is changed by user interaction
    geometryChangedByUser = Signal()

    def __init__(self, rect: QRectF, label="", parent=None):
        super().__init__(rect, parent)
        self.setFlags(
            QGraphicsItem.ItemIsMovable |
            QGraphicsItem.ItemIsSelectable |
            QGraphicsItem.ItemSendsGeometryChanges | # Needed for itemChange
            QGraphicsItem.ItemIsFocusable
        )
        self.setAcceptHoverEvents(True)
        self.setPen(BOX_BORDER_PEN)
        self.setBrush(BOX_BRUSH)

        self.label = label
        self.posText = QGraphicsTextItem(self)
        self.updatePosText() # Initial text setup

        # Resizing state
        self._resizeMargins = RESIZE_MARGIN
        self._resizeEdges = {'left': False, 'right': False, 'top': False, 'bottom': False}
        self._resizing = False
        self._dragStartPos = None
        self._initialRect = self.rect()
        self._initialScenePos = self.pos()

    def setLabel(self, text: str):
        """Updates the box label and the displayed text."""
        self.label = text
        self.updatePosText()

    def updatePosText(self):
        """Updates the text item above the box."""
        if self.label:
            display_text = self.label
        else:
            pos = self.scenePos()
            display_text = f"X: {int(pos.x())} | Y: {int(pos.y())}"
        self.posText.setPlainText(display_text)
        # Adjust text position relative to box top-left
        self.posText.setPos(0, -self.posText.boundingRect().height() - 2) # Place above the box

    def _updateCursorShape(self, pos: QPointF):
        """Sets the cursor shape based on the hover position."""
        rect = self.rect()
        margin = self._resizeMargins
        # Check proximity to edges based on item's local coordinates (0,0 is top-left)
        left   = abs(pos.x() - 0) < margin
        right  = abs(pos.x() - rect.width()) < margin
        top    = abs(pos.y() - 0) < margin
        bottom = abs(pos.y() - rect.height()) < margin

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
            self.setCursor(Qt.OpenHandCursor) # Default move cursor

    def hoverEnterEvent(self, event):
        self._updateCursorShape(event.pos())
        super().hoverEnterEvent(event)

    def hoverMoveEvent(self, event):
        if not self._resizing: # Don't change cursor while resizing
            self._updateCursorShape(event.pos())
        super().hoverMoveEvent(event)

    def hoverLeaveEvent(self, event):
        self.setCursor(Qt.ArrowCursor) # Reset cursor when leaving
        super().hoverLeaveEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            if any(self._resizeEdges.values()):
                self._resizing = True
                self._dragStartPos = event.pos() # Position within item coordinates
                self._initialRect = QRectF(self.rect()) # Copy current rect
                self._initialScenePos = QPointF(self.scenePos()) # Copy current scene pos
                self.setCursor(self.cursor()) # Keep resize cursor during drag
                event.accept()
            else:
                # Start standard move drag
                self.setCursor(Qt.ClosedHandCursor)
                super().mousePressEvent(event) # Allow base class to handle move start
        else:
             super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._resizing:
            # Calculate change in item coordinates
            delta = event.pos() - self._dragStartPos

            # Start with the initial state
            newRect = QRectF(self._initialRect) # Represents the local (0,0,w,h) rect
            newPos = QPointF(self._initialScenePos) # Represents the top-left position in the scene

            # Calculate potential new dimensions and positions based on edge(s) dragged
            # Adjust left edge
            if self._resizeEdges['left']:
                dx = delta.x()
                newWidth = self._initialRect.width() - dx
                if newWidth < MIN_BOX_WIDTH:
                    # Calculate the maximum allowed delta based on min width
                    dx = self._initialRect.width() - MIN_BOX_WIDTH
                    newWidth = MIN_BOX_WIDTH
                # Scene position moves right by dx
                newPos.setX(self._initialScenePos.x() + dx)
                # Local rect width changes
                newRect.setWidth(newWidth)
                # Local rect left remains 0

            # Adjust right edge
            if self._resizeEdges['right']:
                dx = delta.x()
                newWidth = self._initialRect.width() + dx
                if newWidth < MIN_BOX_WIDTH:
                    newWidth = MIN_BOX_WIDTH
                newRect.setWidth(newWidth)
                # Scene position x does not change when resizing right

            # Adjust top edge
            if self._resizeEdges['top']:
                dy = delta.y()
                newHeight = self._initialRect.height() - dy
                if newHeight < MIN_BOX_HEIGHT:
                    # Calculate the maximum allowed delta based on min height
                    dy = self._initialRect.height() - MIN_BOX_HEIGHT
                    newHeight = MIN_BOX_HEIGHT
                # Scene position moves down by dy
                newPos.setY(self._initialScenePos.y() + dy)
                # Local rect height changes
                newRect.setHeight(newHeight)
                # Local rect top remains 0

            # Adjust bottom edge
            if self._resizeEdges['bottom']:
                dy = delta.y()
                newHeight = self._initialRect.height() + dy
                if newHeight < MIN_BOX_HEIGHT:
                    newHeight = MIN_BOX_HEIGHT
                newRect.setHeight(newHeight)
                # Scene position y does not change when resizing bottom

            # Apply the changes
            # Prepare geometry change must be called before changing the geometry
            # if ItemSendsGeometryChanges flag is set.
            self.prepareGeometryChange()
            # Update scene position first
            self.setPos(newPos)
            # Update local rectangle (always 0,0 origin)
            self.setRect(QRectF(0, 0, newRect.width(), newRect.height()))
            # updatePosText() will be called by itemChange signal after setPos

            self.geometryChangedByUser.emit() # Notify listeners about the change
            event.accept()
        else:
            # Standard move handling
            super().mouseMoveEvent(event)
            # No need to emit geometryChangedByUser here, itemChange handles position changes

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            if self._resizing:
                self._resizing = False
                # Update cursor based on current position after resize
                self._updateCursorShape(event.pos())
                # Final geometry change signal handled by mouseMoveEvent
                event.accept()
            else:
                # Reset cursor after move
                self.setCursor(Qt.OpenHandCursor if self.isUnderMouse() else Qt.ArrowCursor)
                super().mouseReleaseEvent(event)
        else:
             super().mouseReleaseEvent(event)

    def itemChange(self, change, value):
        """Called by Qt when specific item properties change."""
        # Called after setPos()
        if change == QGraphicsItem.ItemPositionHasChanged and self.scene():
            self.updatePosText()
            # Emit signal only if move was likely user-initiated (not during resize start)
            if not self._resizing: # Check if we are NOT currently in a resize operation drag
                 self.geometryChangedByUser.emit()
        # Called after setRect() - though less common to track this directly
        # We rely on emitting the signal in mouseMoveEvent for resize changes
        # elif change == QGraphicsItem.ItemGeometryHasChanged and self.scene():
        #      self.updatePosText()


        return super().itemChange(change, value)


class BoxPair:
    """ Represents a pair of linked DraggableBox items. """
    manager = ItemIdManager() # Class-level ID manager

    def __init__(self, scene: QGraphicsScene, startPos=QPointF(50, 50)):
        self.id = BoxPair.manager.get_new_id()
        self.scene = scene

        rect = QRectF(0, 0, DEFAULT_BOX_WIDTH, DEFAULT_BOX_HEIGHT)

        self.box1 = DraggableBox(rect, label=f"{BOX_PAIR_LABEL_1_PREFIX}{self.id}")
        self.box1.setPos(startPos)
        self.box1.setPen(QPen(BOX_PAIR_COLOR_1, 2))

        offset = QPointF(DEFAULT_BOX_WIDTH + 20, 0) # Place second box right of the first
        self.box2 = DraggableBox(rect, label=f"{BOX_PAIR_LABEL_2_PREFIX}{self.id}")
        self.box2.setPos(startPos + offset)
        self.box2.setPen(QPen(BOX_PAIR_COLOR_2, 2))

        scene.addItem(self.box1)
        scene.addItem(self.box2)

    def remove_from_scene(self):
        """Removes both boxes from the scene and releases the ID."""
        if self.scene:
            # Check if items are still in scene before removing
            if self.box1.scene() == self.scene:
                 self.scene.removeItem(self.box1)
            if self.box2.scene() == self.scene:
                 self.scene.removeItem(self.box2)
        BoxPair.manager.release_id(self.id)

    def get_boxes(self):
        """Returns the two DraggableBox items."""
        return self.box1, self.box2

    def __str__(self):
        return f"BoxPair {self.id}"


class SingleBox(DraggableBox):
    """ Represents a single DraggableBox with its own ID management. """
    manager = ItemIdManager() # Class-level ID manager

    def __init__(self, rect: QRectF, parent=None):
        self.id = SingleBox.manager.get_new_id()
        label = f"{SINGLE_BOX_LABEL_PREFIX}{self.id}"
        super().__init__(rect, label, parent)
        self.setPen(QPen(SINGLE_BOX_COLOR, 2))

    def remove_from_scene(self):
        """Removes the box from the scene and releases the ID."""
        if self.scene():
            self.scene().removeItem(self)
        SingleBox.manager.release_id(self.id)

    def __str__(self):
         return f"SingleBox {self.id} ({self.label})" # More descriptive


# --- Main Application Widget ---
class PdfDisplay(BaseUi): # Inherit from your base UI class (QWidget or QMainWindow)

    # Define a signal for the exit button if needed externally
    exit_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = PdfDisplayUi()
        self.ui.setupUi(self)

        # --- Member Variables ---
        self.pdfDocument = QPdfDocument(self)
        self.boxPairs = []
        self.singleBoxes = []
        self.pdfPath = ""
        self.pdf_item = None # Keep track of the PDF background item
        self.currentBox = None # Currently selected DraggableBox
        self._block_property_updates = False # Flag to prevent signal loops
        self._block_selection_sync = False # Flag to prevent list/scene sync loops

        # --- UI Element Access (using self.ui) ---
        # Access elements via self.ui.graphicsView, self.ui.btnLoadPDF, etc.

        # --- Scene Setup ---
        self.scene = QGraphicsScene(self)
        self.ui.graphicsView.setScene(self.scene)
        self.ui.graphicsView.setRenderHints(QPainter.Antialiasing | QPainter.SmoothPixmapTransform)
        self.ui.graphicsView.setDragMode(QGraphicsView.ScrollHandDrag) # Allow panning

        # --- Connect Signals ---
        self.setup_connections()


    def setup_connections(self):
        """Connects UI signals to slots."""
        self.ui.btnLoadPDF.clicked.connect(self.load_pdf)
        self.ui.btnAddBoxPair.clicked.connect(self.add_box_pair)
        self.ui.btnAddSingleBox.clicked.connect(self.add_single_box)
        self.ui.btnRemoveBoxPair.clicked.connect(self.remove_selected_list_item)
        self.ui.btnZoomIn.clicked.connect(self.zoom_in)
        self.ui.btnZoomOut.clicked.connect(self.zoom_out)
        self.ui.btnSave.clicked.connect(self.save_state)
        self.ui.btnLoad.clicked.connect(self.load_state)
        self.ui.btnClosePDF.clicked.connect(self.exit_requested.emit)
        self.ui.btnClosePDF.clicked.connect(self.close)

        # List selection change
        self.ui.listBoxPairs.itemSelectionChanged.connect(self.handle_list_selection_change) # Renamed slot

        # Scene selection change
        self.scene.selectionChanged.connect(self.handle_scene_selection_change) # Renamed slot

        # Property LineEdit changes
        self.ui.lineEditX.editingFinished.connect(self.handle_box_properties_change) # Renamed slot
        self.ui.lineEditY.editingFinished.connect(self.handle_box_properties_change) # Renamed slot
        self.ui.lineEditWidth.editingFinished.connect(self.handle_box_properties_change) # Renamed slot
        self.ui.lineEditHeight.editingFinished.connect(self.handle_box_properties_change) # Renamed slot


    # --- PDF Handling ---
    @Slot()
    def load_pdf(self):
        """Opens a file dialog to load a PDF document."""
        fileName, _ = QFileDialog.getOpenFileName(self, "PDF Datei öffnen", "", "PDF Dateien (*.pdf)")
        if fileName:
            # Check if it's the same PDF
            if fileName == self.pdfPath:
                 print("PDF already loaded.")
                 return

            # Ask before clearing boxes if a PDF is already loaded with boxes
            if self.pdfPath and (self.boxPairs or self.singleBoxes):
                 reply = QMessageBox.question(self, "Neue PDF laden",
                                             "Möchten Sie die vorhandenen Boxen löschen, bevor Sie die neue PDF laden?",
                                             QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel, QMessageBox.No)
                 if reply == QMessageBox.Cancel:
                      return
                 elif reply == QMessageBox.Yes:
                      self._clear_all_boxes()
                 # If No, keep boxes

            status = self.pdfDocument.load(fileName)
            if status == QPdfDocument.Error.None_:
                self.pdfPath = fileName
                self.setWindowTitle(f"PDF Editor - {os.path.basename(fileName)}")
                self.load_page(0)
            else:
                QMessageBox.critical(self, "Fehler", f"Fehler beim Laden der PDF:\n{self.pdfDocument.errorString()}")
                self.pdfPath = ""
                self.setWindowTitle("PDF Editor")


    def load_page(self, page_index: int):
        """Renders and displays a specific PDF page."""
        if not self.pdfDocument or self.pdfDocument.isNull() or page_index >= self.pdfDocument.pageCount():
            print(f"Invalid page index or PDF document state: {page_index}")
            # Clear scene if PDF is invalid
            if self.pdf_item is not None and self.pdf_item in self.scene.items():
                self.scene.removeItem(self.pdf_item)
            self.pdf_item = None
            self.scene.setSceneRect(QRectF())
            return

        pageSizeF = self.pdfDocument.pagePointSize(page_index)
        if pageSizeF.isEmpty():
             print(f"Could not get page size for page {page_index}")
             return

        # Render at a reasonable resolution, e.g., 150 DPI
        dpi = 150
        renderSize = QSize(int(pageSizeF.width() * dpi / 72), int(pageSizeF.height() * dpi / 72))

        image = self.pdfDocument.render(page_index, renderSize)
        if image.isNull():
            QMessageBox.warning(self, "Fehler", f"Fehler beim Rendern der Seite {page_index}.")
            return

        pixmap = QPixmap.fromImage(image)

        # Remove the old PDF item if it exists
        if self.pdf_item is not None and self.pdf_item in self.scene.items():
            self.scene.removeItem(self.pdf_item)

        self.pdf_item = QGraphicsPixmapItem(pixmap)
        self.pdf_item.setFlag(QGraphicsItem.ItemIsSelectable, False)
        self.pdf_item.setZValue(-1) # Ensure PDF is behind boxes

        # Add new PDF item and set scene size
        self.scene.addItem(self.pdf_item)
        self.scene.setSceneRect(self.pdf_item.boundingRect())

        # Ensure existing boxes are visible and on top
        for item in self.scene.items():
             if isinstance(item, DraggableBox):
                  item.setZValue(0)


    # --- Box Handling ---
    def _add_list_item(self, text: str, data_object):
        """Helper to add an item to the list widget."""
        listItem = QListWidgetItem(text)
        listItem.setData(LIST_ITEM_DATA_ROLE, data_object)
        self.ui.listBoxPairs.addItem(listItem)
        return listItem

    def _connect_box_signals(self, box: DraggableBox):
        """Connect signals from a DraggableBox to update UI."""
        try:
             # Check if already connected before connecting
             box.geometryChangedByUser.disconnect(self.handle_box_geometry_change)
        except RuntimeError: # Thrown if not connected
             pass # Okay to proceed
        # Connect the box's signal to the update slot
        box.geometryChangedByUser.connect(self.handle_box_geometry_change) # Renamed slot

    def _disconnect_box_signals(self, box: DraggableBox):
         """Disconnect signals from a DraggableBox."""
         try:
              box.geometryChangedByUser.disconnect(self.handle_box_geometry_change)
         except RuntimeError:
              pass # Ignore if not connected

    # Slot to handle geometry changes from any connected box
    @Slot()
    def handle_box_geometry_change(self): # Renamed slot
        sender_box = self.sender()
        if sender_box and isinstance(sender_box, DraggableBox) and sender_box == self.currentBox:
            # Update properties only if the sender is the currently selected box
            self.update_box_properties_from_item(sender_box)


    @Slot()
    def add_box_pair(self):
        """Adds a new pair of linked boxes to the scene and list."""
        if not self.pdf_item:
            QMessageBox.warning(self, "Aktion nicht möglich", "Bitte laden Sie zuerst eine PDF-Datei.")
            return
        view_rect = self.ui.graphicsView.mapToScene(self.ui.graphicsView.viewport().rect()).boundingRect()
        startPos = view_rect.center() - QPointF(DEFAULT_BOX_WIDTH / 2, DEFAULT_BOX_HEIGHT / 2)

        newPair = BoxPair(self.scene, startPos)
        self.boxPairs.append(newPair)
        list_item = self._add_list_item(str(newPair), newPair)

        # Connect signals for the new boxes
        self._connect_box_signals(newPair.box1)
        self._connect_box_signals(newPair.box2)

        # Select the new item in the list and the first box in the scene
        self.ui.listBoxPairs.setCurrentItem(list_item) # This triggers handle_list_selection_change

    @Slot()
    def add_single_box(self):
        """Adds a new single box to the scene and list."""
        if not self.pdf_item:
            QMessageBox.warning(self, "Aktion nicht möglich", "Bitte laden Sie zuerst eine PDF-Datei.")
            return
        view_rect = self.ui.graphicsView.mapToScene(self.ui.graphicsView.viewport().rect()).boundingRect()
        startPos = view_rect.center() - QPointF(DEFAULT_BOX_WIDTH / 2, DEFAULT_BOX_HEIGHT / 2)

        rect = QRectF(0, 0, DEFAULT_BOX_WIDTH, DEFAULT_BOX_HEIGHT)
        newSingle = SingleBox(rect)
        newSingle.setPos(startPos)
        self.scene.addItem(newSingle)
        self.singleBoxes.append(newSingle)
        list_item = self._add_list_item(str(newSingle), newSingle)

        # Connect signal
        self._connect_box_signals(newSingle)

        # Select the new item
        self.ui.listBoxPairs.setCurrentItem(list_item) # Triggers handle_list_selection_change


    def _clear_all_boxes(self):
         """Removes all boxes from scene, lists, and list widget."""
         items_to_remove = [self.ui.listBoxPairs.item(i) for i in range(self.ui.listBoxPairs.count())]

         for item in items_to_remove:
              obj = item.data(LIST_ITEM_DATA_ROLE)
              self._remove_box_object(obj) # Handles scene removal, list removal, disconnects

         self.ui.listBoxPairs.clear()
         # Ensure internal lists are also clear
         self.boxPairs.clear()
         self.singleBoxes.clear()

         BoxPair.manager.reset()
         SingleBox.manager.reset()
         self.currentBox = None
         self.clear_box_properties_ui()


    def _remove_box_object(self, obj):
         """Removes a BoxPair or SingleBox object completely."""
         if isinstance(obj, BoxPair):
              self._disconnect_box_signals(obj.box1)
              self._disconnect_box_signals(obj.box2)
              obj.remove_from_scene() # Removes from scene, releases ID
              if obj in self.boxPairs: self.boxPairs.remove(obj)
         elif isinstance(obj, SingleBox):
              self._disconnect_box_signals(obj)
              obj.remove_from_scene() # Removes from scene, releases ID
              if obj in self.singleBoxes: self.singleBoxes.remove(obj)


    @Slot()
    def remove_selected_list_item(self):
        """Removes the selected item(s) from the list widget and scene."""
        items_to_process = []
        focused_widget = QApplication.focusWidget()

        if focused_widget == self.ui.listBoxPairs and self.ui.listBoxPairs.selectedItems():
            items_to_process = self.ui.listBoxPairs.selectedItems()
        elif self.scene.selectedItems():
             selected_scene_items = self.scene.selectedItems()
             if isinstance(selected_scene_items[0], DraggableBox):
                  box_to_remove = selected_scene_items[0]
                  list_item = self.find_list_item_for_box(box_to_remove)
                  if list_item:
                       items_to_process = [list_item]

        if not items_to_process:
             QMessageBox.information(self, "Löschen", "Bitte wählen Sie zuerst ein Element zum Löschen aus (in der Liste oder in der PDF-Ansicht).")
             return

        # Ask for confirmation
        item_text = items_to_process[0].text() if len(items_to_process) == 1 else f"{len(items_to_process)} Elemente"
        reply = QMessageBox.question(self, "Löschen bestätigen",
                                     f"Möchten Sie '{item_text}' wirklich löschen?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            # Important: Process list copy as removing items modifies the original list/selection
            for item in list(items_to_process):
                obj = item.data(LIST_ITEM_DATA_ROLE)
                self._remove_box_object(obj)
                # Remove from list widget (check if item still exists)
                row = self.ui.listBoxPairs.row(item)
                if row != -1: # Check if item still exists in the list
                     taken_item = self.ui.listBoxPairs.takeItem(row) # takeItem deletes the QListWidgetItem
                     del taken_item # Explicitly delete

            self.currentBox = None
            self.clear_box_properties_ui()
            self.scene.clearSelection() # Ensure scene selection is also cleared


    # --- View Control ---
    @Slot()
    def zoom_in(self):
        self.ui.graphicsView.scale(1.2, 1.2)

    @Slot()
    def zoom_out(self):
        self.ui.graphicsView.scale(1 / 1.2, 1 / 1.2)


    # --- State Persistence ---
    def _box_to_dict(self, box: DraggableBox):
         """Serializes a DraggableBox to a dictionary."""
         pos = box.scenePos()
         rect = box.rect()
         return {
             "label": box.label,
             "x": pos.x(),
             "y": pos.y(),
             "width": rect.width(),
             "height": rect.height()
         }

    @Slot()
    def save_state(self):
        """Saves the current state (PDF path, boxes) to a JSON file."""
        if not self.pdfPath:
            QMessageBox.warning(self, "Speichern nicht möglich", "Keine PDF geladen oder Konfiguration aktiv.")
            return

        data = {}
        try:
             # Try to make PDF path relative to current working directory if possible
             # This might be less useful if the JSON is moved elsewhere
             # Consider saving relative to JSON location upon loading instead.
             relative_path = os.path.relpath(self.pdfPath)
             data["pdf_path_relative_to_cwd"] = relative_path
        except ValueError:
             pass # Cannot make relative (e.g., different drives)
        data["pdf_path_absolute"] = self.pdfPath # Always save absolute path as fallback
        data["pdf_name"] = os.path.basename(self.pdfPath) # For reference

        data["boxPairs"] = []
        for pair in self.boxPairs:
            box1_data = self._box_to_dict(pair.box1)
            box2_data = self._box_to_dict(pair.box2)
            pair_data = {"id": pair.id, "box1": box1_data, "box2": box2_data}
            data["boxPairs"].append(pair_data)

        data["singleBoxes"] = []
        for single in self.singleBoxes:
            single_data = self._box_to_dict(single)
            single_data["id"] = single.id
            data["singleBoxes"].append(single_data)

        # Get save file name
        # Suggest a filename based on PDF name
        suggested_name = os.path.splitext(os.path.basename(self.pdfPath))[0] + "_config.json"
        fileName, _ = QFileDialog.getSaveFileName(self, "Konfiguration speichern", suggested_name, "JSON Dateien (*.json)")
        if fileName:
            # Ensure filename ends with .json
            if not fileName.lower().endswith(".json"):
                 fileName += ".json"
            try:
                with open(fileName, "w") as f:
                    json.dump(data, f, indent=4)
                print(f"Daten gespeichert: {fileName}")
                QMessageBox.information(self, "Erfolg", f"Konfiguration erfolgreich gespeichert:\n{fileName}")
            except IOError as e:
                QMessageBox.critical(self, "Fehler", f"Fehler beim Speichern der Datei:\n{e}")
            except TypeError as e:
                 QMessageBox.critical(self, "Fehler", f"Fehler beim Serialisieren der Daten (Typfehler):\n{e}")


    @Slot()
    def load_state(self):
        """Loads state from a JSON file."""
        fileName, _ = QFileDialog.getOpenFileName(self, "Konfiguration laden", "", "JSON Dateien (*.json)")
        if fileName:
            try:
                with open(fileName, "r") as f:
                    data = json.load(f)
            except FileNotFoundError:
                 QMessageBox.critical(self, "Fehler", f"Datei nicht gefunden:\n{fileName}")
                 return
            except json.JSONDecodeError as e:
                 QMessageBox.critical(self, "Fehler", f"Fehler beim Lesen der JSON-Datei (ungültiges Format):\n{e}")
                 return
            except Exception as e:
                QMessageBox.critical(self, "Fehler", f"Ein unerwarteter Fehler ist beim Lesen der Datei aufgetreten:\n{e}")
                return

            # --- Load PDF ---
            # Prefer absolute path, fallback to trying to resolve relative path
            pdf_path_saved = data.get("pdf_path_absolute")
            if not pdf_path_saved:
                 # Try legacy or relative path (less reliable)
                 pdf_path_saved = data.get("pdf_path") or data.get("pdf_path_relative_to_cwd")

            if not pdf_path_saved:
                 QMessageBox.warning(self, "Warnung", "Kein PDF-Pfad in der Konfigurationsdatei gefunden. Bitte PDF manuell laden.")
                 pdf_loaded_successfully = False
            else:
                 # Try to load PDF from saved path
                 pdf_path_to_load = pdf_path_saved
                 # Check if path needs resolving (relative to JSON or CWD)
                 if not os.path.isabs(pdf_path_to_load):
                      # Assume relative to JSON file's directory first
                      json_dir = os.path.dirname(fileName)
                      potential_path = os.path.normpath(os.path.join(json_dir, pdf_path_to_load))
                      if os.path.exists(potential_path):
                           pdf_path_to_load = potential_path
                      else:
                           # Fallback: try relative to current working directory
                           potential_path_cwd = os.path.normpath(os.path.join(os.getcwd(), pdf_path_to_load))
                           if os.path.exists(potential_path_cwd):
                                pdf_path_to_load = potential_path_cwd
                           else: # If still not absolute, it's likely wrong
                                pdf_path_to_load = pdf_path_saved # Keep original for error message


                 if not os.path.exists(pdf_path_to_load):
                     QMessageBox.warning(self, "Warnung", f"Die PDF-Datei konnte nicht gefunden werden:\n{pdf_path_to_load}\nBitte manuell laden.")
                     pdf_loaded_successfully = False
                 else:
                     status = self.pdfDocument.load(pdf_path_to_load)
                     if status != QPdfDocument.Error.None_:
                         QMessageBox.critical(self, "Fehler", f"Fehler beim Laden der PDF aus Konfiguration:\n{pdf_path_to_load}\n{self.pdfDocument.errorString()}")
                         pdf_loaded_successfully = False
                     else:
                         self.pdfPath = pdf_path_to_load
                         self.setWindowTitle(f"PDF Editor - {os.path.basename(self.pdfPath)}")
                         pdf_loaded_successfully = True

            # Clear scene if PDF failed or wasn't specified
            if not pdf_loaded_successfully:
                 if self.pdf_item: self.scene.removeItem(self.pdf_item)
                 self.pdf_item = None
                 self.scene.setSceneRect(QRectF())
                 self.pdfPath = ""
                 self.setWindowTitle("PDF Editor")

            # --- Clear existing boxes before loading new ones ---
            self._clear_all_boxes()

            # --- Load Boxes ---
            max_pair_id = 0
            try:
                for pair_data in data.get("boxPairs", []):
                    pair_id = pair_data.get("id", -1)
                    # Use 'box1'/'box2' keys consistent with save_state
                    box1_data = pair_data.get("box1")
                    box2_data = pair_data.get("box2")
                    if pair_id == -1 or not box1_data or not box2_data:
                         print(f"Skipping invalid box pair data: {pair_data}")
                         continue

                    newPair = BoxPair(self.scene, QPointF(0,0))
                    newPair.id = pair_id # Restore ID *after* initial creation
                    box1, box2 = newPair.get_boxes()

                    box1.setLabel(box1_data["label"])
                    box1.setPos(QPointF(box1_data["x"], box1_data["y"]))
                    box1.setRect(QRectF(0, 0, box1_data["width"], box1_data["height"]))

                    box2.setLabel(box2_data["label"])
                    box2.setPos(QPointF(box2_data["x"], box2_data["y"]))
                    box2.setRect(QRectF(0, 0, box2_data["width"], box2_data["height"]))

                    self.boxPairs.append(newPair)
                    self._add_list_item(str(newPair), newPair)
                    self._connect_box_signals(box1)
                    self._connect_box_signals(box2)
                    max_pair_id = max(max_pair_id, newPair.id)

                max_single_id = 0
                for single_data in data.get("singleBoxes", []):
                    single_id = single_data.get("id", -1)
                    if single_id == -1:
                         print(f"Skipping invalid single box data: {single_data}")
                         continue

                    rect = QRectF(0, 0, single_data["width"], single_data["height"])
                    newSingle = SingleBox(rect)
                    newSingle.id = single_id # Restore ID
                    newSingle.setLabel(single_data["label"])
                    newSingle.setPos(QPointF(single_data["x"], single_data["y"]))
                    # setRect already done in __init__ based on passed rect

                    self.scene.addItem(newSingle)
                    self.singleBoxes.append(newSingle)
                    self._add_list_item(str(newSingle), newSingle)
                    self._connect_box_signals(newSingle)
                    max_single_id = max(max_single_id, newSingle.id)

                # Reset ID managers based on loaded data
                BoxPair.manager.reset(max_pair_id)
                SingleBox.manager.reset(max_single_id)

                # Load the first page of the PDF if it was loaded successfully
                if pdf_loaded_successfully:
                    self.load_page(0)

                print("Daten geladen.")
                QMessageBox.information(self, "Erfolg", f"Konfiguration erfolgreich geladen:\n{fileName}")

            except KeyError as e:
                 QMessageBox.critical(self, "Fehler", f"Fehler beim Lesen der Box-Daten (fehlender Schlüssel '{e}' in JSON).")
                 self._clear_all_boxes() # Clear partially loaded state
            except Exception as e:
                 QMessageBox.critical(self, "Fehler", f"Fehler beim Verarbeiten der Box-Daten: {e}")
                 import traceback
                 traceback.print_exc() # Print detailed traceback for debugging
                 self._clear_all_boxes()


    # --- UI Update Slots ---
    @Slot()
    def handle_scene_selection_change(self): # Renamed slot
        """Updates property fields and list selection when scene selection changes."""
        if self._block_selection_sync: return # Prevent recursion

        selected = self.scene.selectedItems()
        new_selection = None
        if selected:
            item = selected[0]
            if isinstance(item, DraggableBox):
                new_selection = item

        if self.currentBox != new_selection:
             # Selection changed in scene
            self.currentBox = new_selection
            self._block_selection_sync = True # Block list update temporarily
            if self.currentBox:
                 self.update_box_properties_from_item(self.currentBox)
                 list_item = self.find_list_item_for_box(self.currentBox)
                 if list_item:
                      # Select only the corresponding list item
                      self.ui.listBoxPairs.clearSelection()
                      list_item.setSelected(True)
                      self.ui.listBoxPairs.scrollToItem(list_item, QAbstractItemView.PositionAtCenter)
                 else:
                     self.ui.listBoxPairs.clearSelection() # Deselect list if no match found
            else:
                 self.clear_box_properties_ui()
                 self.ui.listBoxPairs.clearSelection() # Deselect list if scene deselected
            self._block_selection_sync = False


    @Slot()
    def handle_list_selection_change(self): # Renamed slot
        """Updates scene selection and property fields when list selection changes."""
        if self._block_selection_sync: return # Prevent recursion

        selectedItems = self.ui.listBoxPairs.selectedItems()
        box_to_select = None
        if selectedItems:
            item = selectedItems[0]
            obj = item.data(LIST_ITEM_DATA_ROLE)
            if isinstance(obj, BoxPair):
                # Default to selecting the first box of the pair in the scene
                box_to_select = obj.box1
            elif isinstance(obj, SingleBox):
                box_to_select = obj

        self._block_selection_sync = True # Block scene update temporarily
        self.scene.clearSelection() # Clear previous scene selection
        if box_to_select:
             box_to_select.setSelected(True)
             self.currentBox = box_to_select
             self.update_box_properties_from_item(self.currentBox)
             self.ui.graphicsView.ensureVisible(box_to_select)
        else:
             self.currentBox = None
             self.clear_box_properties_ui()
        self._block_selection_sync = False


    def find_list_item_for_box(self, box: DraggableBox):
        """Finds the QListWidgetItem corresponding to a DraggableBox."""
        target_obj = None
        if isinstance(box, SingleBox):
            target_obj = box
        else: # Could be part of a BoxPair
            for pair in self.boxPairs:
                 if box in pair.get_boxes():
                      target_obj = pair
                      break
        if target_obj:
            for i in range(self.ui.listBoxPairs.count()):
                 item = self.ui.listBoxPairs.item(i)
                 if item.data(LIST_ITEM_DATA_ROLE) == target_obj:
                      return item
        return None


    def update_box_properties_from_item(self, item: DraggableBox):
        """Updates the LineEdits based on the selected item's geometry."""
        if not item or self._block_property_updates:
             return

        pos = item.scenePos()
        rect = item.rect()
        # Block signals from LineEdits while we set their text
        self.ui.lineEditX.blockSignals(True)
        self.ui.lineEditY.blockSignals(True)
        self.ui.lineEditWidth.blockSignals(True)
        self.ui.lineEditHeight.blockSignals(True)

        self.ui.lineEditX.setText(str(int(pos.x())))
        self.ui.lineEditY.setText(str(int(pos.y())))
        self.ui.lineEditWidth.setText(str(int(rect.width())))
        self.ui.lineEditHeight.setText(str(int(rect.height())))

        # Unblock signals
        self.ui.lineEditX.blockSignals(False)
        self.ui.lineEditY.blockSignals(False)
        self.ui.lineEditWidth.blockSignals(False)
        self.ui.lineEditHeight.blockSignals(False)


    def clear_box_properties_ui(self):
        """Clears the property LineEdits."""
        self._block_property_updates = True
        self.ui.lineEditX.setText("")
        self.ui.lineEditY.setText("")
        self.ui.lineEditWidth.setText("")
        self.ui.lineEditHeight.setText("")
        self._block_property_updates = False


    @Slot()
    def handle_box_properties_change(self): # Renamed slot
        """Updates the selected box geometry based on LineEdit values."""
        if self.currentBox and not self._block_property_updates:
            try:
                x = float(self.ui.lineEditX.text())
                y = float(self.ui.lineEditY.text())
                w = float(self.ui.lineEditWidth.text())
                h = float(self.ui.lineEditHeight.text())

                if w < MIN_BOX_WIDTH or h < MIN_BOX_HEIGHT:
                     # Restore valid values before showing message
                     orig_x = int(self.currentBox.scenePos().x())
                     orig_y = int(self.currentBox.scenePos().y())
                     orig_w = int(self.currentBox.rect().width())
                     orig_h = int(self.currentBox.rect().height())
                     self.ui.lineEditWidth.setText(str(orig_w))
                     self.ui.lineEditHeight.setText(str(orig_h))
                     Q