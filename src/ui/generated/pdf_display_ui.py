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
from PySide6.QtWidgets import (QApplication, QGraphicsView, QGridLayout, QGroupBox,
    QHBoxLayout, QLabel, QLineEdit, QListWidget,
    QListWidgetItem, QPushButton, QSizePolicy, QSpacerItem,
    QVBoxLayout, QWidget)

class Ui_PdfDisplayView(object):
    def setupUi(self, PdfDisplayView):
        if not PdfDisplayView.objectName():
            PdfDisplayView.setObjectName(u"PdfDisplayView")
        PdfDisplayView.resize(1103, 681)
        self.horizontalLayout_5 = QHBoxLayout(PdfDisplayView)
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.verticalLayout_3 = QVBoxLayout()
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.graphicsView = QGraphicsView(PdfDisplayView)
        self.graphicsView.setObjectName(u"graphicsView")

        self.verticalLayout_3.addWidget(self.graphicsView)

        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_4.addItem(self.horizontalSpacer)

        self.btnZoomIn = QPushButton(PdfDisplayView)
        self.btnZoomIn.setObjectName(u"btnZoomIn")

        self.horizontalLayout_4.addWidget(self.btnZoomIn)

        self.btnZoomOut = QPushButton(PdfDisplayView)
        self.btnZoomOut.setObjectName(u"btnZoomOut")

        self.horizontalLayout_4.addWidget(self.btnZoomOut)


        self.verticalLayout_3.addLayout(self.horizontalLayout_4)


        self.horizontalLayout_5.addLayout(self.verticalLayout_3)

        self.verticalLayout_2 = QVBoxLayout()
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.groupBox_2 = QGroupBox(PdfDisplayView)
        self.groupBox_2.setObjectName(u"groupBox_2")
        self.horizontalLayout_2 = QHBoxLayout(self.groupBox_2)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.btnLoadPDF = QPushButton(self.groupBox_2)
        self.btnLoadPDF.setObjectName(u"btnLoadPDF")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btnLoadPDF.sizePolicy().hasHeightForWidth())
        self.btnLoadPDF.setSizePolicy(sizePolicy)

        self.horizontalLayout_2.addWidget(self.btnLoadPDF)

        self.btnGeneratePDF = QPushButton(self.groupBox_2)
        self.btnGeneratePDF.setObjectName(u"btnGeneratePDF")
        sizePolicy.setHeightForWidth(self.btnGeneratePDF.sizePolicy().hasHeightForWidth())
        self.btnGeneratePDF.setSizePolicy(sizePolicy)

        self.horizontalLayout_2.addWidget(self.btnGeneratePDF)


        self.verticalLayout_2.addWidget(self.groupBox_2)

        self.groupBox_3 = QGroupBox(PdfDisplayView)
        self.groupBox_3.setObjectName(u"groupBox_3")
        self.horizontalLayout_3 = QHBoxLayout(self.groupBox_3)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.btnSave = QPushButton(self.groupBox_3)
        self.btnSave.setObjectName(u"btnSave")
        sizePolicy.setHeightForWidth(self.btnSave.sizePolicy().hasHeightForWidth())
        self.btnSave.setSizePolicy(sizePolicy)

        self.horizontalLayout_3.addWidget(self.btnSave)

        self.btnLoad = QPushButton(self.groupBox_3)
        self.btnLoad.setObjectName(u"btnLoad")
        sizePolicy.setHeightForWidth(self.btnLoad.sizePolicy().hasHeightForWidth())
        self.btnLoad.setSizePolicy(sizePolicy)

        self.horizontalLayout_3.addWidget(self.btnLoad)


        self.verticalLayout_2.addWidget(self.groupBox_3)

        self.groupBox = QGroupBox(PdfDisplayView)
        self.groupBox.setObjectName(u"groupBox")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Preferred)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.groupBox.sizePolicy().hasHeightForWidth())
        self.groupBox.setSizePolicy(sizePolicy1)
        self.verticalLayout = QVBoxLayout(self.groupBox)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.listBoxPairs = QListWidget(self.groupBox)
        self.listBoxPairs.setObjectName(u"listBoxPairs")
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.listBoxPairs.sizePolicy().hasHeightForWidth())
        self.listBoxPairs.setSizePolicy(sizePolicy2)

        self.verticalLayout.addWidget(self.listBoxPairs)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.btnAddBoxPair = QPushButton(self.groupBox)
        self.btnAddBoxPair.setObjectName(u"btnAddBoxPair")
        sizePolicy3 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.btnAddBoxPair.sizePolicy().hasHeightForWidth())
        self.btnAddBoxPair.setSizePolicy(sizePolicy3)

        self.horizontalLayout.addWidget(self.btnAddBoxPair)

        self.btnAddSingleBox = QPushButton(self.groupBox)
        self.btnAddSingleBox.setObjectName(u"btnAddSingleBox")
        sizePolicy.setHeightForWidth(self.btnAddSingleBox.sizePolicy().hasHeightForWidth())
        self.btnAddSingleBox.setSizePolicy(sizePolicy)

        self.horizontalLayout.addWidget(self.btnAddSingleBox)

        self.btnRemoveBoxPair = QPushButton(self.groupBox)
        self.btnRemoveBoxPair.setObjectName(u"btnRemoveBoxPair")
        sizePolicy3.setHeightForWidth(self.btnRemoveBoxPair.sizePolicy().hasHeightForWidth())
        self.btnRemoveBoxPair.setSizePolicy(sizePolicy3)

        self.horizontalLayout.addWidget(self.btnRemoveBoxPair)


        self.verticalLayout.addLayout(self.horizontalLayout)


        self.verticalLayout_2.addWidget(self.groupBox)

        self.groupBoxProperties = QGroupBox(PdfDisplayView)
        self.groupBoxProperties.setObjectName(u"groupBoxProperties")
        self.gridLayout = QGridLayout(self.groupBoxProperties)
        self.gridLayout.setObjectName(u"gridLayout")
        self.labelX = QLabel(self.groupBoxProperties)
        self.labelX.setObjectName(u"labelX")

        self.gridLayout.addWidget(self.labelX, 0, 0, 1, 1)

        self.lineEditX = QLineEdit(self.groupBoxProperties)
        self.lineEditX.setObjectName(u"lineEditX")

        self.gridLayout.addWidget(self.lineEditX, 0, 1, 1, 1)

        self.labelY = QLabel(self.groupBoxProperties)
        self.labelY.setObjectName(u"labelY")

        self.gridLayout.addWidget(self.labelY, 0, 2, 1, 1)

        self.lineEditY = QLineEdit(self.groupBoxProperties)
        self.lineEditY.setObjectName(u"lineEditY")

        self.gridLayout.addWidget(self.lineEditY, 0, 3, 1, 2)

        self.labelWidth = QLabel(self.groupBoxProperties)
        self.labelWidth.setObjectName(u"labelWidth")

        self.gridLayout.addWidget(self.labelWidth, 1, 0, 1, 1)

        self.lineEditWidth = QLineEdit(self.groupBoxProperties)
        self.lineEditWidth.setObjectName(u"lineEditWidth")

        self.gridLayout.addWidget(self.lineEditWidth, 1, 1, 1, 1)

        self.labelHeight = QLabel(self.groupBoxProperties)
        self.labelHeight.setObjectName(u"labelHeight")

        self.gridLayout.addWidget(self.labelHeight, 1, 2, 1, 2)

        self.lineEditHeight = QLineEdit(self.groupBoxProperties)
        self.lineEditHeight.setObjectName(u"lineEditHeight")

        self.gridLayout.addWidget(self.lineEditHeight, 1, 4, 1, 1)


        self.verticalLayout_2.addWidget(self.groupBoxProperties)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_2.addItem(self.verticalSpacer)

        self.btnClosePDF = QPushButton(PdfDisplayView)
        self.btnClosePDF.setObjectName(u"btnClosePDF")
        sizePolicy.setHeightForWidth(self.btnClosePDF.sizePolicy().hasHeightForWidth())
        self.btnClosePDF.setSizePolicy(sizePolicy)

        self.verticalLayout_2.addWidget(self.btnClosePDF)


        self.horizontalLayout_5.addLayout(self.verticalLayout_2)


        self.retranslateUi(PdfDisplayView)

        QMetaObject.connectSlotsByName(PdfDisplayView)
    # setupUi

    def retranslateUi(self, PdfDisplayView):
        PdfDisplayView.setWindowTitle(QCoreApplication.translate("PdfDisplayView", u"PDF Editor mit resizbaren Box-Overlays", None))
        self.btnZoomIn.setText(QCoreApplication.translate("PdfDisplayView", u"  +  ", None))
        self.btnZoomOut.setText(QCoreApplication.translate("PdfDisplayView", u"  -  ", None))
        self.groupBox_2.setTitle("")
        self.btnLoadPDF.setText(QCoreApplication.translate("PdfDisplayView", u"PDF laden", None))
        self.btnGeneratePDF.setText(QCoreApplication.translate("PdfDisplayView", u"Drucken", None))
        self.groupBox_3.setTitle(QCoreApplication.translate("PdfDisplayView", u"Konfiguration:", None))
        self.btnSave.setText(QCoreApplication.translate("PdfDisplayView", u"Speichern", None))
        self.btnLoad.setText(QCoreApplication.translate("PdfDisplayView", u"Laden", None))
        self.groupBox.setTitle(QCoreApplication.translate("PdfDisplayView", u"Name und Stammnummer:", None))
        self.btnAddBoxPair.setText(QCoreApplication.translate("PdfDisplayView", u"+ 2", None))
        self.btnAddSingleBox.setText(QCoreApplication.translate("PdfDisplayView", u" + 1", None))
        self.btnRemoveBoxPair.setText(QCoreApplication.translate("PdfDisplayView", u"-", None))
        self.groupBoxProperties.setTitle(QCoreApplication.translate("PdfDisplayView", u"Box Eigenschaften", None))
        self.labelX.setText(QCoreApplication.translate("PdfDisplayView", u"X:", None))
        self.labelY.setText(QCoreApplication.translate("PdfDisplayView", u"Y:", None))
        self.labelWidth.setText(QCoreApplication.translate("PdfDisplayView", u"Width:", None))
        self.labelHeight.setText(QCoreApplication.translate("PdfDisplayView", u"Height:", None))
        self.btnClosePDF.setText(QCoreApplication.translate("PdfDisplayView", u"Schlie\u00dfen", None))
    # retranslateUi

