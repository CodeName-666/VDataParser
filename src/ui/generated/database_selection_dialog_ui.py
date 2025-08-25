# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'database_selection_dialog.ui'
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
from PySide6.QtWidgets import (QAbstractButton, QApplication, QDialog, QDialogButtonBox,
    QListWidget, QListWidgetItem, QSizePolicy, QVBoxLayout,
    QWidget)

class Ui_DatabaseSelectionDialog(object):
    def setupUi(self, DatabaseSelectionDialog):
        if not DatabaseSelectionDialog.objectName():
            DatabaseSelectionDialog.setObjectName(u"DatabaseSelectionDialog")
        self.verticalLayout = QVBoxLayout(DatabaseSelectionDialog)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.databaseList = QListWidget(DatabaseSelectionDialog)
        self.databaseList.setObjectName(u"databaseList")

        self.verticalLayout.addWidget(self.databaseList)

        self.buttonBox = QDialogButtonBox(DatabaseSelectionDialog)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)

        self.verticalLayout.addWidget(self.buttonBox)


        self.retranslateUi(DatabaseSelectionDialog)

        QMetaObject.connectSlotsByName(DatabaseSelectionDialog)
    # setupUi

    def retranslateUi(self, DatabaseSelectionDialog):
        DatabaseSelectionDialog.setWindowTitle(QCoreApplication.translate("DatabaseSelectionDialog", u"Datenbank ausw\u00e4hlen", None))
    # retranslateUi

