# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'market_setting.ui'
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
from PySide6.QtWidgets import (QApplication, QCheckBox, QDateEdit, QDateTimeEdit,
    QDialog, QFormLayout, QGroupBox, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QRadioButton,
    QSizePolicy, QSpacerItem, QSpinBox, QVBoxLayout,
    QWidget)

class Ui_MarketConfigDialog(object):
    def setupUi(self, MarketConfigDialog):
        if not MarketConfigDialog.objectName():
            MarketConfigDialog.setObjectName(u"MarketConfigDialog")
        MarketConfigDialog.resize(666, 500)
        self.verticalLayout = QVBoxLayout(MarketConfigDialog)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.titleLabel = QLabel(MarketConfigDialog)
        self.titleLabel.setObjectName(u"titleLabel")
        self.titleLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout.addWidget(self.titleLabel)

        self.modeGroupBox = QGroupBox(MarketConfigDialog)
        self.modeGroupBox.setObjectName(u"modeGroupBox")
        self.horizontalLayout_mode = QHBoxLayout(self.modeGroupBox)
        self.horizontalLayout_mode.setObjectName(u"horizontalLayout_mode")
        self.radioActiveFlohmarkt = QRadioButton(self.modeGroupBox)
        self.radioActiveFlohmarkt.setObjectName(u"radioActiveFlohmarkt")

        self.horizontalLayout_mode.addWidget(self.radioActiveFlohmarkt)

        self.radioDisbaledFlohmarkt = QRadioButton(self.modeGroupBox)
        self.radioDisbaledFlohmarkt.setObjectName(u"radioDisbaledFlohmarkt")
        self.radioDisbaledFlohmarkt.setChecked(True)

        self.horizontalLayout_mode.addWidget(self.radioDisbaledFlohmarkt)


        self.verticalLayout.addWidget(self.modeGroupBox)

        self.formLayout = QFormLayout()
        self.formLayout.setObjectName(u"formLayout")
        self.labelMaxStammnummer = QLabel(MarketConfigDialog)
        self.labelMaxStammnummer.setObjectName(u"labelMaxStammnummer")

        self.formLayout.setWidget(0, QFormLayout.LabelRole, self.labelMaxStammnummer)

        self.spinMaxStammnummer = QSpinBox(MarketConfigDialog)
        self.spinMaxStammnummer.setObjectName(u"spinMaxStammnummer")
        self.spinMaxStammnummer.setMinimum(1)
        self.spinMaxStammnummer.setMaximum(10000)
        self.spinMaxStammnummer.setValue(250)

        self.formLayout.setWidget(0, QFormLayout.FieldRole, self.spinMaxStammnummer)

        self.labelMaxArtikel = QLabel(MarketConfigDialog)
        self.labelMaxArtikel.setObjectName(u"labelMaxArtikel")

        self.formLayout.setWidget(1, QFormLayout.LabelRole, self.labelMaxArtikel)

        self.spinMaxArtikel = QSpinBox(MarketConfigDialog)
        self.spinMaxArtikel.setObjectName(u"spinMaxArtikel")
        self.spinMaxArtikel.setMinimum(1)
        self.spinMaxArtikel.setMaximum(1000)
        self.spinMaxArtikel.setValue(40)

        self.formLayout.setWidget(1, QFormLayout.FieldRole, self.spinMaxArtikel)

        self.labelFlohmarktDatum = QLabel(MarketConfigDialog)
        self.labelFlohmarktDatum.setObjectName(u"labelFlohmarktDatum")

        self.formLayout.setWidget(2, QFormLayout.LabelRole, self.labelFlohmarktDatum)

        self.dateTimeEditFlohmarktCountDown = QDateTimeEdit(MarketConfigDialog)
        self.dateTimeEditFlohmarktCountDown.setObjectName(u"dateTimeEditFlohmarktCountDown")
        self.dateTimeEditFlohmarktCountDown.setDateTime(QDateTime(QDate(2000, 1, 1), QTime(0, 0, 0)))
        self.dateTimeEditFlohmarktCountDown.setCalendarPopup(True)

        self.formLayout.setWidget(2, QFormLayout.FieldRole, self.dateTimeEditFlohmarktCountDown)

        self.labelFlohmarkt = QLabel(MarketConfigDialog)
        self.labelFlohmarkt.setObjectName(u"labelFlohmarkt")

        self.formLayout.setWidget(3, QFormLayout.LabelRole, self.labelFlohmarkt)

        self.labelFlohmarktNummer = QLabel(MarketConfigDialog)
        self.labelFlohmarktNummer.setObjectName(u"labelFlohmarktNummer")

        self.formLayout.setWidget(4, QFormLayout.LabelRole, self.labelFlohmarktNummer)

        self.spinFlohmarktNummer = QSpinBox(MarketConfigDialog)
        self.spinFlohmarktNummer.setObjectName(u"spinFlohmarktNummer")
        self.spinFlohmarktNummer.setMinimum(1)
        self.spinFlohmarktNummer.setMaximum(100)
        self.spinFlohmarktNummer.setValue(5)

        self.formLayout.setWidget(4, QFormLayout.FieldRole, self.spinFlohmarktNummer)

        self.labelPwLength = QLabel(MarketConfigDialog)
        self.labelPwLength.setObjectName(u"labelPwLength")

        self.formLayout.setWidget(5, QFormLayout.LabelRole, self.labelPwLength)

        self.spinPwLength = QSpinBox(MarketConfigDialog)
        self.spinPwLength.setObjectName(u"spinPwLength")
        self.spinPwLength.setMinimum(1)
        self.spinPwLength.setMaximum(50)
        self.spinPwLength.setValue(10)

        self.formLayout.setWidget(5, QFormLayout.FieldRole, self.spinPwLength)

        self.labelTabellePrefix = QLabel(MarketConfigDialog)
        self.labelTabellePrefix.setObjectName(u"labelTabellePrefix")

        self.formLayout.setWidget(6, QFormLayout.LabelRole, self.labelTabellePrefix)

        self.lineEditTabellePrefix = QLineEdit(MarketConfigDialog)
        self.lineEditTabellePrefix.setObjectName(u"lineEditTabellePrefix")

        self.formLayout.setWidget(6, QFormLayout.FieldRole, self.lineEditTabellePrefix)

        self.labelTabelleVerkaeufer = QLabel(MarketConfigDialog)
        self.labelTabelleVerkaeufer.setObjectName(u"labelTabelleVerkaeufer")

        self.formLayout.setWidget(7, QFormLayout.LabelRole, self.labelTabelleVerkaeufer)

        self.lineEditTabelleVerkaeufer = QLineEdit(MarketConfigDialog)
        self.lineEditTabelleVerkaeufer.setObjectName(u"lineEditTabelleVerkaeufer")

        self.formLayout.setWidget(7, QFormLayout.FieldRole, self.lineEditTabelleVerkaeufer)

        self.labelMaxIdPerUser = QLabel(MarketConfigDialog)
        self.labelMaxIdPerUser.setObjectName(u"labelMaxIdPerUser")

        self.formLayout.setWidget(8, QFormLayout.LabelRole, self.labelMaxIdPerUser)

        self.spinMaxIdPerUser = QSpinBox(MarketConfigDialog)
        self.spinMaxIdPerUser.setObjectName(u"spinMaxIdPerUser")
        self.spinMaxIdPerUser.setMinimum(1)
        self.spinMaxIdPerUser.setMaximum(100)
        self.spinMaxIdPerUser.setValue(8)

        self.formLayout.setWidget(8, QFormLayout.FieldRole, self.spinMaxIdPerUser)

        self.checkBoxLoginDisable = QCheckBox(MarketConfigDialog)
        self.checkBoxLoginDisable.setObjectName(u"checkBoxLoginDisable")
        self.checkBoxLoginDisable.setChecked(False)

        self.formLayout.setWidget(9, QFormLayout.SpanningRole, self.checkBoxLoginDisable)

        self.dateTimeEditFlohmarkt = QDateEdit(MarketConfigDialog)
        self.dateTimeEditFlohmarkt.setObjectName(u"dateTimeEditFlohmarkt")
        self.dateTimeEditFlohmarkt.setCalendarPopup(True)

        self.formLayout.setWidget(3, QFormLayout.FieldRole, self.dateTimeEditFlohmarkt)


        self.verticalLayout.addLayout(self.formLayout)

        self.buttonLayout = QHBoxLayout()
        self.buttonLayout.setObjectName(u"buttonLayout")
        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.buttonLayout.addItem(self.horizontalSpacer)

        self.buttonSave = QPushButton(MarketConfigDialog)
        self.buttonSave.setObjectName(u"buttonSave")

        self.buttonLayout.addWidget(self.buttonSave)

        self.buttonCancel = QPushButton(MarketConfigDialog)
        self.buttonCancel.setObjectName(u"buttonCancel")

        self.buttonLayout.addWidget(self.buttonCancel)


        self.verticalLayout.addLayout(self.buttonLayout)


        self.retranslateUi(MarketConfigDialog)

        QMetaObject.connectSlotsByName(MarketConfigDialog)
    # setupUi

    def retranslateUi(self, MarketConfigDialog):
        MarketConfigDialog.setWindowTitle(QCoreApplication.translate("MarketConfigDialog", u"Markt-Konfiguration", None))
        self.titleLabel.setText(QCoreApplication.translate("MarketConfigDialog", u"<h2>Markt-Konfiguration</h2>", None))
        self.modeGroupBox.setTitle(QCoreApplication.translate("MarketConfigDialog", u"Modus", None))
        self.radioActiveFlohmarkt.setText(QCoreApplication.translate("MarketConfigDialog", u"Flohmarkt Aktivieren", None))
        self.radioDisbaledFlohmarkt.setText(QCoreApplication.translate("MarketConfigDialog", u"Flohmarkt Deaktivieren", None))
        self.labelMaxStammnummer.setText(QCoreApplication.translate("MarketConfigDialog", u"Max. Stammnummern:", None))
        self.labelMaxArtikel.setText(QCoreApplication.translate("MarketConfigDialog", u"Max. Artikel:", None))
        self.labelFlohmarktDatum.setText(QCoreApplication.translate("MarketConfigDialog", u"Flohmarkt CountDown", None))
        self.dateTimeEditFlohmarktCountDown.setDisplayFormat(QCoreApplication.translate("MarketConfigDialog", u"yyyy-MM-dd HH:mm:ss", None))
        self.labelFlohmarkt.setText(QCoreApplication.translate("MarketConfigDialog", u"Flohmarkt Start:", None))
        self.labelFlohmarktNummer.setText(QCoreApplication.translate("MarketConfigDialog", u"Flohmarkt Nummer:", None))
        self.labelPwLength.setText(QCoreApplication.translate("MarketConfigDialog", u"Passwortl\u00e4nge:", None))
        self.labelTabellePrefix.setText(QCoreApplication.translate("MarketConfigDialog", u"Tabellen-Prefix:", None))
        self.lineEditTabellePrefix.setText(QCoreApplication.translate("MarketConfigDialog", u"stnr", None))
        self.labelTabelleVerkaeufer.setText(QCoreApplication.translate("MarketConfigDialog", u"Tabelle Verk\u00e4ufer:", None))
        self.lineEditTabelleVerkaeufer.setText(QCoreApplication.translate("MarketConfigDialog", u"verkaeufer", None))
        self.labelMaxIdPerUser.setText(QCoreApplication.translate("MarketConfigDialog", u"Max. ID pro User:", None))
        self.checkBoxLoginDisable.setText(QCoreApplication.translate("MarketConfigDialog", u"Login deaktivieren", None))
        self.buttonSave.setText(QCoreApplication.translate("MarketConfigDialog", u"Speichern", None))
        self.buttonCancel.setText(QCoreApplication.translate("MarketConfigDialog", u"Abbrechen", None))
    # retranslateUi

