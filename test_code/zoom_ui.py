# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'zoom.ui'
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
from PySide6.QtWidgets import (QApplication, QGraphicsView, QHBoxLayout, QListWidget,
    QListWidgetItem, QMainWindow, QMenuBar, QPushButton,
    QSizePolicy, QSpacerItem, QStatusBar, QVBoxLayout,
    QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(900, 700)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.horizontalLayout = QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.graphicsView = QGraphicsView(self.centralwidget)
        self.graphicsView.setObjectName(u"graphicsView")

        self.horizontalLayout.addWidget(self.graphicsView)

        self.sideMenu = QWidget(self.centralwidget)
        self.sideMenu.setObjectName(u"sideMenu")
        self.verticalLayout = QVBoxLayout(self.sideMenu)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.btnLoadPDF = QPushButton(self.sideMenu)
        self.btnLoadPDF.setObjectName(u"btnLoadPDF")

        self.verticalLayout.addWidget(self.btnLoadPDF)

        self.btnAddBoxPair = QPushButton(self.sideMenu)
        self.btnAddBoxPair.setObjectName(u"btnAddBoxPair")

        self.verticalLayout.addWidget(self.btnAddBoxPair)

        self.btnRemoveBoxPair = QPushButton(self.sideMenu)
        self.btnRemoveBoxPair.setObjectName(u"btnRemoveBoxPair")

        self.verticalLayout.addWidget(self.btnRemoveBoxPair)

        self.btnZoomIn = QPushButton(self.sideMenu)
        self.btnZoomIn.setObjectName(u"btnZoomIn")

        self.verticalLayout.addWidget(self.btnZoomIn)

        self.btnZoomOut = QPushButton(self.sideMenu)
        self.btnZoomOut.setObjectName(u"btnZoomOut")

        self.verticalLayout.addWidget(self.btnZoomOut)

        self.btnAddSingleBox = QPushButton(self.sideMenu)
        self.btnAddSingleBox.setObjectName(u"btnAddSingleBox")

        self.verticalLayout.addWidget(self.btnAddSingleBox)

        self.btnSave = QPushButton(self.sideMenu)
        self.btnSave.setObjectName(u"btnSave")

        self.verticalLayout.addWidget(self.btnSave)

        self.btnLoad = QPushButton(self.sideMenu)
        self.btnLoad.setObjectName(u"btnLoad")

        self.verticalLayout.addWidget(self.btnLoad)

        self.listBoxPairs = QListWidget(self.sideMenu)
        self.listBoxPairs.setObjectName(u"listBoxPairs")

        self.verticalLayout.addWidget(self.listBoxPairs)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer)


        self.horizontalLayout.addWidget(self.sideMenu)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"PDF Editor mit resizbaren Box-Overlays", None))
        self.btnLoadPDF.setText(QCoreApplication.translate("MainWindow", u"PDF laden", None))
        self.btnAddBoxPair.setText(QCoreApplication.translate("MainWindow", u"+", None))
        self.btnRemoveBoxPair.setText(QCoreApplication.translate("MainWindow", u"-", None))
        self.btnZoomIn.setText(QCoreApplication.translate("MainWindow", u"Zoom +", None))
        self.btnZoomOut.setText(QCoreApplication.translate("MainWindow", u"Zoom -", None))
        self.btnAddSingleBox.setText(QCoreApplication.translate("MainWindow", u"Single Box +", None))
        self.btnSave.setText(QCoreApplication.translate("MainWindow", u"Speichern", None))
        self.btnLoad.setText(QCoreApplication.translate("MainWindow", u"Laden", None))
    # retranslateUi

