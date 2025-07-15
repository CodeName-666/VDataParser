# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'pdf_display.ui'
##
## Created by: Qt User Interface Compiler version 6.9.1
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
    QSpacerItem, QSplitter, QVBoxLayout, QWidget)

class Ui_PdfDisplayView(object):
    def setupUi(self, PdfDisplayView):
        if not PdfDisplayView.objectName():
            PdfDisplayView.setObjectName(u"PdfDisplayView")
        PdfDisplayView.resize(1096, 669)
        self.verticalLayout = QVBoxLayout(PdfDisplayView)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.horizontalLayout_toolbar = QHBoxLayout()
        self.horizontalLayout_toolbar.setSpacing(6)
        self.horizontalLayout_toolbar.setObjectName(u"horizontalLayout_toolbar")
        self.btnLoadPDF = QPushButton(PdfDisplayView)
        self.btnLoadPDF.setObjectName(u"btnLoadPDF")

        self.horizontalLayout_toolbar.addWidget(self.btnLoadPDF)

        self.btnGeneratePDF = QPushButton(PdfDisplayView)
        self.btnGeneratePDF.setObjectName(u"btnGeneratePDF")

        self.horizontalLayout_toolbar.addWidget(self.btnGeneratePDF)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_toolbar.addItem(self.horizontalSpacer)


        self.verticalLayout.addLayout(self.horizontalLayout_toolbar)

        self.splitter_main = QSplitter(PdfDisplayView)
        self.splitter_main.setObjectName(u"splitter_main")
        self.splitter_main.setOrientation(Qt.Orientation.Horizontal)
        self.pdfContainer = QWidget(self.splitter_main)
        self.pdfContainer.setObjectName(u"pdfContainer")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(2)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.pdfContainer.sizePolicy().hasHeightForWidth())
        self.pdfContainer.setSizePolicy(sizePolicy)
        self.verticalLayout_pdf = QVBoxLayout(self.pdfContainer)
        self.verticalLayout_pdf.setObjectName(u"verticalLayout_pdf")
        self.verticalLayout_pdf.setContentsMargins(0, 0, 0, 0)
        self.graphicsView = QGraphicsView(self.pdfContainer)
        self.graphicsView.setObjectName(u"graphicsView")
        sizePolicy.setHeightForWidth(self.graphicsView.sizePolicy().hasHeightForWidth())
        self.graphicsView.setSizePolicy(sizePolicy)

        self.verticalLayout_pdf.addWidget(self.graphicsView)

        self.horizontalLayout_zoom = QHBoxLayout()
        self.horizontalLayout_zoom.setSpacing(6)
        self.horizontalLayout_zoom.setObjectName(u"horizontalLayout_zoom")
        self.zoomLeftSpacer = QSpacerItem(20, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_zoom.addItem(self.zoomLeftSpacer)

        self.btnZoomIn = QPushButton(self.pdfContainer)
        self.btnZoomIn.setObjectName(u"btnZoomIn")

        self.horizontalLayout_zoom.addWidget(self.btnZoomIn)

        self.btnZoomOut = QPushButton(self.pdfContainer)
        self.btnZoomOut.setObjectName(u"btnZoomOut")

        self.horizontalLayout_zoom.addWidget(self.btnZoomOut)

        self.zoomRightSpacer = QSpacerItem(20, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_zoom.addItem(self.zoomRightSpacer)


        self.verticalLayout_pdf.addLayout(self.horizontalLayout_zoom)

        self.splitter_main.addWidget(self.pdfContainer)
        self.sidebarWidget = QWidget(self.splitter_main)
        self.sidebarWidget.setObjectName(u"sidebarWidget")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        sizePolicy1.setHorizontalStretch(1)
        sizePolicy1.setVerticalStretch(1)
        sizePolicy1.setHeightForWidth(self.sidebarWidget.sizePolicy().hasHeightForWidth())
        self.sidebarWidget.setSizePolicy(sizePolicy1)
        self.verticalLayout_sidebar = QVBoxLayout(self.sidebarWidget)
        self.verticalLayout_sidebar.setSpacing(12)
        self.verticalLayout_sidebar.setObjectName(u"verticalLayout_sidebar")
        self.verticalLayout_sidebar.setContentsMargins(0, 0, 0, 0)
        self.groupBox_2 = QGroupBox(self.sidebarWidget)
        self.groupBox_2.setObjectName(u"groupBox_2")
        self.verticalLayout_2 = QVBoxLayout(self.groupBox_2)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(-1, 20, -1, -1)
        self.listBoxPairs = QListWidget(self.groupBox_2)
        self.listBoxPairs.setObjectName(u"listBoxPairs")

        self.verticalLayout_2.addWidget(self.listBoxPairs)


        self.verticalLayout_sidebar.addWidget(self.groupBox_2)

        self.groupBox = QGroupBox(self.sidebarWidget)
        self.groupBox.setObjectName(u"groupBox")
        self.formLayout_1 = QFormLayout(self.groupBox)
        self.formLayout_1.setObjectName(u"formLayout_1")
        self.formLayout_1.setContentsMargins(-1, 20, -1, -1)
        self.label_name = QLabel(self.groupBox)
        self.label_name.setObjectName(u"label_name")

        self.formLayout_1.setWidget(0, QFormLayout.ItemRole.LabelRole, self.label_name)

        self.lineEditName = QLineEdit(self.groupBox)
        self.lineEditName.setObjectName(u"lineEditName")
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.lineEditName.sizePolicy().hasHeightForWidth())
        self.lineEditName.setSizePolicy(sizePolicy2)

        self.formLayout_1.setWidget(0, QFormLayout.ItemRole.FieldRole, self.lineEditName)

        self.label_stammnummer = QLabel(self.groupBox)
        self.label_stammnummer.setObjectName(u"label_stammnummer")

        self.formLayout_1.setWidget(1, QFormLayout.ItemRole.LabelRole, self.label_stammnummer)

        self.lineEditStammnummer = QLineEdit(self.groupBox)
        self.lineEditStammnummer.setObjectName(u"lineEditStammnummer")
        sizePolicy2.setHeightForWidth(self.lineEditStammnummer.sizePolicy().hasHeightForWidth())
        self.lineEditStammnummer.setSizePolicy(sizePolicy2)

        self.formLayout_1.setWidget(1, QFormLayout.ItemRole.FieldRole, self.lineEditStammnummer)


        self.verticalLayout_sidebar.addWidget(self.groupBox)

        self.groupBoxProperties = QGroupBox(self.sidebarWidget)
        self.groupBoxProperties.setObjectName(u"groupBoxProperties")
        self.formLayoutProperties = QFormLayout(self.groupBoxProperties)
        self.formLayoutProperties.setObjectName(u"formLayoutProperties")
        self.formLayoutProperties.setContentsMargins(-1, 20, -1, -1)
        self.labelX = QLabel(self.groupBoxProperties)
        self.labelX.setObjectName(u"labelX")

        self.formLayoutProperties.setWidget(0, QFormLayout.ItemRole.LabelRole, self.labelX)

        self.lineEditX = QLineEdit(self.groupBoxProperties)
        self.lineEditX.setObjectName(u"lineEditX")
        sizePolicy2.setHeightForWidth(self.lineEditX.sizePolicy().hasHeightForWidth())
        self.lineEditX.setSizePolicy(sizePolicy2)

        self.formLayoutProperties.setWidget(0, QFormLayout.ItemRole.FieldRole, self.lineEditX)

        self.labelY = QLabel(self.groupBoxProperties)
        self.labelY.setObjectName(u"labelY")

        self.formLayoutProperties.setWidget(1, QFormLayout.ItemRole.LabelRole, self.labelY)

        self.lineEditY = QLineEdit(self.groupBoxProperties)
        self.lineEditY.setObjectName(u"lineEditY")
        sizePolicy2.setHeightForWidth(self.lineEditY.sizePolicy().hasHeightForWidth())
        self.lineEditY.setSizePolicy(sizePolicy2)

        self.formLayoutProperties.setWidget(1, QFormLayout.ItemRole.FieldRole, self.lineEditY)

        self.labelWidth = QLabel(self.groupBoxProperties)
        self.labelWidth.setObjectName(u"labelWidth")

        self.formLayoutProperties.setWidget(2, QFormLayout.ItemRole.LabelRole, self.labelWidth)

        self.lineEditWidth = QLineEdit(self.groupBoxProperties)
        self.lineEditWidth.setObjectName(u"lineEditWidth")
        sizePolicy2.setHeightForWidth(self.lineEditWidth.sizePolicy().hasHeightForWidth())
        self.lineEditWidth.setSizePolicy(sizePolicy2)

        self.formLayoutProperties.setWidget(2, QFormLayout.ItemRole.FieldRole, self.lineEditWidth)

        self.labelHeight = QLabel(self.groupBoxProperties)
        self.labelHeight.setObjectName(u"labelHeight")

        self.formLayoutProperties.setWidget(3, QFormLayout.ItemRole.LabelRole, self.labelHeight)

        self.lineEditHeight = QLineEdit(self.groupBoxProperties)
        self.lineEditHeight.setObjectName(u"lineEditHeight")
        sizePolicy2.setHeightForWidth(self.lineEditHeight.sizePolicy().hasHeightForWidth())
        self.lineEditHeight.setSizePolicy(sizePolicy2)

        self.formLayoutProperties.setWidget(3, QFormLayout.ItemRole.FieldRole, self.lineEditHeight)


        self.verticalLayout_sidebar.addWidget(self.groupBoxProperties)

        self.groupBox_3 = QGroupBox(self.sidebarWidget)
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

        self.formLayoutOutput = QFormLayout()
        self.formLayoutOutput.setObjectName(u"formLayoutOutput")
        self.labelOutputPath = QLabel(self.groupBox_3)
        self.labelOutputPath.setObjectName(u"labelOutputPath")

        self.formLayoutOutput.setWidget(0, QFormLayout.ItemRole.LabelRole, self.labelOutputPath)

        self.layoutOutput = QHBoxLayout()
        self.layoutOutput.setObjectName(u"layoutOutput")
        self.lineEditOutputPath = QLineEdit(self.groupBox_3)
        self.lineEditOutputPath.setObjectName(u"lineEditOutputPath")

        self.layoutOutput.addWidget(self.lineEditOutputPath)

        self.btnSaveOutputPath = QPushButton(self.groupBox_3)
        self.btnSaveOutputPath.setObjectName(u"btnSaveOutputPath")

        self.layoutOutput.addWidget(self.btnSaveOutputPath)


        self.formLayoutOutput.setLayout(0, QFormLayout.ItemRole.FieldRole, self.layoutOutput)


        self.verticalLayout_3.addLayout(self.formLayoutOutput)


        self.verticalLayout_sidebar.addWidget(self.groupBox_3)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_sidebar.addItem(self.verticalSpacer)

        self.splitter_main.addWidget(self.sidebarWidget)

        self.verticalLayout.addWidget(self.splitter_main)

        self.horizontalLayout_actions = QHBoxLayout()
        self.horizontalLayout_actions.setSpacing(8)
        self.horizontalLayout_actions.setObjectName(u"horizontalLayout_actions")
        self.btnAddSingleBox = QPushButton(PdfDisplayView)
        self.btnAddSingleBox.setObjectName(u"btnAddSingleBox")

        self.horizontalLayout_actions.addWidget(self.btnAddSingleBox)

        self.btnAddBoxPair = QPushButton(PdfDisplayView)
        self.btnAddBoxPair.setObjectName(u"btnAddBoxPair")

        self.horizontalLayout_actions.addWidget(self.btnAddBoxPair)

        self.btnRemoveBoxPair = QPushButton(PdfDisplayView)
        self.btnRemoveBoxPair.setObjectName(u"btnRemoveBoxPair")

        self.horizontalLayout_actions.addWidget(self.btnRemoveBoxPair)

        self.actionSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_actions.addItem(self.actionSpacer)

        self.btnClosePDF = QPushButton(PdfDisplayView)
        self.btnClosePDF.setObjectName(u"btnClosePDF")

        self.horizontalLayout_actions.addWidget(self.btnClosePDF)


        self.verticalLayout.addLayout(self.horizontalLayout_actions)


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
        self.btnZoomIn.setText(QCoreApplication.translate("PdfDisplayView", u"+", None))
        self.btnZoomOut.setText(QCoreApplication.translate("PdfDisplayView", u"\u2212", None))
        self.groupBox_2.setTitle(QCoreApplication.translate("PdfDisplayView", u"\u00dcbersicht", None))
        self.groupBox.setTitle(QCoreApplication.translate("PdfDisplayView", u"Name und Stammnummer", None))
        self.label_name.setText(QCoreApplication.translate("PdfDisplayView", u"Name:", None))
        self.label_stammnummer.setText(QCoreApplication.translate("PdfDisplayView", u"Stammnummer:", None))
        self.groupBoxProperties.setTitle(QCoreApplication.translate("PdfDisplayView", u"Box Eigenschaften", None))
        self.labelX.setText(QCoreApplication.translate("PdfDisplayView", u"X:", None))
        self.labelY.setText(QCoreApplication.translate("PdfDisplayView", u"Y:", None))
        self.labelWidth.setText(QCoreApplication.translate("PdfDisplayView", u"Breite:", None))
        self.labelHeight.setText(QCoreApplication.translate("PdfDisplayView", u"H\u00f6he:", None))
        self.groupBox_3.setTitle(QCoreApplication.translate("PdfDisplayView", u"Konfiguration", None))
        self.btnLoadConfig.setText(QCoreApplication.translate("PdfDisplayView", u"Laden", None))
        self.btnSaveConfig.setText(QCoreApplication.translate("PdfDisplayView", u"Speichern", None))
        self.btnSaveAsConfig.setText(QCoreApplication.translate("PdfDisplayView", u"Speichern unter", None))
        self.labelOutputPath.setText(QCoreApplication.translate("PdfDisplayView", u"Output Datei:", None))
        self.btnSaveOutputPath.setText(QCoreApplication.translate("PdfDisplayView", u"Speichern", None))
        self.btnAddSingleBox.setText(QCoreApplication.translate("PdfDisplayView", u"Datum hinzuf\u00fcgen", None))
        self.btnAddBoxPair.setText(QCoreApplication.translate("PdfDisplayView", u"StNr. hinzuf\u00fcgen", None))
        self.btnRemoveBoxPair.setText(QCoreApplication.translate("PdfDisplayView", u"Entfernen", None))
        self.btnClosePDF.setText(QCoreApplication.translate("PdfDisplayView", u"Schlie\u00dfen", None))
    # retranslateUi

