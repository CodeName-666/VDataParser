# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'user_info.ui'
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
from PySide6.QtWidgets import (QApplication, QCheckBox, QFormLayout, QGroupBox,
    QHBoxLayout, QHeaderView, QLabel, QListWidget,
    QListWidgetItem, QSizePolicy, QTableWidget, QTableWidgetItem,
    QVBoxLayout, QWidget)

class Ui_MainWindowWidget(object):
    def setupUi(self, MainWindowWidget):
        if not MainWindowWidget.objectName():
            MainWindowWidget.setObjectName(u"MainWindowWidget")
        MainWindowWidget.resize(381, 238)
        self.horizontalLayout = QHBoxLayout(MainWindowWidget)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.verticalLayoutLeft = QVBoxLayout()
        self.verticalLayoutLeft.setObjectName(u"verticalLayoutLeft")
        self.checkboxUnique = QCheckBox(MainWindowWidget)
        self.checkboxUnique.setObjectName(u"checkboxUnique")
        self.checkboxUnique.setChecked(False)

        self.verticalLayoutLeft.addWidget(self.checkboxUnique)

        self.listWidgetUsers = QListWidget(MainWindowWidget)
        self.listWidgetUsers.setObjectName(u"listWidgetUsers")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.listWidgetUsers.sizePolicy().hasHeightForWidth())
        self.listWidgetUsers.setSizePolicy(sizePolicy)

        self.verticalLayoutLeft.addWidget(self.listWidgetUsers)


        self.horizontalLayout.addLayout(self.verticalLayoutLeft)

        self.groupBoxDetails = QGroupBox(MainWindowWidget)
        self.groupBoxDetails.setObjectName(u"groupBoxDetails")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.groupBoxDetails.sizePolicy().hasHeightForWidth())
        self.groupBoxDetails.setSizePolicy(sizePolicy1)
        self.formLayoutDetails = QFormLayout(self.groupBoxDetails)
        self.formLayoutDetails.setObjectName(u"formLayoutDetails")
        self.labelVorname = QLabel(self.groupBoxDetails)
        self.labelVorname.setObjectName(u"labelVorname")

        self.formLayoutDetails.setWidget(0, QFormLayout.ItemRole.LabelRole, self.labelVorname)

        self.valueVorname = QLabel(self.groupBoxDetails)
        self.valueVorname.setObjectName(u"valueVorname")

        self.formLayoutDetails.setWidget(0, QFormLayout.ItemRole.FieldRole, self.valueVorname)

        self.labelNachname = QLabel(self.groupBoxDetails)
        self.labelNachname.setObjectName(u"labelNachname")

        self.formLayoutDetails.setWidget(1, QFormLayout.ItemRole.LabelRole, self.labelNachname)

        self.valueNachname = QLabel(self.groupBoxDetails)
        self.valueNachname.setObjectName(u"valueNachname")

        self.formLayoutDetails.setWidget(1, QFormLayout.ItemRole.FieldRole, self.valueNachname)

        self.labelTelefon = QLabel(self.groupBoxDetails)
        self.labelTelefon.setObjectName(u"labelTelefon")

        self.formLayoutDetails.setWidget(2, QFormLayout.ItemRole.LabelRole, self.labelTelefon)

        self.valueTelefon = QLabel(self.groupBoxDetails)
        self.valueTelefon.setObjectName(u"valueTelefon")

        self.formLayoutDetails.setWidget(2, QFormLayout.ItemRole.FieldRole, self.valueTelefon)

        self.labelEmail = QLabel(self.groupBoxDetails)
        self.labelEmail.setObjectName(u"labelEmail")

        self.formLayoutDetails.setWidget(3, QFormLayout.ItemRole.LabelRole, self.labelEmail)

        self.valueEmail = QLabel(self.groupBoxDetails)
        self.valueEmail.setObjectName(u"valueEmail")

        self.formLayoutDetails.setWidget(3, QFormLayout.ItemRole.FieldRole, self.valueEmail)

        self.labelCreatedAt = QLabel(self.groupBoxDetails)
        self.labelCreatedAt.setObjectName(u"labelCreatedAt")

        self.formLayoutDetails.setWidget(4, QFormLayout.ItemRole.LabelRole, self.labelCreatedAt)

        self.valueCreatedAt = QLabel(self.groupBoxDetails)
        self.valueCreatedAt.setObjectName(u"valueCreatedAt")

        self.formLayoutDetails.setWidget(4, QFormLayout.ItemRole.FieldRole, self.valueCreatedAt)

        self.labelUpdatedAt = QLabel(self.groupBoxDetails)
        self.labelUpdatedAt.setObjectName(u"labelUpdatedAt")

        self.formLayoutDetails.setWidget(5, QFormLayout.ItemRole.LabelRole, self.labelUpdatedAt)

        self.valueUpdatedAt = QLabel(self.groupBoxDetails)
        self.valueUpdatedAt.setObjectName(u"valueUpdatedAt")

        self.formLayoutDetails.setWidget(5, QFormLayout.ItemRole.FieldRole, self.valueUpdatedAt)

        self.labelIDs = QLabel(self.groupBoxDetails)
        self.labelIDs.setObjectName(u"labelIDs")

        self.formLayoutDetails.setWidget(6, QFormLayout.ItemRole.LabelRole, self.labelIDs)

        self.tableIDs = QTableWidget(self.groupBoxDetails)
        if (self.tableIDs.columnCount() < 3):
            self.tableIDs.setColumnCount(3)
        self.tableIDs.setObjectName(u"tableIDs")
        self.tableIDs.setColumnCount(3)

        self.formLayoutDetails.setWidget(6, QFormLayout.ItemRole.FieldRole, self.tableIDs)


        self.horizontalLayout.addWidget(self.groupBoxDetails)


        self.retranslateUi(MainWindowWidget)

        QMetaObject.connectSlotsByName(MainWindowWidget)
    # setupUi

    def retranslateUi(self, MainWindowWidget):
        MainWindowWidget.setWindowTitle(QCoreApplication.translate("MainWindowWidget", u"Benutzer\u00fcbersicht", None))
        MainWindowWidget.setStyleSheet(QCoreApplication.translate("MainWindowWidget", u"QWidget { font-family: \"Segoe UI\", sans-serif; font-size: 11pt; background-color: #fafafa; color: #333; }\n"
"QPushButton { border: none; padding: 8px 16px; border-radius: 6px; background-color: #2d89ef; color: white; }\n"
"QPushButton:hover { background-color: #1b68c7; }\n"
"QGroupBox { border: 1px solid #d1d1d1; border-radius: 8px; margin-top: 8px; padding: 4px; }\n"
"QGroupBox::title { subcontrol-origin: margin; left: 8px; padding: 0 6px; font-weight: bold; }\n"
"QListWidget { background: white; border: 1px solid #d1d1d1; }\n"
"QTableWidget { background: white; gridline-color: #d1d1d1; }", None))
        self.checkboxUnique.setText(QCoreApplication.translate("MainWindowWidget", u"Eindeutige Benutzer anzeigen", None))
        self.groupBoxDetails.setTitle(QCoreApplication.translate("MainWindowWidget", u"Benutzerdetails", None))
        self.labelVorname.setText(QCoreApplication.translate("MainWindowWidget", u"Vorname:", None))
        self.valueVorname.setText("")
        self.valueVorname.setStyleSheet(QCoreApplication.translate("MainWindowWidget", u"font-weight: bold;", None))
        self.labelNachname.setText(QCoreApplication.translate("MainWindowWidget", u"Nachname:", None))
        self.valueNachname.setText("")
        self.valueNachname.setStyleSheet(QCoreApplication.translate("MainWindowWidget", u"font-weight: bold;", None))
        self.labelTelefon.setText(QCoreApplication.translate("MainWindowWidget", u"Telefon:", None))
        self.valueTelefon.setText("")
        self.valueTelefon.setStyleSheet(QCoreApplication.translate("MainWindowWidget", u"font-weight: bold;", None))
        self.labelEmail.setText(QCoreApplication.translate("MainWindowWidget", u"E-Mail:", None))
        self.valueEmail.setText("")
        self.valueEmail.setStyleSheet(QCoreApplication.translate("MainWindowWidget", u"font-weight: bold;", None))
        self.labelCreatedAt.setText(QCoreApplication.translate("MainWindowWidget", u"Created At:", None))
        self.valueCreatedAt.setText("")
        self.valueCreatedAt.setStyleSheet(QCoreApplication.translate("MainWindowWidget", u"font-weight: bold;", None))
        self.labelUpdatedAt.setText(QCoreApplication.translate("MainWindowWidget", u"Updated At:", None))
        self.valueUpdatedAt.setText("")
        self.valueUpdatedAt.setStyleSheet(QCoreApplication.translate("MainWindowWidget", u"font-weight: bold;", None))
        self.labelIDs.setText(QCoreApplication.translate("MainWindowWidget", u"IDs:", None))
        self.tableIDs.setProperty(u"horizontalHeaderLabels", [
            QCoreApplication.translate("MainWindowWidget", u"ID", None),
            QCoreApplication.translate("MainWindowWidget", u"Anzahl", None),
            QCoreApplication.translate("MainWindowWidget", u"Summe", None)])
    # retranslateUi

