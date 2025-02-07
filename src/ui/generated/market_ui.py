# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'market.ui'
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
from PySide6.QtWidgets import (QApplication, QSizePolicy, QTabWidget, QVBoxLayout,
    QWidget)

class Ui_marketDialog(object):
    def setupUi(self, marketDialog):
        if not marketDialog.objectName():
            marketDialog.setObjectName(u"marketDialog")
        marketDialog.resize(701, 625)
        self.verticalLayout = QVBoxLayout(marketDialog)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.tabWidget = QTabWidget(marketDialog)
        self.tabWidget.setObjectName(u"tabWidget")
        self.tab = QWidget()
        self.tab.setObjectName(u"tab")
        self.tabWidget.addTab(self.tab, "")
        self.tab_3 = QWidget()
        self.tab_3.setObjectName(u"tab_3")
        self.tabWidget.addTab(self.tab_3, "")
        self.tab_2 = QWidget()
        self.tab_2.setObjectName(u"tab_2")
        self.tabWidget.addTab(self.tab_2, "")

        self.verticalLayout.addWidget(self.tabWidget)


        self.retranslateUi(marketDialog)

        self.tabWidget.setCurrentIndex(1)


        QMetaObject.connectSlotsByName(marketDialog)
    # setupUi

    def retranslateUi(self, marketDialog):
        marketDialog.setWindowTitle(QCoreApplication.translate("marketDialog", u"Form", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), QCoreApplication.translate("marketDialog", u"Markt Einstellungen", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_3), QCoreApplication.translate("marketDialog", u"Benutzerinformationen", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), QCoreApplication.translate("marketDialog", u"Verkaufslisten", None))
    # retranslateUi

