# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'main_menu.ui'
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
from PySide6.QtWidgets import (QApplication, QGridLayout, QPushButton, QSizePolicy,
    QSpacerItem, QVBoxLayout, QWidget)

class Ui_MainMenuView(object):
    def setupUi(self, MainMenuView):
        if not MainMenuView.objectName():
            MainMenuView.setObjectName(u"MainMenuView")
        MainMenuView.resize(293, 359)
        self.gridLayout = QGridLayout(MainMenuView)
        self.gridLayout.setObjectName(u"gridLayout")
        self.verticalSpacer = QSpacerItem(20, 104, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.gridLayout.addItem(self.verticalSpacer, 0, 1, 1, 1)

        self.horizontalSpacer_2 = QSpacerItem(79, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout.addItem(self.horizontalSpacer_2, 1, 0, 1, 1)

        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.newButton = QPushButton(MainMenuView)
        self.newButton.setObjectName(u"newButton")

        self.verticalLayout.addWidget(self.newButton)

        self.loadButton = QPushButton(MainMenuView)
        self.loadButton.setObjectName(u"loadButton")

        self.verticalLayout.addWidget(self.loadButton)

        self.exportButton = QPushButton(MainMenuView)
        self.exportButton.setObjectName(u"exportButton")

        self.verticalLayout.addWidget(self.exportButton)

        self.exitButton = QPushButton(MainMenuView)
        self.exitButton.setObjectName(u"exitButton")

        self.verticalLayout.addWidget(self.exitButton)


        self.gridLayout.addLayout(self.verticalLayout, 1, 1, 1, 1)

        self.horizontalSpacer = QSpacerItem(78, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout.addItem(self.horizontalSpacer, 1, 2, 1, 1)

        self.verticalSpacer_2 = QSpacerItem(20, 103, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.gridLayout.addItem(self.verticalSpacer_2, 2, 1, 1, 1)


        self.retranslateUi(MainMenuView)

        QMetaObject.connectSlotsByName(MainMenuView)
    # setupUi

    def retranslateUi(self, MainMenuView):
        MainMenuView.setWindowTitle(QCoreApplication.translate("MainMenuView", u"Form", None))
        self.newButton.setText(QCoreApplication.translate("MainMenuView", u"    Neuer Markt    ", None))
        self.loadButton.setText(QCoreApplication.translate("MainMenuView", u"Markt Laden", None))
        self.exportButton.setText(QCoreApplication.translate("MainMenuView", u"    Export Daten Laden    ", None))
        self.exitButton.setText(QCoreApplication.translate("MainMenuView", u"Beenden", None))
    # retranslateUi

