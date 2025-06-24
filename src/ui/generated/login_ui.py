# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'login.ui'
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
from PySide6.QtWidgets import (QApplication, QDialog, QFormLayout, QHBoxLayout,
    QLabel, QLineEdit, QSizePolicy, QSpacerItem,
    QToolButton, QVBoxLayout, QWidget)

class Ui_LoginDialog(object):
    def setupUi(self, LoginDialog):
        if not LoginDialog.objectName():
            LoginDialog.setObjectName(u"LoginDialog")
        LoginDialog.resize(217, 186)
        self.verticalLayout = QVBoxLayout(LoginDialog)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.formLayout = QFormLayout()
        self.formLayout.setObjectName(u"formLayout")
        self.labelHost = QLabel(LoginDialog)
        self.labelHost.setObjectName(u"labelHost")

        self.formLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.labelHost)

        self.lineEditHost = QLineEdit(LoginDialog)
        self.lineEditHost.setObjectName(u"lineEditHost")

        self.formLayout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.lineEditHost)

        self.labelPort = QLabel(LoginDialog)
        self.labelPort.setObjectName(u"labelPort")

        self.formLayout.setWidget(1, QFormLayout.ItemRole.LabelRole, self.labelPort)

        self.lineEditPort = QLineEdit(LoginDialog)
        self.lineEditPort.setObjectName(u"lineEditPort")

        self.formLayout.setWidget(1, QFormLayout.ItemRole.FieldRole, self.lineEditPort)

        self.labelUser = QLabel(LoginDialog)
        self.labelUser.setObjectName(u"labelUser")

        self.formLayout.setWidget(2, QFormLayout.ItemRole.LabelRole, self.labelUser)

        self.lineEditUser = QLineEdit(LoginDialog)
        self.lineEditUser.setObjectName(u"lineEditUser")

        self.formLayout.setWidget(2, QFormLayout.ItemRole.FieldRole, self.lineEditUser)

        self.labelPassword = QLabel(LoginDialog)
        self.labelPassword.setObjectName(u"labelPassword")

        self.formLayout.setWidget(3, QFormLayout.ItemRole.LabelRole, self.labelPassword)

        self.lineEditPassword = QLineEdit(LoginDialog)
        self.lineEditPassword.setObjectName(u"lineEditPassword")
        self.lineEditPassword.setEchoMode(QLineEdit.EchoMode.Password)

        self.formLayout.setWidget(3, QFormLayout.ItemRole.FieldRole, self.lineEditPassword)

        self.labelDatabase = QLabel(LoginDialog)
        self.labelDatabase.setObjectName(u"labelDatabase")

        self.formLayout.setWidget(4, QFormLayout.ItemRole.LabelRole, self.labelDatabase)

        self.lineEditDatabase = QLineEdit(LoginDialog)
        self.lineEditDatabase.setObjectName(u"lineEditDatabase")

        self.formLayout.setWidget(4, QFormLayout.ItemRole.FieldRole, self.lineEditDatabase)


        self.verticalLayout.addLayout(self.formLayout)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.toolButton = QToolButton(LoginDialog)
        self.toolButton.setObjectName(u"toolButton")

        self.horizontalLayout.addWidget(self.toolButton)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.toolButtonLogin = QToolButton(LoginDialog)
        self.toolButtonLogin.setObjectName(u"toolButtonLogin")

        self.horizontalLayout.addWidget(self.toolButtonLogin)


        self.verticalLayout.addLayout(self.horizontalLayout)


        self.retranslateUi(LoginDialog)

        QMetaObject.connectSlotsByName(LoginDialog)
    # setupUi

    def retranslateUi(self, LoginDialog):
        LoginDialog.setWindowTitle(QCoreApplication.translate("LoginDialog", u"Login - Flohmarktmanager", None))
        LoginDialog.setStyleSheet(QCoreApplication.translate("LoginDialog", u"QWidget { font-family: \"Segoe UI\", sans-serif; font-size: 10pt; background-color: #f0f0f0; }\n"
"QPushButton { border: none; padding: 6px 12px; border-radius: 4px; background-color: #0078d7; color: white; }\n"
"QPushButton:hover { background-color: #005a9e; }\n"
"QGroupBox { border: 1px solid #cccccc; border-radius: 4px; margin-top: 6px; }\n"
"QGroupBox::title { subcontrol-origin: margin; subcontrol-position: top left; padding: 0 6px; }", None))
        self.labelHost.setText(QCoreApplication.translate("LoginDialog", u"Host:", None))
        self.labelPort.setText(QCoreApplication.translate("LoginDialog", u"Port:", None))
        self.labelUser.setText(QCoreApplication.translate("LoginDialog", u"Benutzer:", None))
        self.labelPassword.setText(QCoreApplication.translate("LoginDialog", u"Passwort:", None))
        self.labelDatabase.setText(QCoreApplication.translate("LoginDialog", u"Datenbank:", None))
        self.toolButton.setText(QCoreApplication.translate("LoginDialog", u"...", None))
        self.toolButtonLogin.setText(QCoreApplication.translate("LoginDialog", u"Einloggen", None))
    # retranslateUi

