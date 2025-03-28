# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'about.ui'
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
from PySide6.QtWidgets import (QAbstractButton, QApplication, QDialog, QDialogButtonBox,
    QFrame, QHBoxLayout, QLabel, QSizePolicy,
    QVBoxLayout, QWidget)

class Ui_AboutDialog(object):
    def setupUi(self, AboutDialog):
        if not AboutDialog.objectName():
            AboutDialog.setObjectName(u"AboutDialog")
        AboutDialog.resize(600, 383)
        self.verticalLayoutMain = QVBoxLayout(AboutDialog)
        self.verticalLayoutMain.setObjectName(u"verticalLayoutMain")
        self.horizontalLayoutTop = QHBoxLayout()
        self.horizontalLayoutTop.setObjectName(u"horizontalLayoutTop")
        self.labelLogo = QLabel(AboutDialog)
        self.labelLogo.setObjectName(u"labelLogo")
        self.labelLogo.setMinimumSize(QSize(64, 64))
        self.labelLogo.setMaximumSize(QSize(128, 128))
        self.labelLogo.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayoutTop.addWidget(self.labelLogo)

        self.verticalLayoutInfo = QVBoxLayout()
        self.verticalLayoutInfo.setObjectName(u"verticalLayoutInfo")
        self.labelToolName = QLabel(AboutDialog)
        self.labelToolName.setObjectName(u"labelToolName")
        font = QFont()
        font.setPointSize(14)
        font.setBold(True)
        self.labelToolName.setFont(font)
        self.labelToolName.setAlignment(Qt.AlignmentFlag.AlignLeading|Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignVCenter)

        self.verticalLayoutInfo.addWidget(self.labelToolName)

        self.labelVersion = QLabel(AboutDialog)
        self.labelVersion.setObjectName(u"labelVersion")
        self.labelVersion.setAlignment(Qt.AlignmentFlag.AlignLeading|Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignVCenter)

        self.verticalLayoutInfo.addWidget(self.labelVersion)

        self.labelDescription = QLabel(AboutDialog)
        self.labelDescription.setObjectName(u"labelDescription")
        self.labelDescription.setAlignment(Qt.AlignmentFlag.AlignLeading|Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignTop)
        self.labelDescription.setWordWrap(True)

        self.verticalLayoutInfo.addWidget(self.labelDescription)


        self.horizontalLayoutTop.addLayout(self.verticalLayoutInfo)


        self.verticalLayoutMain.addLayout(self.horizontalLayoutTop)

        self.line = QFrame(AboutDialog)
        self.line.setObjectName(u"line")
        self.line.setFrameShape(QFrame.Shape.HLine)
        self.line.setFrameShadow(QFrame.Shadow.Sunken)

        self.verticalLayoutMain.addWidget(self.line)

        self.verticalLayoutContact = QVBoxLayout()
        self.verticalLayoutContact.setObjectName(u"verticalLayoutContact")
        self.labelContactHeader = QLabel(AboutDialog)
        self.labelContactHeader.setObjectName(u"labelContactHeader")
        font1 = QFont()
        font1.setBold(True)
        self.labelContactHeader.setFont(font1)

        self.verticalLayoutContact.addWidget(self.labelContactHeader)

        self.labelEmail = QLabel(AboutDialog)
        self.labelEmail.setObjectName(u"labelEmail")
        self.labelEmail.setOpenExternalLinks(True)

        self.verticalLayoutContact.addWidget(self.labelEmail)

        self.labelWebsite = QLabel(AboutDialog)
        self.labelWebsite.setObjectName(u"labelWebsite")
        self.labelWebsite.setWordWrap(True)
        self.labelWebsite.setOpenExternalLinks(True)

        self.verticalLayoutContact.addWidget(self.labelWebsite)


        self.verticalLayoutMain.addLayout(self.verticalLayoutContact)

        self.buttonBox = QDialogButtonBox(AboutDialog)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setOrientation(Qt.Orientation.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.StandardButton.Close)

        self.verticalLayoutMain.addWidget(self.buttonBox)


        self.retranslateUi(AboutDialog)
        self.buttonBox.clicked.connect(AboutDialog.close)

        QMetaObject.connectSlotsByName(AboutDialog)
    # setupUi

    def retranslateUi(self, AboutDialog):
        AboutDialog.setWindowTitle(QCoreApplication.translate("AboutDialog", u"\u00dcber MeinTool", None))
        self.labelLogo.setText("")
        self.labelToolName.setText(QCoreApplication.translate("AboutDialog", u"MeinTool", None))
        self.labelVersion.setText(QCoreApplication.translate("AboutDialog", u"Version 1.0.0", None))
        self.labelDescription.setText(QCoreApplication.translate("AboutDialog", u"MeinTool ist ein gro\u00dfartiges Werkzeug, um XYZ zu erledigen.", None))
        self.labelContactHeader.setText(QCoreApplication.translate("AboutDialog", u"Kontakt", None))
        self.labelEmail.setText(QCoreApplication.translate("AboutDialog", u"Email: info@meintool.de", None))
        self.labelWebsite.setText(QCoreApplication.translate("AboutDialog", u"Website: <a href=\"https://www.meintool.de\">https://www.meintool.de</a>", None))
    # retranslateUi

