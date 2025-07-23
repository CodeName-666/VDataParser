# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'output_window.ui'
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
from PySide6.QtWidgets import (QApplication, QListWidget, QListWidgetItem, QProgressBar,
    QSizePolicy, QVBoxLayout, QWidget)

class Ui_OutputWindow(object):
    def setupUi(self, OutputWindow):
        if not OutputWindow.objectName():
            OutputWindow.setObjectName(u"OutputWindow")
        OutputWindow.resize(450, 350)
        self.verticalLayout = QVBoxLayout(OutputWindow)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.logOutputList = QListWidget(OutputWindow)
        self.logOutputList.setObjectName(u"logOutputList")

        self.verticalLayout.addWidget(self.logOutputList)

        self.progressBar = QProgressBar(OutputWindow)
        self.progressBar.setObjectName(u"progressBar")
        self.progressBar.setValue(0)
        self.progressBar.setMinimum(0)
        self.progressBar.setMaximum(100)
        self.progressBar.setTextVisible(True)
        self.progressBar.setAlignment(Qt.AlignCenter)

        self.verticalLayout.addWidget(self.progressBar)

        self.progressBar_2 = QProgressBar(OutputWindow)
        self.progressBar_2.setObjectName(u"progressBar_2")
        self.progressBar_2.setValue(0)
        self.progressBar_2.setMinimum(0)
        self.progressBar_2.setMaximum(100)
        self.progressBar_2.setTextVisible(True)
        self.progressBar_2.setAlignment(Qt.AlignCenter)

        self.verticalLayout.addWidget(self.progressBar_2)


        self.retranslateUi(OutputWindow)

        QMetaObject.connectSlotsByName(OutputWindow)
    # setupUi

    def retranslateUi(self, OutputWindow):
        OutputWindow.setWindowTitle(QCoreApplication.translate("OutputWindow", u"Print Ausgabe", None))
        OutputWindow.setStyleSheet(QCoreApplication.translate("OutputWindow", u"QWidget { font-family: \"Segoe UI\", sans-serif; font-size: 10pt; background-color: #f0f0f0; }\n"
"QPushButton { border: none; padding: 6px 12px; border-radius: 4px; background-color: #0078d7; color: white; }\n"
"QPushButton:hover { background-color: #005a9e; }\n"
"QGroupBox { border: 1px solid #cccccc; border-radius: 4px; margin-top: 6px; }\n"
"QGroupBox::title { subcontrol-origin: margin; subcontrol-position: top left; padding: 0 6px; }", None))
#if QT_CONFIG(tooltip)
        self.logOutputList.setToolTip(QCoreApplication.translate("OutputWindow", u"Zeigt die Ausgaben an", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.progressBar.setToolTip(QCoreApplication.translate("OutputWindow", u"Zeigt den Fortschritt der Ausgabe an", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.progressBar_2.setToolTip(QCoreApplication.translate("OutputWindow", u"Zeigt den Fortschritt der Ausgabe an (zweite Leiste)", None))
#endif // QT_CONFIG(tooltip)
    # retranslateUi

