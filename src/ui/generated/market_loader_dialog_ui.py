# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'market_loader_dialog.ui'
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
from PySide6.QtWidgets import (QApplication, QDialog, QFormLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QRadioButton,
    QSizePolicy, QSpacerItem, QVBoxLayout, QWidget)

class Ui_MarketLoaderDialog(object):
    def setupUi(self, MarketLoaderDialog):
        if not MarketLoaderDialog.objectName():
            MarketLoaderDialog.setObjectName(u"MarketLoaderDialog")
        MarketLoaderDialog.resize(321, 270)
        self.verticalLayout = QVBoxLayout(MarketLoaderDialog)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.jsonRadio = QRadioButton(MarketLoaderDialog)
        self.jsonRadio.setObjectName(u"jsonRadio")
        self.jsonRadio.setChecked(True)

        self.verticalLayout.addWidget(self.jsonRadio)

        self.jsonHBox = QHBoxLayout()
        self.jsonHBox.setObjectName(u"jsonHBox")
        self.labelJson = QLabel(MarketLoaderDialog)
        self.labelJson.setObjectName(u"labelJson")

        self.jsonHBox.addWidget(self.labelJson)

        self.jsonPathEdit = QLineEdit(MarketLoaderDialog)
        self.jsonPathEdit.setObjectName(u"jsonPathEdit")

        self.jsonHBox.addWidget(self.jsonPathEdit)

        self.browseJsonBtn = QPushButton(MarketLoaderDialog)
        self.browseJsonBtn.setObjectName(u"browseJsonBtn")

        self.jsonHBox.addWidget(self.browseJsonBtn)


        self.verticalLayout.addLayout(self.jsonHBox)

        self.mysqlRadio = QRadioButton(MarketLoaderDialog)
        self.mysqlRadio.setObjectName(u"mysqlRadio")

        self.verticalLayout.addWidget(self.mysqlRadio)

        self.formLayout = QFormLayout()
        self.formLayout.setObjectName(u"formLayout")
        self.labelHost = QLabel(MarketLoaderDialog)
        self.labelHost.setObjectName(u"labelHost")

        self.formLayout.setWidget(0, QFormLayout.LabelRole, self.labelHost)

        self.hostEdit = QLineEdit(MarketLoaderDialog)
        self.hostEdit.setObjectName(u"hostEdit")

        self.formLayout.setWidget(0, QFormLayout.FieldRole, self.hostEdit)

        self.labelPort = QLabel(MarketLoaderDialog)
        self.labelPort.setObjectName(u"labelPort")

        self.formLayout.setWidget(1, QFormLayout.LabelRole, self.labelPort)

        self.portEdit = QLineEdit(MarketLoaderDialog)
        self.portEdit.setObjectName(u"portEdit")

        self.formLayout.setWidget(1, QFormLayout.FieldRole, self.portEdit)

        self.labelDatabase = QLabel(MarketLoaderDialog)
        self.labelDatabase.setObjectName(u"labelDatabase")

        self.formLayout.setWidget(2, QFormLayout.LabelRole, self.labelDatabase)

        self.dbEdit = QLineEdit(MarketLoaderDialog)
        self.dbEdit.setObjectName(u"dbEdit")

        self.formLayout.setWidget(2, QFormLayout.FieldRole, self.dbEdit)

        self.labelUser = QLabel(MarketLoaderDialog)
        self.labelUser.setObjectName(u"labelUser")

        self.formLayout.setWidget(3, QFormLayout.LabelRole, self.labelUser)

        self.userEdit = QLineEdit(MarketLoaderDialog)
        self.userEdit.setObjectName(u"userEdit")

        self.formLayout.setWidget(3, QFormLayout.FieldRole, self.userEdit)

        self.labelPassword = QLabel(MarketLoaderDialog)
        self.labelPassword.setObjectName(u"labelPassword")

        self.formLayout.setWidget(4, QFormLayout.LabelRole, self.labelPassword)

        self.pwEdit = QLineEdit(MarketLoaderDialog)
        self.pwEdit.setObjectName(u"pwEdit")
        self.pwEdit.setEchoMode(QLineEdit.EchoMode.Password)

        self.formLayout.setWidget(4, QFormLayout.FieldRole, self.pwEdit)


        self.verticalLayout.addLayout(self.formLayout)

        self.buttonLayout = QHBoxLayout()
        self.buttonLayout.setObjectName(u"buttonLayout")
        self.hSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.buttonLayout.addItem(self.hSpacer)

        self.okBtn = QPushButton(MarketLoaderDialog)
        self.okBtn.setObjectName(u"okBtn")

        self.buttonLayout.addWidget(self.okBtn)

        self.cancelBtn = QPushButton(MarketLoaderDialog)
        self.cancelBtn.setObjectName(u"cancelBtn")

        self.buttonLayout.addWidget(self.cancelBtn)


        self.verticalLayout.addLayout(self.buttonLayout)


        self.retranslateUi(MarketLoaderDialog)

        self.okBtn.setDefault(True)


        QMetaObject.connectSlotsByName(MarketLoaderDialog)
    # setupUi

    def retranslateUi(self, MarketLoaderDialog):
        MarketLoaderDialog.setWindowTitle(QCoreApplication.translate("MarketLoaderDialog", u"Markt laden", None))
        MarketLoaderDialog.setStyleSheet(QCoreApplication.translate("MarketLoaderDialog", u"QWidget { font-family: \"Segoe UI\", sans-serif; font-size: 10pt; background-color: #f0f0f0; }\n"
"QPushButton { border: none; padding: 6px 12px; border-radius: 4px; background-color: #0078d7; color: white; }\n"
"QPushButton:hover { background-color: #005a9e; }\n"
"QGroupBox { border: 1px solid #cccccc; border-radius: 4px; margin-top: 6px; }\n"
"QGroupBox::title { subcontrol-origin: margin; subcontrol-position: top left; padding: 0 6px; }", None))
        self.jsonRadio.setText(QCoreApplication.translate("MarketLoaderDialog", u"Projektdatei verwenden", None))
        self.labelJson.setText(QCoreApplication.translate("MarketLoaderDialog", u"Projektdatei:", None))
        self.browseJsonBtn.setText(QCoreApplication.translate("MarketLoaderDialog", u"Durchsuchen \u2026", None))
        self.mysqlRadio.setText(QCoreApplication.translate("MarketLoaderDialog", u"Direkte MySQL-Verbindung", None))
        self.labelHost.setText(QCoreApplication.translate("MarketLoaderDialog", u"Host:", None))
        self.hostEdit.setText(QCoreApplication.translate("MarketLoaderDialog", u"localhost", None))
        self.labelPort.setText(QCoreApplication.translate("MarketLoaderDialog", u"Port:", None))
        self.portEdit.setText(QCoreApplication.translate("MarketLoaderDialog", u"3306", None))
        self.labelDatabase.setText(QCoreApplication.translate("MarketLoaderDialog", u"Datenbank:", None))
        self.labelUser.setText(QCoreApplication.translate("MarketLoaderDialog", u"Benutzer:", None))
        self.labelPassword.setText(QCoreApplication.translate("MarketLoaderDialog", u"Passwort:", None))
        self.okBtn.setText(QCoreApplication.translate("MarketLoaderDialog", u"OK", None))
        self.cancelBtn.setText(QCoreApplication.translate("MarketLoaderDialog", u"Abbrechen", None))
    # retranslateUi

