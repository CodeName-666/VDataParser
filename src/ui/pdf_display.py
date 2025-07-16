
import json
from PySide6.QtWidgets import (
    QApplication, QWidget, QGraphicsScene, QGraphicsPixmapItem,
    QFileDialog, QListWidgetItem, QMessageBox, QGraphicsView, # <--- Added here
    QGraphicsItem, QGraphicsTextItem, QGraphicsRectItem # Other items might be here
)
from PySide6.QtGui import QPixmap, QPainter, QPen, QBrush, QColor
from PySide6.QtCore import Qt, QRectF, QPointF, Signal, Slot, QSize, QObject
from PySide6.QtPdf import QPdfDocument
from pathlib import Path

from .generated import PdfDisplayUi
from .persistent_base_ui import PersistentBaseUi
from data import PdfDisplayConfig

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
BOX_PAIR_LABEL_PREFIX = "USER/NR"
LIST_ITEM_DATA_ROLE = Qt.UserRole


# --- ID Management (Helper Class) ---
class ItemIdManager(QObject):
    """Manages unique IDs for items, allowing reuse."""
    def __init__(self):
        super().__init__()
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
         # Signal emitted when the geometry (pos or size) is changed by user interaction

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
        left   = abs(pos.x() - rect.left()) < margin
        right  = abs(pos.x() - rect.right()) < margin
        top    = abs(pos.y() - rect.top()) < margin
        bottom = abs(pos.y() - rect.bottom()) < margin

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
            newRect = QRectF(self._initialRect)
            newPos = QPointF(self._initialScenePos)

            # Calculate potential new dimensions and positions based on edge(s) dragged
            # Adjust left edge
            if self._resizeEdges['left']:
                dx = delta.x()
                newWidth = newRect.width() - dx
                if newWidth < MIN_BOX_WIDTH:
                    dx = newRect.width() - MIN_BOX_WIDTH # Limit delta
                    newWidth = MIN_BOX_WIDTH
                newPos.setX(self._initialScenePos.x() + dx) # Move origin right
                newRect.setWidth(newWidth)
                newRect.setLeft(0) # Keep local origin at 0

            # Adjust right edge
            if self._resizeEdges['right']:
                dx = delta.x()
                newWidth = self._initialRect.width() + dx
                if newWidth < MIN_BOX_WIDTH:
                    newWidth = MIN_BOX_WIDTH
                newRect.setWidth(newWidth)

            # Adjust top edge
            if self._resizeEdges['top']:
                dy = delta.y()
                newHeight = newRect.height() - dy
                if newHeight < MIN_BOX_HEIGHT:
                    dy = newRect.height() - MIN_BOX_HEIGHT # Limit delta
                    newHeight = MIN_BOX_HEIGHT
                newPos.setY(self._initialScenePos.y() + dy) # Move origin down
                newRect.setHeight(newHeight)
                newRect.setTop(0) # Keep local origin at 0

            # Adjust bottom edge
            if self._resizeEdges['bottom']:
                dy = delta.y()
                newHeight = self._initialRect.height() + dy
                if newHeight < MIN_BOX_HEIGHT:
                    newHeight = MIN_BOX_HEIGHT
                newRect.setHeight(newHeight)

            # Apply the changes
            # Prepare geometry change must be called before changing the geometry
            # if ItemSendsGeometryChanges flag is set.
            self.prepareGeometryChange()
            self.setPos(newPos)
            self.setRect(newRect) # Rect is always (0,0, w, h)
            # self.updatePosText() # updatePosText called by itemChange signal

            self.geometryChangedByUser.emit() # Notify listeners
            event.accept()
        else:
            # Standard move handling
            super().mouseMoveEvent(event)
            # No need to emit geometryChangedByUser here, itemChange handles position

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            if self._resizing:
                self._resizing = False
                # Update cursor based on current position after resize
                self._updateCursorShape(event.pos())
                event.accept()
            else:
                # Reset cursor after move
                self.setCursor(Qt.OpenHandCursor if self.isUnderMouse() else Qt.ArrowCursor)
                super().mouseReleaseEvent(event)
        else:
             super().mouseReleaseEvent(event)

    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemPositionHasChanged and self.scene():
            self.updatePosText()
            if not self._resizing:
                self.geometryChangedByUser.emit()
        # Den folgenden Block entfernen oder auskommentieren,
        # da ItemRectHasChanged in PySide6 nicht verfügbar ist:
        # elif change == QGraphicsItem.ItemRectHasChanged and self.scene():
        #     self.updatePosText()
        
        return super().itemChange(change, value)



class BoxPair(QObject):
    """ Represents a pair of linked DraggableBox items. """
    manager = ItemIdManager() # Class-level ID manager

    def __init__(self, scene: QGraphicsScene, startPos=QPointF(50, 50)):
        super().__init__()
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
        self.label = f"{BOX_PAIR_LABEL_PREFIX}{self.id}"
        scene.addItem(self.box1)
        scene.addItem(self.box2)

    def remove_from_scene(self):
        """Removes both boxes from the scene and releases the ID."""
        if self.scene:
            self.scene.removeItem(self.box1)
            self.scene.removeItem(self.box2)
        BoxPair.manager.release_id(self.id)

    def get_boxes(self):
        """Returns the two DraggableBox items."""
        return self.box1, self.box2

    def __str__(self):
        return f"BoxPair {self.id} ({self.label})" # More descriptive


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
class PdfDisplay(PersistentBaseUi):

    # Define a signal for the exit button if needed externally
    exit_requested = Signal()

    def __init__(self, parent=None, *, state: PdfDisplayConfig | None = None, json_path: str | None = None):
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
        self._config: PdfDisplayConfig = None
        # --- UI Element Access (using self.ui) ---
        # No need to redefine self.graphicsView etc. if BaseUi is QWidget/QMainWindow
        # Access them directly via self.ui.graphicsView, self.ui.btnLoadPDF, etc.

        # --- Scene Setup ---
        self.scene = QGraphicsScene(self)
        self.ui.graphicsView.setScene(self.scene)
        self.ui.graphicsView.setRenderHints(QPainter.Antialiasing | QPainter.SmoothPixmapTransform)
        self.ui.graphicsView.setDragMode(QGraphicsView.ScrollHandDrag) # Allow panning

        # --- Connect Signals ---
        self.setup_connections()

        # Zustand sofort herstellen, falls übergeben
        if state is not None:
            self.import_state(state)
        elif json_path:
            self.import_state(PdfDisplayConfig(json_path))
            
    def setup_connections(self):
        """Connects UI signals to slots."""
        self.ui.btnLoadPDF.clicked.connect(self.load_pdf)
        self.ui.btnAddBoxPair.clicked.connect(self.add_box_pair)
        self.ui.btnAddSingleBox.clicked.connect(self.add_single_box)
        self.ui.btnRemoveBoxPair.clicked.connect(self.remove_selected_list_item) # Renamed for clarity
        self.ui.btnZoomIn.clicked.connect(self.zoom_in)
        self.ui.btnZoomOut.clicked.connect(self.zoom_out)
        self.ui.btnSaveAsConfig.clicked.connect(self.save_as_state)
        self.ui.btnSaveConfig.clicked.connect(self.save_state)
        self.ui.btnLoadConfig.clicked.connect(self.load_state)
        self.ui.btnSaveOutputPath.clicked.connect(self.save_output_path)
        
        self.scene.selectionChanged.connect(self.on_scene_selection_changed)
        self.ui.listBoxPairs.itemSelectionChanged.connect(self.on_list_selection_changed)

        self.ui.lineEditX.editingFinished.connect(self.on_box_properties_changed) # Renamed
        self.ui.lineEditY.editingFinished.connect(self.on_box_properties_changed) # Renamed
        self.ui.lineEditWidth.editingFinished.connect(self.on_box_properties_changed) # Renamed
        self.ui.lineEditHeight.editingFinished.connect(self.on_box_properties_changed) # Renamed       

    # --- PDF Handling ---
    @Slot()
    def load_pdf(self):
        """Opens a file dialog to load a PDF document."""
        fileName, _ = QFileDialog.getOpenFileName(self, "PDF Datei öffnen", "", "PDF Dateien (*.pdf)")
        if fileName:
            status = self.pdfDocument.load(fileName)
            if status == QPdfDocument.Error.None_:
                self.pdfPath = fileName
                self.setWindowTitle(f"PDF Editor - {Path(fileName).name}") # Update title
                self.load_page(0) # Load the first page
                
                self._config_changed()

                # Optionally clear existing boxes when loading a *new* PDF
                # self._clear_all_boxes()
            else:
                QMessageBox.critical(self, "Fehler", f"Fehler beim Laden der PDF:\n{self.pdfDocument.errorString()}")
                self.pdfPath = ""
                self.setWindowTitle("PDF Editor")

    def load_page(self, page_index: int):
        """Renders and displays a specific PDF page."""
        if not self.pdfDocument or page_index >= self.pdfDocument.pageCount():
            print(f"Invalid page index: {page_index}")
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
        # Use the PDF item's bounding rect for the scene rect
        self.scene.setSceneRect(self.pdf_item.boundingRect())

        # Ensure existing boxes are visible (add them back if removed, or just ensure they are top)
        for item in self.scene.items():
             if isinstance(item, DraggableBox):
                  item.setZValue(0) # Bring boxes to front


    # --- Box Handling ---
    def _add_list_item(self, text: str, data_object):
        """Helper to add an item to the list widget."""
        listItem = QListWidgetItem(text)
        listItem.setData(LIST_ITEM_DATA_ROLE, data_object)
        self.ui.listBoxPairs.addItem(listItem)
        return listItem

    def _connect_box_signals(self, box: DraggableBox):
        """Connect signals from a DraggableBox to update UI."""
        # Connect the box's signal to the update slot
        box.geometryChangedByUser.connect(self.on_box_geometry_changed_by_user) # Renamed
        # Disconnect when the box is destroyed (important!)
        # box.destroyed.connect(lambda: self.on_box_destroyed(box)) # Requires QObject inheritance or tracking

    # Slot to handle geometry changes from any connected box
    @Slot()
    def on_box_geometry_changed_by_user(self):
        sender_box = self.sender() # Get the box that emitted the signal
        if sender_box and sender_box == self.currentBox:
            self.update_box_properties_from_item(sender_box)

        self._config_changed()


    @Slot()
    def add_box_pair(self):
        """Adds a new pair of linked boxes to the scene and list."""
        if not self.pdf_item:
            QMessageBox.warning(self, "Aktion nicht möglich", "Bitte laden Sie zuerst eine PDF-Datei.")
            return
        # Calculate a reasonable start position (e.g., center of the current view)
        view_rect = self.ui.graphicsView.mapToScene(self.ui.graphicsView.viewport().rect()).boundingRect()
        startPos = view_rect.center() - QPointF(DEFAULT_BOX_WIDTH / 2, DEFAULT_BOX_HEIGHT / 2) # Adjust for box size

        newPair = BoxPair(self.scene, startPos)
        self.boxPairs.append(newPair)
        list_item = self._add_list_item(str(newPair), newPair)
        self.ui.listBoxPairs.setCurrentItem(list_item) # Select the new item
        # Connect signals for the new boxes
        self._connect_box_signals(newPair.box1)
        self._connect_box_signals(newPair.box2)
        self._config_changed()

    @Slot()
    def add_single_box(self):
        """Adds a new single box to the scene and list."""
        if not self.pdf_item:
            self.status_info.emit("WARNING", "Bitte laden Sie zuerst eine PDF-Datei.")
            QMessageBox.warning(self, "Aktion nicht möglich", "Bitte laden Sie zuerst eine PDF-Datei.")
            return
        view_rect = self.ui.graphicsView.mapToScene(self.ui.graphicsView.viewport().rect()).boundingRect()
        startPos = view_rect.center() - QPointF(DEFAULT_BOX_WIDTH / 2, DEFAULT_BOX_HEIGHT / 2)

        rect = QRectF(0, 0, DEFAULT_BOX_WIDTH, DEFAULT_BOX_HEIGHT)
        newSingle = SingleBox(rect) # Parent is None initially
        newSingle.setPos(startPos)
        self.scene.addItem(newSingle) # Add to scene first
        self.singleBoxes.append(newSingle)
        list_item = self._add_list_item(str(newSingle), newSingle)
        self.ui.listBoxPairs.setCurrentItem(list_item)
        # Connect signal
        self._connect_box_signals(newSingle)
        self._config_changed()


    def _clear_all_boxes(self):
        """Removes all boxes from scene, lists, and list widget."""
        # Use a loop that doesn't modify the list while iterating
        items_to_remove = []
        for i in range(self.ui.listBoxPairs.count()):
            items_to_remove.append(self.ui.listBoxPairs.item(i))

        for item in items_to_remove:
            self._remove_box_object(item.data(LIST_ITEM_DATA_ROLE))

        self.ui.listBoxPairs.clear()
        self.boxPairs.clear()
        self.singleBoxes.clear()
        BoxPair.manager.reset()
        SingleBox.manager.reset()
        self.currentBox = None
        self.clear_box_properties_ui()
        self._config_changed()

    def _remove_box_object(self, obj):
        """Removes a BoxPair or SingleBox object completely."""
        if isinstance(obj, BoxPair):
            # Disconnect signals before removing
            obj.box1.geometryChangedByUser.disconnect(self.on_box_geometry_changed_by_user)
            obj.box2.geometryChangedByUser.disconnect(self.on_box_geometry_changed_by_user)
            obj.remove_from_scene()
            if obj in self.boxPairs: self.boxPairs.remove(obj)
        elif isinstance(obj, SingleBox):
            obj.geometryChangedByUser.disconnect(self.on_box_geometry_changed_by_user)
            obj.remove_from_scene()
            if obj in self.singleBoxes: self.singleBoxes.remove(obj)


    @Slot()
    def remove_selected_list_item(self):
        """Removes the selected item(s) from the list widget and scene."""
        selectedItems = self.ui.listBoxPairs.selectedItems()
        if not selectedItems:
             # If nothing selected in list, try scene selection
             selected_scene_items = self.scene.selectedItems()
             if selected_scene_items and isinstance(selected_scene_items[0], DraggableBox):
                  # Find corresponding list item
                  box_to_remove = selected_scene_items[0]
                  obj_to_remove = None
                  list_item_to_remove = None

                  # Check if it's a SingleBox
                  if isinstance(box_to_remove, SingleBox):
                       obj_to_remove = box_to_remove
                  else: # Check if it belongs to a BoxPair
                       for pair in self.boxPairs:
                            if box_to_remove in pair.get_boxes():
                                 obj_to_remove = pair
                                 break

                  if obj_to_remove:
                       for i in range(self.ui.listBoxPairs.count()):
                            item = self.ui.listBoxPairs.item(i)
                            if item.data(LIST_ITEM_DATA_ROLE) == obj_to_remove:
                                 list_item_to_remove = item
                                 break
                       if list_item_to_remove:
                           selectedItems = [list_item_to_remove] # Process this item

        # Proceed with removal if items are found either from list or scene
        if not selectedItems: return

        # Ask for confirmation
        reply = QMessageBox.question(self, "Löschen bestätigen",
                                     f"Möchten Sie die ausgewählten {len(selectedItems)} Elemente wirklich löschen?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            for item in selectedItems:
                obj = item.data(LIST_ITEM_DATA_ROLE)
                self._remove_box_object(obj)
                # Remove from list widget
                row = self.ui.listBoxPairs.row(item)
                self.ui.listBoxPairs.takeItem(row) # takeItem deletes the QListWidgetItem

            self.currentBox = None
            self.clear_box_properties_ui()
        
        self._config_changed()

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
    def save_as_state(self):
        """Saves the current state (PDF path, boxes) to a JSON file."""

        if not self.pdfPath:
            QMessageBox.warning(self, "Speichern nicht möglich", "Keine PDF geladen.")
            return

        super().save_as_state()
        QMessageBox.information(self, "Erfolg", f"Konfiguration erfolgreich gespeichert:\n{self._config.get_storage_full_path()}")

    @Slot()
    def save_output_path(self):
        """Open a file dialog to choose the PDF output path and store it."""
        if not self._config:
            return

        current = self.ui.lineEditOutputPath.text()
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "PDF speichern unter",
            current,
            "PDF Dateien (*.pdf)",
        )
        if not filename:
            return

        self.ui.lineEditOutputPath.setText(filename)
        self._config.set_full_output_path(filename)
        storage = self._config.get_storage_full_path()
        if storage:
            try:
                self._config.save(storage)
                self.status_info.emit("INFO", f"Output-Pfad gespeichert: {storage}")
                self._config_changed()
            except IOError as e:
                QMessageBox.critical(self, "Fehler", f"Speichern fehlgeschlagen:\n{e}")
   

    # --- UI Update Slots ---
    @Slot()
    def on_scene_selection_changed(self):
        """Updates property fields when scene selection changes."""
        selected = self.scene.selectedItems()
        new_selection = None
        if selected:
            item = selected[0]
            if isinstance(item, DraggableBox):
                new_selection = item

        if self.currentBox != new_selection:
             # Selection changed
            self.currentBox = new_selection
            if self.currentBox:
                 self.update_box_properties_from_item(self.currentBox)
                 # Also select corresponding item in list widget
                 list_item = self.find_list_item_for_box(self.currentBox)
                 if list_item and not list_item.isSelected():
                      self.ui.listBoxPairs.setCurrentItem(list_item, QItemSelectionModel.ClearAndSelect)
            else:
                 self.clear_box_properties_ui()
                 # Optionally clear list selection if scene deselected
                 # self.ui.listBoxPairs.clearSelection()

    @Slot()
    def on_list_selection_changed(self):
        """Updates scene selection and property fields when list selection changes."""
        selectedItems = self.ui.listBoxPairs.selectedItems()
        box_to_select = None
        if selectedItems:
            item = selectedItems[0]
            obj = item.data(LIST_ITEM_DATA_ROLE)
            if isinstance(obj, BoxPair):
                # Select the first box of the pair in the scene
                box_to_select = obj.box1
            elif isinstance(obj, SingleBox):
                box_to_select = obj

        # Block scene signals temporarily to avoid loops
        self.scene.selectionChanged.disconnect(self.on_scene_selection_changed)
        self.scene.clearSelection()
        if box_to_select:
             box_to_select.setSelected(True)
             self.currentBox = box_to_select
             self.update_box_properties_from_item(self.currentBox)
             self.ui.graphicsView.ensureVisible(box_to_select) # Scroll to selected box
        else:
             self.currentBox = None
             self.clear_box_properties_ui()
        # Reconnect scene signals
        self.scene.selectionChanged.connect(self.on_scene_selection_changed)


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
        self._block_property_updates = True # Prevent potential signals
        self.ui.lineEditX.setText("")
        self.ui.lineEditY.setText("")
        self.ui.lineEditWidth.setText("")
        self.ui.lineEditHeight.setText("")
        self._block_property_updates = False


    @Slot()
    def on_box_properties_changed(self):
        """Updates the selected box geometry based on LineEdit values."""
        if self.currentBox and not self._block_property_updates:
            try:
                x = float(self.ui.lineEditX.text())
                y = float(self.ui.lineEditY.text())
                w = float(self.ui.lineEditWidth.text())
                h = float(self.ui.lineEditHeight.text())

                if w < MIN_BOX_WIDTH or h < MIN_BOX_HEIGHT:
                     raise ValueError(f"Width/Height must be >= {MIN_BOX_WIDTH}/{MIN_BOX_HEIGHT}")

            except ValueError as e:
                QMessageBox.warning(self, "Ungültige Eingabe", f"Bitte geben Sie gültige Zahlen ein.\nFehler: {e}")
                 # Restore previous values
                self.update_box_properties_from_item(self.currentBox)
                return

            # Prevent signals while programmatically changing box
            self.currentBox.blockSignals(True)
            self.currentBox.prepareGeometryChange() # Important before changing pos/rect
            self.currentBox.setPos(x, y)
            # Ensure rect is always relative to the item's origin (0,0)
            self.currentBox.setRect(0, 0, w, h)
            self.currentBox.blockSignals(False)

            # Manually update text as itemChange might not be sufficient now
            self.currentBox.updatePosText()


    # --- Event Handling ---
    def keyPressEvent(self, event):
        """Handles key presses, e.g., Delete key."""
        if event.key() == Qt.Key_Delete:
            # Check focus - delete from list if list has focus, otherwise from scene
            if self.ui.listBoxPairs.hasFocus():
                 self.remove_selected_list_item()
            else:
                 # Attempt removal based on scene selection first
                 selected_scene_items = self.scene.selectedItems()
                 if selected_scene_items:
                      self.remove_selected_list_item() # This func now handles scene sel.
                 else: # Fallback to list selection if nothing in scene selected
                      self.remove_selected_list_item()
            event.accept()
        else:
            # Allow base class or parent to handle other keys
            super().keyPressEvent(event)

    # ---------------------------------------------------------------------
    def export_state(self) -> PdfDisplayConfig:
        """Öffentliche, side-effect-freie Methode (z.B. für Tests)."""
        return self._state_to_dict()

    def import_state(self, config: PdfDisplayConfig):
        """Öffentliche Methode, die den GUI-Zustand setzt."""
        self._apply_state_dict(config)


    # --- State helpers ----------------------------------------------------
    def _state_to_dict(self) -> PdfDisplayConfig:
        """Sammelt den kompletten GUI-Zustand als PdfDisplayConfig mittels der Config-Methoden."""
        if not self.pdfPath:
            raise RuntimeError("Es ist noch keine PDF geladen")
        
        config = PdfDisplayConfig()
        # Setze Metadaten via die setter-Methoden der Config

        config.set_full_pdf_path(self.pdfPath)
        config.set_full_output_path(self.ui.lineEditOutputPath.text())
        

        # Box-Paare hinzufügen
        box_pairs = []
        for pair in self.boxPairs:
            box_pairs.append({
                "id": pair.id,
                "box1": self._box_to_dict(pair.box1),
                "box2": self._box_to_dict(pair.box2),
            })
        config.set_key_value(["boxPairs"], box_pairs)

        # Einzelboxen hinzufügen
        single_boxes = []
        for single in self.singleBoxes:
            d = self._box_to_dict(single)
            d["id"] = single.id
            single_boxes.append(d)
        config.set_key_value(["singleBoxes"], single_boxes)

        return config

    def _apply_state_dict(self, config: PdfDisplayConfig, clear_existing: bool = True):
        """Stellt den Zustand aus einem zuvor erzeugten PdfDisplayConfig wieder her,
        unter Nutzung der Methoden von PdfDisplayConfig."""
        
        self._config = config

        if not self._config.is_empty():

            if clear_existing:
                self._clear_all_boxes()

            # ---------- PDF ----------
            # Set the config for later use
            if self._config.get_full_pdf_path():
                self._load_pdf_from_path(self._config.get_full_pdf_path())

            self.ui.lineEditOutputPath.setText(self._config.get_full_output_path())

            # ---------- Box-Paare ----------
            max_pair_id = 0
            for p in self._config.get_box_pairs():
                pair = BoxPair(self.scene, QPointF(0, 0))
                pair.id = p.id
                # Wiederherstellung der beiden Boxes aus den Dataclass-Dictionaries
                self._restore_box(pair.box1, p.box1.to_dict())
                self._restore_box(pair.box2, p.box2.to_dict())
                self.boxPairs.append(pair)
                self._add_list_item(str(pair), pair)
                max_pair_id = max(max_pair_id, pair.id)

            # ---------- Einzelboxen ----------
            max_single_id = 0
            for s in self._config.get_single_boxes():
                rect = QRectF(0, 0, s.width, s.height)
                single = SingleBox(rect)
                single.id = s.id
                self._restore_box(single, s.to_dict())
                self.scene.addItem(single)
                self.singleBoxes.append(single)
                self._add_list_item(str(single), single)
                max_single_id = max(max_single_id, single.id)

            # Update der ID-Manager
            BoxPair.manager.reset(max_pair_id)
            SingleBox.manager.reset(max_single_id)

  

    def _restore_box(self, box: DraggableBox, d: dict):
        box.setLabel(d["label"])
        box.setPos(QPointF(d["x"], d["y"]))
        box.setRect(QRectF(0, 0, d["width"], d["height"]))
        self._connect_box_signals(box)

    def _load_pdf_from_path(self, path: str):
        pdf_path = Path(path)
        if not pdf_path.is_absolute():
            pdf_path = pdf_path.resolve()
        if self.pdfDocument.load(str(pdf_path)) == QPdfDocument.Error.None_:
            self.pdfPath = str(pdf_path)
            self.setWindowTitle(f"PDF Editor - {pdf_path.name}")
            self.load_page(0)
        else:
            raise IOError(self.pdfDocument.errorString())
        

    def _config_changed(self) -> bool:
        if self.pdfPath:
            ret = not self._config.data_equal(self.export_state())
            self.data_changed.emit(ret)
            return ret
        else:
            return False
    

