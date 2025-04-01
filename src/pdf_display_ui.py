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
from PySide6.QtWidgets import (QApplication, QGraphicsView, QGroupBox, QHBoxLayout,
    QListWidget, QListWidgetItem, QPushButton, QSizePolicy,
    QSpacerItem, QVBoxLayout, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(874, 823)
        self.horizontalLayout_5 = QHBoxLayout(MainWindow)
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.verticalLayout_3 = QVBoxLayout()
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.graphicsView = QGraphicsView(MainWindow)
        self.graphicsView.setObjectName(u"graphicsView")

        self.verticalLayout_3.addWidget(self.graphicsView)

        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_4.addItem(self.horizontalSpacer)

        self.btnZoomIn = QPushButton(MainWindow)
        self.btnZoomIn.setObjectName(u"btnZoomIn")

        self.horizontalLayout_4.addWidget(self.btnZoomIn)

        self.btnZoomOut = QPushButton(MainWindow)
        self.btnZoomOut.setObjectName(u"btnZoomOut")

        self.horizontalLayout_4.addWidget(self.btnZoomOut)


        self.verticalLayout_3.addLayout(self.horizontalLayout_4)


        self.horizontalLayout_5.addLayout(self.verticalLayout_3)

        self.verticalLayout_2 = QVBoxLayout()
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.groupBox_2 = QGroupBox(MainWindow)
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

        self.btnClosePDF = QPushButton(self.groupBox_2)
        self.btnClosePDF.setObjectName(u"btnClosePDF")
        sizePolicy.setHeightForWidth(self.btnClosePDF.sizePolicy().hasHeightForWidth())
        self.btnClosePDF.setSizePolicy(sizePolicy)

        self.horizontalLayout_2.addWidget(self.btnClosePDF)


        self.verticalLayout_2.addWidget(self.groupBox_2)

        self.groupBox_3 = QGroupBox(MainWindow)
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

        self.groupBox = QGroupBox(MainWindow)
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

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_2.addItem(self.verticalSpacer)


        self.horizontalLayout_5.addLayout(self.verticalLayout_2)


        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"PDF Editor mit resizbaren Box-Overlays", None))
        self.btnZoomIn.setText(QCoreApplication.translate("MainWindow", u"  +  ", None))
        self.btnZoomOut.setText(QCoreApplication.translate("MainWindow", u"  -  ", None))
        self.groupBox_2.setTitle("")
        self.btnLoadPDF.setText(QCoreApplication.translate("MainWindow", u"PDF laden", None))
        self.btnGeneratePDF.setText(QCoreApplication.translate("MainWindow", u"Drucken", None))
        self.btnClosePDF.setText(QCoreApplication.translate("MainWindow", u"Beenden", None))
        self.groupBox_3.setTitle(QCoreApplication.translate("MainWindow", u"Konfiguration:", None))
        self.btnSave.setText(QCoreApplication.translate("MainWindow", u"Speichern", None))
        self.btnLoad.setText(QCoreApplication.translate("MainWindow", u"Laden", None))
        self.groupBox.setTitle(QCoreApplication.translate("MainWindow", u"Name und Stammnummer:", None))
        self.btnAddBoxPair.setText(QCoreApplication.translate("MainWindow", u"+ 2", None))
        self.btnAddSingleBox.setText(QCoreApplication.translate("MainWindow", u" + 1", None))
        self.btnRemoveBoxPair.setText(QCoreApplication.translate("MainWindow", u"-", None))
    # retranslateUi

