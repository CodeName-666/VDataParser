# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'market_statistics.ui'
##
## Created by: Qt User Interface Compiler version 6.6.0
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
from PySide6.QtWidgets import (QApplication, QFormLayout, QGroupBox, QLabel,
    QSizePolicy, QVBoxLayout, QWidget)
from PySide6.QtCharts import QChartView

class Ui_MarketStatistics(object):
    def setupUi(self, MarketStatistics):
        if not MarketStatistics.objectName():
            MarketStatistics.setObjectName(u"MarketStatistics")
        MarketStatistics.resize(400, 300)
        self.verticalLayout = QVBoxLayout(MarketStatistics)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.groupBoxMainNumbers = QGroupBox(MarketStatistics)
        self.groupBoxMainNumbers.setObjectName(u"groupBoxMainNumbers")
        self.verticalLayoutMainNumbers = QVBoxLayout(self.groupBoxMainNumbers)
        self.verticalLayoutMainNumbers.setObjectName(u"verticalLayoutMainNumbers")
        self.chartMainNumbers = QChartView(self.groupBoxMainNumbers)
        self.chartMainNumbers.setObjectName(u"chartMainNumbers")

        self.verticalLayoutMainNumbers.addWidget(self.chartMainNumbers)

        self.formLayoutMainNumbers = QFormLayout()
        self.formLayoutMainNumbers.setObjectName(u"formLayoutMainNumbers")
        self.labelUsed = QLabel(self.groupBoxMainNumbers)
        self.labelUsed.setObjectName(u"labelUsed")

        self.formLayoutMainNumbers.setWidget(0, QFormLayout.LabelRole, self.labelUsed)

        self.valueUsed = QLabel(self.groupBoxMainNumbers)
        self.valueUsed.setObjectName(u"valueUsed")

        self.formLayoutMainNumbers.setWidget(0, QFormLayout.FieldRole, self.valueUsed)

        self.labelFree = QLabel(self.groupBoxMainNumbers)
        self.labelFree.setObjectName(u"labelFree")

        self.formLayoutMainNumbers.setWidget(1, QFormLayout.LabelRole, self.labelFree)

        self.valueFree = QLabel(self.groupBoxMainNumbers)
        self.valueFree.setObjectName(u"valueFree")

        self.formLayoutMainNumbers.setWidget(1, QFormLayout.FieldRole, self.valueFree)


        self.verticalLayoutMainNumbers.addLayout(self.formLayoutMainNumbers)

        self.verticalLayout.addWidget(self.groupBoxMainNumbers)

        self.groupBoxArticles = QGroupBox(MarketStatistics)
        self.groupBoxArticles.setObjectName(u"groupBoxArticles")
        self.verticalLayoutArticles = QVBoxLayout(self.groupBoxArticles)
        self.verticalLayoutArticles.setObjectName(u"verticalLayoutArticles")
        self.chartArticles = QChartView(self.groupBoxArticles)
        self.chartArticles.setObjectName(u"chartArticles")

        self.verticalLayoutArticles.addWidget(self.chartArticles)

        self.formLayoutArticles = QFormLayout()
        self.formLayoutArticles.setObjectName(u"formLayoutArticles")
        self.labelTotal = QLabel(self.groupBoxArticles)
        self.labelTotal.setObjectName(u"labelTotal")

        self.formLayoutArticles.setWidget(0, QFormLayout.LabelRole, self.labelTotal)

        self.valueTotal = QLabel(self.groupBoxArticles)
        self.valueTotal.setObjectName(u"valueTotal")

        self.formLayoutArticles.setWidget(0, QFormLayout.FieldRole, self.valueTotal)

        self.labelComplete = QLabel(self.groupBoxArticles)
        self.labelComplete.setObjectName(u"labelComplete")

        self.formLayoutArticles.setWidget(1, QFormLayout.LabelRole, self.labelComplete)

        self.valueComplete = QLabel(self.groupBoxArticles)
        self.valueComplete.setObjectName(u"valueComplete")

        self.formLayoutArticles.setWidget(1, QFormLayout.FieldRole, self.valueComplete)

        self.labelPartial = QLabel(self.groupBoxArticles)
        self.labelPartial.setObjectName(u"labelPartial")

        self.formLayoutArticles.setWidget(2, QFormLayout.LabelRole, self.labelPartial)

        self.valuePartial = QLabel(self.groupBoxArticles)
        self.valuePartial.setObjectName(u"valuePartial")

        self.formLayoutArticles.setWidget(2, QFormLayout.FieldRole, self.valuePartial)

        self.labelOpen = QLabel(self.groupBoxArticles)
        self.labelOpen.setObjectName(u"labelOpen")

        self.formLayoutArticles.setWidget(3, QFormLayout.LabelRole, self.labelOpen)

        self.valueOpen = QLabel(self.groupBoxArticles)
        self.valueOpen.setObjectName(u"valueOpen")

        self.formLayoutArticles.setWidget(3, QFormLayout.FieldRole, self.valueOpen)


        self.verticalLayoutArticles.addLayout(self.formLayoutArticles)

        self.verticalLayout.addWidget(self.groupBoxArticles)

        self.groupBoxUsers = QGroupBox(MarketStatistics)
        self.groupBoxUsers.setObjectName(u"groupBoxUsers")
        self.formLayoutUsers = QFormLayout(self.groupBoxUsers)
        self.formLayoutUsers.setObjectName(u"formLayoutUsers")
        self.labelUserCount = QLabel(self.groupBoxUsers)
        self.labelUserCount.setObjectName(u"labelUserCount")

        self.formLayoutUsers.setWidget(0, QFormLayout.LabelRole, self.labelUserCount)

        self.valueUserCount = QLabel(self.groupBoxUsers)
        self.valueUserCount.setObjectName(u"valueUserCount")

        self.formLayoutUsers.setWidget(0, QFormLayout.FieldRole, self.valueUserCount)


        self.verticalLayout.addWidget(self.groupBoxUsers)


        self.retranslateUi(MarketStatistics)

        QMetaObject.connectSlotsByName(MarketStatistics)
    # setupUi

    def retranslateUi(self, MarketStatistics):
        MarketStatistics.setWindowTitle(QCoreApplication.translate("MarketStatistics", u"Statistik", None))
        MarketStatistics.setStyleSheet(QCoreApplication.translate(
            "MarketStatistics",
            u"QWidget { font-family: \"Segoe UI\", sans-serif; font-size: 10pt; background-color: #f0f0f0; }\n"
            "QPushButton { border: none; padding: 6px 12px; border-radius: 4px; background-color: #0078d7; color: white; }\n"
            "QPushButton:hover { background-color: #005a9e; }\n"
            "QGroupBox { border: 1px solid #cccccc; border-radius: 4px; margin-top: 6px; }\n"
            "QGroupBox::title { subcontrol-origin: margin; subcontrol-position: top left; padding: 0 6px; }\n",
            None
        ))
        self.groupBoxMainNumbers.setTitle(QCoreApplication.translate("MarketStatistics", u"Stammnummern", None))
        self.labelUsed.setText(QCoreApplication.translate("MarketStatistics", u"Verwendet:", None))
        self.labelFree.setText(QCoreApplication.translate("MarketStatistics", u"Frei:", None))
        self.groupBoxArticles.setTitle(QCoreApplication.translate("MarketStatistics", u"Artikel", None))
        self.labelTotal.setText(QCoreApplication.translate("MarketStatistics", u"Gesamt:", None))
        self.labelComplete.setText(QCoreApplication.translate("MarketStatistics", u"Fertig:", None))
        self.labelPartial.setText(QCoreApplication.translate("MarketStatistics", u"Aktuell:", None))
        self.labelOpen.setText(QCoreApplication.translate("MarketStatistics", u"Offen:", None))
        self.groupBoxUsers.setTitle(QCoreApplication.translate("MarketStatistics", u"Benutzer", None))
        self.labelUserCount.setText(QCoreApplication.translate("MarketStatistics", u"Anzahl:", None))
    # retranslateUi
