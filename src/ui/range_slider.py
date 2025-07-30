from PySide6.QtCore import Qt, Signal, QRectF, QEvent, QSize
from PySide6.QtGui import QPainter, QPen, QBrush, QColor
from PySide6.QtWidgets import QWidget
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QLabel
import sys

class RangeSlider(QWidget):
    # Signale
    lowerValueChanged = Signal(int)
    upperValueChanged = Signal(int)
    rangeChanged = Signal(int, int)

    # Optionen (Flags)
    NO_HANDLE = 0
    LEFT_HANDLE = 1
    RIGHT_HANDLE = 2
    DOUBLE_HANDLES = LEFT_HANDLE | RIGHT_HANDLE

    # Konstanten (Dimensionen)
    SC_HANDLE_SIDE_LENGTH = 11
    SC_SLIDER_BAR_HEIGHT = 5
    SC_LEFT_RIGHT_MARGIN = 1

    def __init__(self, orientation=Qt.Horizontal, options=DOUBLE_HANDLES, parent=None):
        super().__init__(parent)
        self.orientation = orientation
        self.options = options

        # Werte initialisieren
        self.mMinimum = 0
        self.mMaximum = 100
        self.mLowerValue = 0
        self.mUpperValue = 100
        self.mInterval = self.mMaximum - self.mMinimum
        self.mDelta = 0

        self.mFirstHandlePressed = False
        self.mSecondHandlePressed = False

        self.mBackgroudColorEnabled = QColor(0x1E, 0x90, 0xFF)
        self.mBackgroudColorDisabled = QColor(Qt.darkGray)
        self.mBackgroudColor = self.mBackgroudColorEnabled

        self.setMouseTracking(True)

    def minimumSizeHint(self) -> QSize:
        return QSize(self.SC_HANDLE_SIDE_LENGTH * 2 + self.SC_LEFT_RIGHT_MARGIN * 2,
                     self.SC_HANDLE_SIDE_LENGTH)

    def paintEvent(self, event):
        painter = QPainter(self)

        # Hintergrund zeichnen
        if self.orientation == Qt.Horizontal:
            backgroundRect = QRectF(
                self.SC_LEFT_RIGHT_MARGIN,
                (self.height() - self.SC_SLIDER_BAR_HEIGHT) / 2,
                self.width() - self.SC_LEFT_RIGHT_MARGIN * 2,
                self.SC_SLIDER_BAR_HEIGHT)
        else:
            backgroundRect = QRectF(
                (self.width() - self.SC_SLIDER_BAR_HEIGHT) / 2,
                self.SC_LEFT_RIGHT_MARGIN,
                self.SC_SLIDER_BAR_HEIGHT,
                self.height() - self.SC_LEFT_RIGHT_MARGIN * 2)

        pen = QPen(Qt.gray, 0.8)
        painter.setPen(pen)
        painter.setRenderHint(QPainter.Antialiasing, False)
        backgroundBrush = QBrush(QColor(0xD0, 0xD0, 0xD0))
        painter.setBrush(backgroundBrush)
        painter.drawRoundedRect(backgroundRect, 1, 1)

        # Ersten Handle zeichnen
        pen.setColor(Qt.darkGray)
        pen.setWidth(0.5)
        painter.setPen(pen)
        painter.setRenderHint(QPainter.Antialiasing, True)
        handleBrush = QBrush(QColor(0xFA, 0xFA, 0xFA))
        painter.setBrush(handleBrush)
        leftHandleRect = self.firstHandleRect()
        if self.options & self.LEFT_HANDLE:
            painter.drawRoundedRect(leftHandleRect, 2, 2)

        # Zweiten Handle zeichnen
        rightHandleRect = self.secondHandleRect()
        if self.options & self.RIGHT_HANDLE:
            painter.drawRoundedRect(rightHandleRect, 2, 2)

        # Auswahlbereich (zwischen den Handles) zeichnen
        painter.setRenderHint(QPainter.Antialiasing, False)
        selectedRect = QRectF(backgroundRect)
        if self.orientation == Qt.Horizontal:
            if self.options & self.LEFT_HANDLE:
                selectedRect.setLeft(leftHandleRect.right() + 0.5)
            else:
                selectedRect.setLeft(leftHandleRect.left() + 0.5)
            if self.options & self.RIGHT_HANDLE:
                selectedRect.setRight(rightHandleRect.left() - 0.5)
            else:
                selectedRect.setRight(rightHandleRect.right() - 0.5)
        else:
            if self.options & self.LEFT_HANDLE:
                selectedRect.setTop(leftHandleRect.bottom() + 0.5)
            else:
                selectedRect.setTop(leftHandleRect.top() + 0.5)
            if self.options & self.RIGHT_HANDLE:
                selectedRect.setBottom(rightHandleRect.top() - 0.5)
            else:
                selectedRect.setBottom(rightHandleRect.bottom() - 0.5)
        selectedBrush = QBrush(self.mBackgroudColor)
        painter.setBrush(selectedBrush)
        painter.drawRect(selectedRect)

    def firstHandleRect(self) -> QRectF:
        # Berechnung der Position des linken Handles basierend auf dem Prozentsatz
        percentage = (self.mLowerValue - self.mMinimum) / self.mInterval if self.mInterval != 0 else 0
        pos = percentage * self.validLength() + self.SC_LEFT_RIGHT_MARGIN
        return self.handleRect(pos)

    def secondHandleRect(self) -> QRectF:
        # Berechnung der Position des rechten Handles basierend auf dem Prozentsatz
        percentage = (self.mUpperValue - self.mMinimum) / self.mInterval if self.mInterval != 0 else 0
        offset = self.SC_HANDLE_SIDE_LENGTH if (self.options & self.LEFT_HANDLE) else 0
        pos = percentage * self.validLength() + self.SC_LEFT_RIGHT_MARGIN + offset
        return self.handleRect(pos)

    def handleRect(self, posValue: float) -> QRectF:
        # Zeichnungsrechteck für einen Handle
        if self.orientation == Qt.Horizontal:
            return QRectF(posValue,
                          (self.height() - self.SC_HANDLE_SIDE_LENGTH) / 2,
                          self.SC_HANDLE_SIDE_LENGTH,
                          self.SC_HANDLE_SIDE_LENGTH)
        else:
            return QRectF((self.width() - self.SC_HANDLE_SIDE_LENGTH) / 2,
                          posValue,
                          self.SC_HANDLE_SIDE_LENGTH,
                          self.SC_HANDLE_SIDE_LENGTH)

    def validLength(self) -> float:
        # Verfügbare Länge abzüglich Ränder und Handle-Größe
        length = self.width() if self.orientation == Qt.Horizontal else self.height()
        # Falls beide Handles vorhanden sind, müssen beide abgezogen werden
        handlesCount = 2 if (self.options & self.DOUBLE_HANDLES) == self.DOUBLE_HANDLES else 1
        return length - self.SC_LEFT_RIGHT_MARGIN * 2 - self.SC_HANDLE_SIDE_LENGTH * handlesCount

    def mousePressEvent(self, event):
        if event.buttons() & Qt.LeftButton:
            posCheck = event.pos().y() if self.orientation == Qt.Horizontal else event.pos().x()
            posMax = self.height() if self.orientation == Qt.Horizontal else self.width()
            posValue = event.pos().x() if self.orientation == Qt.Horizontal else event.pos().y()
            firstHandleRectPosValue = self.firstHandleRect().x() if self.orientation == Qt.Horizontal else self.firstHandleRect().y()
            secondHandleRectPosValue = self.secondHandleRect().x() if self.orientation == Qt.Horizontal else self.secondHandleRect().y()

            if self.secondHandleRect().contains(event.pos()):
                self.mSecondHandlePressed = True
            elif self.firstHandleRect().contains(event.pos()):
                self.mFirstHandlePressed = True

            if self.mFirstHandlePressed:
                self.mDelta = posValue - (firstHandleRectPosValue + self.SC_HANDLE_SIDE_LENGTH / 2)
            elif self.mSecondHandlePressed:
                self.mDelta = posValue - (secondHandleRectPosValue + self.SC_HANDLE_SIDE_LENGTH / 2)

            if 2 <= posCheck <= posMax - 2:
                step = self.mInterval // 10 if (self.mInterval // 10) >= 1 else 1
                if posValue < firstHandleRectPosValue:
                    self.setLowerValue(self.mLowerValue - step)
                elif (((posValue > firstHandleRectPosValue + self.SC_HANDLE_SIDE_LENGTH) or not (self.options & self.LEFT_HANDLE))
                      and ((posValue < secondHandleRectPosValue) or not (self.options & self.RIGHT_HANDLE))):
                    if self.options == self.DOUBLE_HANDLES:
                        if posValue - (firstHandleRectPosValue + self.SC_HANDLE_SIDE_LENGTH) < \
                           (secondHandleRectPosValue - (firstHandleRectPosValue + self.SC_HANDLE_SIDE_LENGTH)) / 2:
                            newLower = self.mLowerValue + step if self.mLowerValue + step < self.mUpperValue else self.mUpperValue
                            self.setLowerValue(newLower)
                        else:
                            newUpper = self.mUpperValue - step if self.mUpperValue - step > self.mLowerValue else self.mLowerValue
                            self.setUpperValue(newUpper)
                    elif self.options & self.LEFT_HANDLE:
                        newLower = self.mLowerValue + step if self.mLowerValue + step < self.mUpperValue else self.mUpperValue
                        self.setLowerValue(newLower)
                    elif self.options & self.RIGHT_HANDLE:
                        newUpper = self.mUpperValue - step if self.mUpperValue - step > self.mLowerValue else self.mLowerValue
                        self.setUpperValue(newUpper)
                elif posValue > secondHandleRectPosValue + self.SC_HANDLE_SIDE_LENGTH:
                    self.setUpperValue(self.mUpperValue + step)

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.LeftButton:
            posValue = event.pos().x() if self.orientation == Qt.Horizontal else event.pos().y()
            firstHandleRectPosValue = self.firstHandleRect().x() if self.orientation == Qt.Horizontal else self.firstHandleRect().y()
            secondHandleRectPosValue = self.secondHandleRect().x() if self.orientation == Qt.Horizontal else self.secondHandleRect().y()

            if self.mFirstHandlePressed and (self.options & self.LEFT_HANDLE):
                if posValue - self.mDelta + self.SC_HANDLE_SIDE_LENGTH / 2 <= secondHandleRectPosValue:
                    newVal = (posValue - self.mDelta - self.SC_LEFT_RIGHT_MARGIN - self.SC_HANDLE_SIDE_LENGTH / 2) / self.validLength() * self.mInterval + self.mMinimum
                    self.setLowerValue(int(newVal))
                else:
                    self.setLowerValue(self.mUpperValue)
            elif self.mSecondHandlePressed and (self.options & self.RIGHT_HANDLE):
                # Unterschiedliche Offsets für Doppelklick vs. Einzelfall
                left_offset = self.SC_HANDLE_SIDE_LENGTH * (1.5 if (self.options == self.DOUBLE_HANDLES) else 0.5)
                if firstHandleRectPosValue + left_offset <= posValue - self.mDelta:
                    newVal = (posValue - self.mDelta - self.SC_LEFT_RIGHT_MARGIN - self.SC_HANDLE_SIDE_LENGTH / 2 -
                              (self.SC_HANDLE_SIDE_LENGTH if (self.options == self.DOUBLE_HANDLES) else 0)) / self.validLength() * self.mInterval + self.mMinimum
                    self.setUpperValue(int(newVal))
                else:
                    self.setUpperValue(self.mLowerValue)

    def mouseReleaseEvent(self, event):
        self.mFirstHandlePressed = False
        self.mSecondHandlePressed = False

    def changeEvent(self, event):
        if event.type() == QEvent.EnabledChange:
            if self.isEnabled():
                self.mBackgroudColor = self.mBackgroudColorEnabled
            else:
                self.mBackgroudColor = self.mBackgroudColorDisabled
            self.update()
        super().changeEvent(event)

    # Getter und Setter
    def getMinimum(self) -> int:
        return self.mMinimum

    def setMinimum(self, value: int):
        if value <= self.mMaximum:
            self.mMinimum = value
        else:
            oldMax = self.mMaximum
            self.mMinimum = oldMax
            self.mMaximum = value
        self.mInterval = self.mMaximum - self.mMinimum
        self.update()
        self.setLowerValue(self.mMinimum)
        self.setUpperValue(self.mMaximum)
        self.rangeChanged.emit(self.mMinimum, self.mMaximum)

    def getMaximum(self) -> int:
        return self.mMaximum

    def setMaximum(self, value: int):
        if value >= self.mMinimum:
            self.mMaximum = value
        else:
            oldMin = self.mMinimum
            self.mMaximum = oldMin
            self.mMinimum = value
        self.mInterval = self.mMaximum - self.mMinimum
        self.update()
        self.setLowerValue(self.mMinimum)
        self.setUpperValue(self.mMaximum)
        self.rangeChanged.emit(self.mMinimum, self.mMaximum)

    def getLowerValue(self) -> int:
        return self.mLowerValue

    def setLowerValue(self, value: int):
        if value > self.mMaximum:
            value = self.mMaximum
        if value < self.mMinimum:
            value = self.mMinimum
        self.mLowerValue = value
        self.lowerValueChanged.emit(self.mLowerValue)
        self.update()

    def getUpperValue(self) -> int:
        return self.mUpperValue

    def setUpperValue(self, value: int):
        if value > self.mMaximum:
            value = self.mMaximum
        if value < self.mMinimum:
            value = self.mMinimum
        self.mUpperValue = value
        self.upperValueChanged.emit(self.mUpperValue)
        self.update()

    def setRange(self, minimum: int, maximum: int):
        self.setMinimum(minimum)
        self.setMaximum(maximum)

    # Optional: Properties zur leichteren Verwendung
    minimum = property(getMinimum, setMinimum)
    maximum = property(getMaximum, setMaximum)
    lowerValue = property(getLowerValue, setLowerValue)
    upperValue = property(getUpperValue, setUpperValue)



class RangeSliderDemo(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("RangeSlider Beispiel")

        # Zentrales Widget und Layout erstellen
        centralWidget = QWidget(self)
        self.setCentralWidget(centralWidget)
        layout = QVBoxLayout(centralWidget)

        # Label zum Anzeigen der Werte
        self.label = QLabel("Werte: 0 - 100", self)
        layout.addWidget(self.label)

        # Erstelle den RangeSlider
        self.rangeSlider = RangeSlider(orientation=Qt.Horizontal)
        self.rangeSlider.setRange(0, 200)
        self.rangeSlider.setLowerValue(50)
        self.rangeSlider.setUpperValue(150)
        layout.addWidget(self.rangeSlider)

        # Signale verbinden, um das Label zu aktualisieren, wenn sich die Werte ändern
        self.rangeSlider.lowerValueChanged.connect(self.updateLabel)
        self.rangeSlider.upperValueChanged.connect(self.updateLabel)

    def updateLabel(self, value):
        # Hole die aktuellen Werte und aktualisiere das Label
        lower = self.rangeSlider.lowerValue
        upper = self.rangeSlider.upperValue
        self.label.setText(f"Werte: {lower} - {upper}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    demo = RangeSliderDemo()
    demo.resize(400, 150)
    demo.show()
    sys.exit(app.exec())