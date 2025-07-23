# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'pdf_display.ui'
##
## Created by: Qt User Interface Compiler version 6.8.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QButtonGroup, QFormLayout, QGraphicsView,
    QGroupBox, QHBoxLayout, QLabel, QLineEdit,
    QListWidget, QListWidgetItem, QPushButton, QSizePolicy,
    QSpacerItem, QSpinBox, QSplitter, QVBoxLayout,
    QWidget)
import resources_rc

class Ui_PdfDisplayView(object):
    def setupUi(self, PdfDisplayView):
        if not PdfDisplayView.objectName():
            PdfDisplayView.setObjectName(u"PdfDisplayView")
        PdfDisplayView.resize(1096, 967)
        self.verticalLayout_5 = QVBoxLayout(PdfDisplayView)
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.splitter = QSplitter(PdfDisplayView)
        self.splitter.setObjectName(u"splitter")
        self.splitter.setOrientation(Qt.Orientation.Horizontal)
        self.layoutWidget = QWidget(self.splitter)
        self.layoutWidget.setObjectName(u"layoutWidget")
        self.user_interface_layout = QVBoxLayout(self.layoutWidget)
        self.user_interface_layout.setObjectName(u"user_interface_layout")
        self.user_interface_layout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_toolbar = QHBoxLayout()
        self.horizontalLayout_toolbar.setSpacing(6)
        self.horizontalLayout_toolbar.setObjectName(u"horizontalLayout_toolbar")
        self.btnLoadPDF = QPushButton(self.layoutWidget)
        self.btnLoadPDF.setObjectName(u"btnLoadPDF")

        self.horizontalLayout_toolbar.addWidget(self.btnLoadPDF)

        self.btnGeneratePDF = QPushButton(self.layoutWidget)
        self.btnGeneratePDF.setObjectName(u"btnGeneratePDF")

        self.horizontalLayout_toolbar.addWidget(self.btnGeneratePDF)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_toolbar.addItem(self.horizontalSpacer)

        self.btnMenuOpenClose = QPushButton(self.layoutWidget)
        self.btnMenuOpenClose.setObjectName(u"btnMenuOpenClose")
        icon = QIcon()
        icon.addFile(u":/icons/icons/white/menu.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.btnMenuOpenClose.setIcon(icon)
        self.btnMenuOpenClose.setIconSize(QSize(24, 24))

        self.horizontalLayout_toolbar.addWidget(self.btnMenuOpenClose)


        self.user_interface_layout.addLayout(self.horizontalLayout_toolbar)

        self.verticalLayout_pdf = QVBoxLayout()
        self.verticalLayout_pdf.setObjectName(u"verticalLayout_pdf")
        self.graphicsView = QGraphicsView(self.layoutWidget)
        self.graphicsView.setObjectName(u"graphicsView")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(2)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.graphicsView.sizePolicy().hasHeightForWidth())
        self.graphicsView.setSizePolicy(sizePolicy)

        self.verticalLayout_pdf.addWidget(self.graphicsView)

        self.horizontalLayout_zoom = QHBoxLayout()
        self.horizontalLayout_zoom.setSpacing(6)
        self.horizontalLayout_zoom.setObjectName(u"horizontalLayout_zoom")
        self.zoomLeftSpacer = QSpacerItem(20, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_zoom.addItem(self.zoomLeftSpacer)

        self.btnZoomIn = QPushButton(self.layoutWidget)
        self.btnZoomIn.setObjectName(u"btnZoomIn")

        self.horizontalLayout_zoom.addWidget(self.btnZoomIn)

        self.btnZoomOut = QPushButton(self.layoutWidget)
        self.btnZoomOut.setObjectName(u"btnZoomOut")

        self.horizontalLayout_zoom.addWidget(self.btnZoomOut)

        self.zoomRightSpacer = QSpacerItem(20, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_zoom.addItem(self.zoomRightSpacer)


        self.verticalLayout_pdf.addLayout(self.horizontalLayout_zoom)


        self.user_interface_layout.addLayout(self.verticalLayout_pdf)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.btnAddSingleBox = QPushButton(self.layoutWidget)
        self.btnAddSingleBox.setObjectName(u"btnAddSingleBox")

        self.horizontalLayout_3.addWidget(self.btnAddSingleBox)

        self.btnAddBoxPair = QPushButton(self.layoutWidget)
        self.btnAddBoxPair.setObjectName(u"btnAddBoxPair")

        self.horizontalLayout_3.addWidget(self.btnAddBoxPair)

        self.btnRemoveBoxPair = QPushButton(self.layoutWidget)
        self.btnRemoveBoxPair.setObjectName(u"btnRemoveBoxPair")

        self.horizontalLayout_3.addWidget(self.btnRemoveBoxPair)

        self.actionSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_3.addItem(self.actionSpacer)

        self.btnRestore = QPushButton(self.layoutWidget)
        self.btnRestore.setObjectName(u"btnRestore")

        self.horizontalLayout_3.addWidget(self.btnRestore)


        self.user_interface_layout.addLayout(self.horizontalLayout_3)

        self.splitter.addWidget(self.layoutWidget)
        self.layoutWidget1 = QWidget(self.splitter)
        self.layoutWidget1.setObjectName(u"layoutWidget1")
        self.pdf_display_layout = QVBoxLayout(self.layoutWidget1)
        self.pdf_display_layout.setObjectName(u"pdf_display_layout")
        self.pdf_display_layout.setContentsMargins(0, 0, 0, 0)
        self.groupBox_3 = QGroupBox(self.layoutWidget1)
        self.groupBox_3.setObjectName(u"groupBox_3")
        self.verticalLayout_3 = QVBoxLayout(self.groupBox_3)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.verticalLayout_3.setContentsMargins(-1, 20, -1, -1)
        self.btnLoadConfig = QPushButton(self.groupBox_3)
        self.btnLoadConfig.setObjectName(u"btnLoadConfig")

        self.verticalLayout_3.addWidget(self.btnLoadConfig)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.btnSaveConfig = QPushButton(self.groupBox_3)
        self.buttonGroup = QButtonGroup(PdfDisplayView)
        self.buttonGroup.setObjectName(u"buttonGroup")
        self.buttonGroup.addButton(self.btnSaveConfig)
        self.btnSaveConfig.setObjectName(u"btnSaveConfig")

        self.horizontalLayout.addWidget(self.btnSaveConfig)

        self.btnSaveAsConfig = QPushButton(self.groupBox_3)
        self.buttonGroup.addButton(self.btnSaveAsConfig)
        self.btnSaveAsConfig.setObjectName(u"btnSaveAsConfig")

        self.horizontalLayout.addWidget(self.btnSaveAsConfig)


        self.verticalLayout_3.addLayout(self.horizontalLayout)


        self.pdf_display_layout.addWidget(self.groupBox_3)

        self.groupBoxDisplayDpi = QGroupBox(self.layoutWidget1)
        self.groupBoxDisplayDpi.setObjectName(u"groupBoxDisplayDpi")
        self.horizontalLayout_display_dpi = QHBoxLayout(self.groupBoxDisplayDpi)
        self.horizontalLayout_display_dpi.setObjectName(u"horizontalLayout_display_dpi")
        self.spinBoxDisplayDpi = QSpinBox(self.groupBoxDisplayDpi)
        self.spinBoxDisplayDpi.setObjectName(u"spinBoxDisplayDpi")
        self.spinBoxDisplayDpi.setMinimum(72)
        self.spinBoxDisplayDpi.setMaximum(600)
        self.spinBoxDisplayDpi.setValue(150)

        self.horizontalLayout_display_dpi.addWidget(self.spinBoxDisplayDpi)


        self.pdf_display_layout.addWidget(self.groupBoxDisplayDpi)

        self.groupBox_2 = QGroupBox(self.layoutWidget1)
        self.groupBox_2.setObjectName(u"groupBox_2")
        self.verticalLayout_2 = QVBoxLayout(self.groupBox_2)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(-1, 20, -1, -1)
        self.listBoxPairs = QListWidget(self.groupBox_2)
        self.listBoxPairs.setObjectName(u"listBoxPairs")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.listBoxPairs.sizePolicy().hasHeightForWidth())
        self.listBoxPairs.setSizePolicy(sizePolicy1)

        self.verticalLayout_2.addWidget(self.listBoxPairs)


        self.pdf_display_layout.addWidget(self.groupBox_2)

        self.groupBoxProperties = QGroupBox(self.layoutWidget1)
        self.groupBoxProperties.setObjectName(u"groupBoxProperties")
        self.formLayoutProperties = QFormLayout(self.groupBoxProperties)
        self.formLayoutProperties.setObjectName(u"formLayoutProperties")
        self.formLayoutProperties.setContentsMargins(-1, 20, -1, -1)
        self.labelX = QLabel(self.groupBoxProperties)
        self.labelX.setObjectName(u"labelX")

        self.formLayoutProperties.setWidget(0, QFormLayout.LabelRole, self.labelX)

        self.lineEditX = QLineEdit(self.groupBoxProperties)
        self.lineEditX.setObjectName(u"lineEditX")
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.lineEditX.sizePolicy().hasHeightForWidth())
        self.lineEditX.setSizePolicy(sizePolicy2)

        self.formLayoutProperties.setWidget(0, QFormLayout.FieldRole, self.lineEditX)

        self.labelY = QLabel(self.groupBoxProperties)
        self.labelY.setObjectName(u"labelY")

        self.formLayoutProperties.setWidget(1, QFormLayout.LabelRole, self.labelY)

        self.lineEditY = QLineEdit(self.groupBoxProperties)
        self.lineEditY.setObjectName(u"lineEditY")
        sizePolicy2.setHeightForWidth(self.lineEditY.sizePolicy().hasHeightForWidth())
        self.lineEditY.setSizePolicy(sizePolicy2)

        self.formLayoutProperties.setWidget(1, QFormLayout.FieldRole, self.lineEditY)

        self.labelWidth = QLabel(self.groupBoxProperties)
        self.labelWidth.setObjectName(u"labelWidth")

        self.formLayoutProperties.setWidget(2, QFormLayout.LabelRole, self.labelWidth)

        self.lineEditWidth = QLineEdit(self.groupBoxProperties)
        self.lineEditWidth.setObjectName(u"lineEditWidth")
        sizePolicy2.setHeightForWidth(self.lineEditWidth.sizePolicy().hasHeightForWidth())
        self.lineEditWidth.setSizePolicy(sizePolicy2)

        self.formLayoutProperties.setWidget(2, QFormLayout.FieldRole, self.lineEditWidth)

        self.labelHeight = QLabel(self.groupBoxProperties)
        self.labelHeight.setObjectName(u"labelHeight")

        self.formLayoutProperties.setWidget(3, QFormLayout.LabelRole, self.labelHeight)

        self.lineEditHeight = QLineEdit(self.groupBoxProperties)
        self.lineEditHeight.setObjectName(u"lineEditHeight")
        sizePolicy2.setHeightForWidth(self.lineEditHeight.sizePolicy().hasHeightForWidth())
        self.lineEditHeight.setSizePolicy(sizePolicy2)

        self.formLayoutProperties.setWidget(3, QFormLayout.FieldRole, self.lineEditHeight)


        self.pdf_display_layout.addWidget(self.groupBoxProperties)

        self.groupBox = QGroupBox(self.layoutWidget1)
        self.groupBox.setObjectName(u"groupBox")
        self.horizontalLayout_2 = QHBoxLayout(self.groupBox)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout_2.setContentsMargins(-1, 20, -1, -1)
        self.layoutOutput = QHBoxLayout()
        self.layoutOutput.setObjectName(u"layoutOutput")
        self.lineEditOutputPath = QLineEdit(self.groupBox)
        self.lineEditOutputPath.setObjectName(u"lineEditOutputPath")

        self.layoutOutput.addWidget(self.lineEditOutputPath)

        self.btnSaveOutputPath = QPushButton(self.groupBox)
        self.btnSaveOutputPath.setObjectName(u"btnSaveOutputPath")

        self.layoutOutput.addWidget(self.btnSaveOutputPath)


        self.horizontalLayout_2.addLayout(self.layoutOutput)


        self.pdf_display_layout.addWidget(self.groupBox)

        self.verticalSpacer = QSpacerItem(20, 17, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.pdf_display_layout.addItem(self.verticalSpacer)

        self.splitter.addWidget(self.layoutWidget1)

        self.verticalLayout_5.addWidget(self.splitter)


        self.retranslateUi(PdfDisplayView)

        QMetaObject.connectSlotsByName(PdfDisplayView)
    # setupUi

    def retranslateUi(self, PdfDisplayView):
        PdfDisplayView.setWindowTitle(QCoreApplication.translate("PdfDisplayView", u"PDF Editor mit resizbaren Box-Overlays", None))
        PdfDisplayView.setStyleSheet(QCoreApplication.translate("PdfDisplayView", u"QWidget { font-family: \"Segoe UI\", sans-serif; font-size: 10pt; background-color: #f0f0f0; }\n"
"QPushButton { border: none; padding: 6px 12px; border-radius: 4px; background-color: #0078d7; color: white; }\n"
"QPushButton:hover { background-color: #005a9e; }\n"
"QGroupBox { border: 1px solid #cccccc; border-radius: 4px; margin-top: 6px; }\n"
"QGroupBox::title { subcontrol-origin: margin; subcontrol-position: top left; padding: 0 6px; }", None))
        self.btnLoadPDF.setText(QCoreApplication.translate("PdfDisplayView", u"PDF Laden", None))
        self.btnGeneratePDF.setText(QCoreApplication.translate("PdfDisplayView", u"Exportieren", None))
        self.btnMenuOpenClose.setText("")
        self.btnZoomIn.setText(QCoreApplication.translate("PdfDisplayView", u"+", None))
        self.btnZoomOut.setText(QCoreApplication.translate("PdfDisplayView", u"\u2212", None))
        self.btnAddSingleBox.setText(QCoreApplication.translate("PdfDisplayView", u"Datum hinzuf\u00fcgen", None))
        self.btnAddBoxPair.setText(QCoreApplication.translate("PdfDisplayView", u"StNr. hinzuf\u00fcgen", None))
        self.btnRemoveBoxPair.setText(QCoreApplication.translate("PdfDisplayView", u"Entfernen", None))
        self.btnRestore.setText(QCoreApplication.translate("PdfDisplayView", u"Zur\u00fccksetzen", None))
        self.groupBox_3.setTitle(QCoreApplication.translate("PdfDisplayView", u"Konfiguration", None))
        self.btnLoadConfig.setText(QCoreApplication.translate("PdfDisplayView", u"Laden", None))
        self.btnSaveConfig.setText(QCoreApplication.translate("PdfDisplayView", u"Speichern", None))
        self.btnSaveAsConfig.setText(QCoreApplication.translate("PdfDisplayView", u"Speichern unter", None))
        self.groupBoxDisplayDpi.setTitle(QCoreApplication.translate("PdfDisplayView", u"PDF DPI", None))
        self.groupBox_2.setTitle(QCoreApplication.translate("PdfDisplayView", u"Name und Stammnummer", None))
        self.groupBoxProperties.setTitle(QCoreApplication.translate("PdfDisplayView", u"Box Eigenschaften", None))
        self.labelX.setText(QCoreApplication.translate("PdfDisplayView", u"X:", None))
        self.labelY.setText(QCoreApplication.translate("PdfDisplayView", u"Y:", None))
        self.labelWidth.setText(QCoreApplication.translate("PdfDisplayView", u"Breite:", None))
        self.labelHeight.setText(QCoreApplication.translate("PdfDisplayView", u"H\u00f6he:", None))
        self.groupBox.setTitle(QCoreApplication.translate("PdfDisplayView", u"PDF Speicherort:", None))
        self.btnSaveOutputPath.setText(QCoreApplication.translate("PdfDisplayView", u"Speichern", None))
    # retranslateUi

