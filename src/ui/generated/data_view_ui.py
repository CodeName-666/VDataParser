# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'data_view.ui'
##
## Created by: Qt User Interface Compiler version 6.6.1
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
from PySide6.QtWidgets import (QApplication, QHBoxLayout, QHeaderView, QPushButton,
    QSizePolicy, QSpacerItem, QSplitter, QTableWidget,
    QTableWidgetItem, QTreeWidget, QTreeWidgetItem, QVBoxLayout,
    QWidget)

class Ui_DataView(object):
    def setupUi(self, DataView):
        if not DataView.objectName():
            DataView.setObjectName(u"DataView")
        DataView.resize(888, 690)
        self.horizontalLayout_2 = QHBoxLayout(DataView)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.splitter = QSplitter(DataView)
        self.splitter.setObjectName(u"splitter")
        self.splitter.setOrientation(Qt.Orientation.Horizontal)
        self.layoutWidget = QWidget(self.splitter)
        self.layoutWidget.setObjectName(u"layoutWidget")
        self.verticalLayoutLeft = QVBoxLayout(self.layoutWidget)
        self.verticalLayoutLeft.setObjectName(u"verticalLayoutLeft")
        self.verticalLayoutLeft.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.btnToggleView = QPushButton(self.layoutWidget)
        self.btnToggleView.setObjectName(u"btnToggleView")

        self.horizontalLayout.addWidget(self.btnToggleView)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)


        self.verticalLayoutLeft.addLayout(self.horizontalLayout)

        self.treeUsers = QTreeWidget(self.layoutWidget)
        __qtreewidgetitem = QTreeWidgetItem()
        __qtreewidgetitem.setText(0, u"1");
        self.treeUsers.setHeaderItem(__qtreewidgetitem)
        self.treeUsers.setObjectName(u"treeUsers")

        self.verticalLayoutLeft.addWidget(self.treeUsers)

        self.splitter.addWidget(self.layoutWidget)
        self.rightWidget = QWidget(self.splitter)
        self.rightWidget.setObjectName(u"rightWidget")
        self.verticalLayoutRight = QVBoxLayout(self.rightWidget)
        self.verticalLayoutRight.setObjectName(u"verticalLayoutRight")
        self.verticalLayoutRight.setContentsMargins(0, 0, 0, 0)
        self.tableEntries = QTableWidget(self.rightWidget)
        if (self.tableEntries.columnCount() < 5):
            self.tableEntries.setColumnCount(5)
        self.tableEntries.setObjectName(u"tableEntries")
        self.tableEntries.setColumnCount(5)

        self.verticalLayoutRight.addWidget(self.tableEntries)

        self.splitter.addWidget(self.rightWidget)

        self.horizontalLayout_2.addWidget(self.splitter)


        self.retranslateUi(DataView)

        QMetaObject.connectSlotsByName(DataView)
    # setupUi

    def retranslateUi(self, DataView):
        DataView.setWindowTitle(QCoreApplication.translate("DataView", u"Form", None))
        DataView.setStyleSheet(QCoreApplication.translate("DataView", u"QWidget { font-family: \"Segoe UI\", sans-serif; font-size: 10pt; background-color: #f0f0f0; }\n"
"QPushButton { border: none; padding: 6px 12px; border-radius: 4px; background-color: #0078d7; color: white; }\n"
"QPushButton:hover { background-color: #005a9e; }\n"
"QGroupBox { border: 1px solid #cccccc; border-radius: 4px; margin-top: 6px; }\n"
"QGroupBox::title { subcontrol-origin: margin; subcontrol-position: top left; padding: 0 6px; }", None))
        self.btnToggleView.setText(QCoreApplication.translate("DataView", u"Ansicht umschalten", None))
        self.treeUsers.setProperty("headerLabels", [
            QCoreApplication.translate("DataView", u"Benutzer", None)])
        self.tableEntries.setProperty("horizontalHeaderLabels", [
            QCoreApplication.translate("DataView", u"Artikelnummer", None),
            QCoreApplication.translate("DataView", u"Beschreibung", None),
            QCoreApplication.translate("DataView", u"Gr\u00f6\u00dfe", None),
            QCoreApplication.translate("DataView", u"Preis", None),
            QCoreApplication.translate("DataView", u"Datum", None)])
    # retranslateUi

