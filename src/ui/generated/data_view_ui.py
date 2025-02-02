# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'data_view.ui'
##
## Created by: Qt User Interface Compiler version 6.8.1
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
    QSizePolicy, QSplitter, QTableWidget, QTableWidgetItem,
    QTreeWidget, QTreeWidgetItem, QVBoxLayout, QWidget)

class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(888, 690)
        self.horizontalLayout = QHBoxLayout(Form)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.splitter = QSplitter(Form)
        self.splitter.setObjectName(u"splitter")
        self.splitter.setOrientation(Qt.Horizontal)
        self.leftWidget = QWidget(self.splitter)
        self.leftWidget.setObjectName(u"leftWidget")
        self.verticalLayoutLeft = QVBoxLayout(self.leftWidget)
        self.verticalLayoutLeft.setObjectName(u"verticalLayoutLeft")
        self.verticalLayoutLeft.setContentsMargins(0, 0, 0, 0)
        self.btnToggleView = QPushButton(self.leftWidget)
        self.btnToggleView.setObjectName(u"btnToggleView")

        self.verticalLayoutLeft.addWidget(self.btnToggleView)

        self.treeUsers = QTreeWidget(self.leftWidget)
        __qtreewidgetitem = QTreeWidgetItem()
        __qtreewidgetitem.setText(0, u"1");
        self.treeUsers.setHeaderItem(__qtreewidgetitem)
        self.treeUsers.setObjectName(u"treeUsers")

        self.verticalLayoutLeft.addWidget(self.treeUsers)

        self.splitter.addWidget(self.leftWidget)
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

        self.horizontalLayout.addWidget(self.splitter)


        self.retranslateUi(Form)

        QMetaObject.connectSlotsByName(Form)
    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"Form", None))
        self.btnToggleView.setText(QCoreApplication.translate("Form", u"Ansicht umschalten", None))
        self.treeUsers.setProperty(u"headerLabels", [
            QCoreApplication.translate("Form", u"Benutzer", None)])
        self.tableEntries.setProperty(u"horizontalHeaderLabels", [
            QCoreApplication.translate("Form", u"Artikelnummer", None),
            QCoreApplication.translate("Form", u"Beschreibung", None),
            QCoreApplication.translate("Form", u"Gr\u00f6\u00dfe", None),
            QCoreApplication.translate("Form", u"Preis", None),
            QCoreApplication.translate("Form", u"Datum", None)])
    # retranslateUi

