# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'market.ui'
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
from PySide6.QtWidgets import (QApplication, QSizePolicy, QTabWidget, QVBoxLayout,
    QWidget)

class Ui_Market(object):
    def setupUi(self, Market):
        if not Market.objectName():
            Market.setObjectName(u"Market")
        Market.resize(701, 625)
        self.verticalLayout = QVBoxLayout(Market)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.tabWidget = QTabWidget(Market)
        self.tabWidget.setObjectName(u"tabWidget")
        self.tab_statistics = QWidget()
        self.tab_statistics.setObjectName(u"tab_statistics")
        self.tabWidget.addTab(self.tab_statistics, "")
        self.tab = QWidget()
        self.tab.setObjectName(u"tab")
        self.tabWidget.addTab(self.tab, "")
        self.tab_3 = QWidget()
        self.tab_3.setObjectName(u"tab_3")
        self.tabWidget.addTab(self.tab_3, "")
        self.tab_2 = QWidget()
        self.tab_2.setObjectName(u"tab_2")
        self.tabWidget.addTab(self.tab_2, "")
        self.tab_4 = QWidget()
        self.tab_4.setObjectName(u"tab_4")
        self.tabWidget.addTab(self.tab_4, "")

        self.verticalLayout.addWidget(self.tabWidget)


        self.retranslateUi(Market)

        self.tabWidget.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(Market)
    # setupUi

    def retranslateUi(self, Market):
        Market.setWindowTitle(QCoreApplication.translate("Market", u"Form", None))
        Market.setStyleSheet(QCoreApplication.translate("Market", u"QWidget { font-family: \"Segoe UI\", sans-serif; font-size: 10pt; background-color: #f0f0f0; }\n"
"QPushButton { border: none; padding: 6px 12px; border-radius: 4px; background-color: #0078d7; color: white; }\n"
"QPushButton:hover { background-color: #005a9e; }\n"
"QGroupBox { border: 1px solid #cccccc; border-radius: 4px; margin-top: 6px; }\n"
"QGroupBox::title { subcontrol-origin: margin; subcontrol-position: top left; padding: 0 6px; }", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_statistics), QCoreApplication.translate("Market", u"Statistik", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), QCoreApplication.translate("Market", u"Markt Einstellungen", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_3), QCoreApplication.translate("Market", u"Benutzerinformationen", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), QCoreApplication.translate("Market", u"Verkaufslisten", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_4), QCoreApplication.translate("Market", u"Abholbest\u00e4tigung", None))
    # retranslateUi

