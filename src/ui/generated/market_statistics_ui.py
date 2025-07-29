# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'market_statistics.ui'
##
## Created by: Qt User Interface Compiler version 6.8.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCharts import QChartView
from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QFormLayout, QGroupBox, QHBoxLayout,
    QLabel, QProgressBar, QSizePolicy, QVBoxLayout,
    QWidget)

class Ui_MarketStatistics(object):
    def setupUi(self, MarketStatistics):
        if not MarketStatistics.objectName():
            MarketStatistics.setObjectName(u"MarketStatistics")
        MarketStatistics.resize(976, 982)
        self.verticalLayout_2 = QVBoxLayout(MarketStatistics)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.groupBoxUsers = QGroupBox(MarketStatistics)
        self.groupBoxUsers.setObjectName(u"groupBoxUsers")
        self.verticalLayout = QVBoxLayout(self.groupBoxUsers)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.labelUserCount = QLabel(self.groupBoxUsers)
        self.labelUserCount.setObjectName(u"labelUserCount")

        self.horizontalLayout.addWidget(self.labelUserCount)

        self.valueUserCount = QLabel(self.groupBoxUsers)
        self.valueUserCount.setObjectName(u"valueUserCount")

        self.horizontalLayout.addWidget(self.valueUserCount)

        self.labelUserCurrent = QLabel(self.groupBoxUsers)
        self.labelUserCurrent.setObjectName(u"labelUserCurrent")

        self.horizontalLayout.addWidget(self.labelUserCurrent)

        self.valueUserCurrent = QLabel(self.groupBoxUsers)
        self.valueUserCurrent.setObjectName(u"valueUserCurrent")

        self.horizontalLayout.addWidget(self.valueUserCurrent)

        self.labelUserMax = QLabel(self.groupBoxUsers)
        self.labelUserMax.setObjectName(u"labelUserMax")

        self.horizontalLayout.addWidget(self.labelUserMax)

        self.valueUserMax = QLabel(self.groupBoxUsers)
        self.valueUserMax.setObjectName(u"valueUserMax")

        self.horizontalLayout.addWidget(self.valueUserMax)


        self.verticalLayout.addLayout(self.horizontalLayout)

        self.progressUsers = QProgressBar(self.groupBoxUsers)
        self.progressUsers.setObjectName(u"progressUsers")
        self.progressUsers.setValue(24)

        self.verticalLayout.addWidget(self.progressUsers)


        self.verticalLayout_2.addWidget(self.groupBoxUsers)

        self.groupBoxMainNumbers = QGroupBox(MarketStatistics)
        self.groupBoxMainNumbers.setObjectName(u"groupBoxMainNumbers")
        self.horizontalLayout_2 = QHBoxLayout(self.groupBoxMainNumbers)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.chartMainNumbers = QChartView(self.groupBoxMainNumbers)
        self.chartMainNumbers.setObjectName(u"chartMainNumbers")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.chartMainNumbers.sizePolicy().hasHeightForWidth())
        self.chartMainNumbers.setSizePolicy(sizePolicy)
        self.chartMainNumbers.setMinimumSize(QSize(0, 100))

        self.horizontalLayout_2.addWidget(self.chartMainNumbers)

        self.formLayoutMainNumbers = QFormLayout()
        self.formLayoutMainNumbers.setObjectName(u"formLayoutMainNumbers")
        self.labelCompleteNums = QLabel(self.groupBoxMainNumbers)
        self.labelCompleteNums.setObjectName(u"labelCompleteNums")

        self.formLayoutMainNumbers.setWidget(0, QFormLayout.LabelRole, self.labelCompleteNums)

        self.valueCompleteNums = QLabel(self.groupBoxMainNumbers)
        self.valueCompleteNums.setObjectName(u"valueCompleteNums")

        self.formLayoutMainNumbers.setWidget(0, QFormLayout.FieldRole, self.valueCompleteNums)

        self.labelAlmostNums = QLabel(self.groupBoxMainNumbers)
        self.labelAlmostNums.setObjectName(u"labelAlmostNums")

        self.formLayoutMainNumbers.setWidget(1, QFormLayout.LabelRole, self.labelAlmostNums)

        self.valueAlmostNums = QLabel(self.groupBoxMainNumbers)
        self.valueAlmostNums.setObjectName(u"valueAlmostNums")

        self.formLayoutMainNumbers.setWidget(1, QFormLayout.FieldRole, self.valueAlmostNums)

        self.labelHalfNums = QLabel(self.groupBoxMainNumbers)
        self.labelHalfNums.setObjectName(u"labelHalfNums")

        self.formLayoutMainNumbers.setWidget(2, QFormLayout.LabelRole, self.labelHalfNums)

        self.valueHalfNums = QLabel(self.groupBoxMainNumbers)
        self.valueHalfNums.setObjectName(u"valueHalfNums")

        self.formLayoutMainNumbers.setWidget(2, QFormLayout.FieldRole, self.valueHalfNums)

        self.labelInProgressNums = QLabel(self.groupBoxMainNumbers)
        self.labelInProgressNums.setObjectName(u"labelInProgressNums")

        self.formLayoutMainNumbers.setWidget(3, QFormLayout.LabelRole, self.labelInProgressNums)

        self.valueInProgressNums = QLabel(self.groupBoxMainNumbers)
        self.valueInProgressNums.setObjectName(u"valueInProgressNums")

        self.formLayoutMainNumbers.setWidget(3, QFormLayout.FieldRole, self.valueInProgressNums)

        self.labelStartedNums = QLabel(self.groupBoxMainNumbers)
        self.labelStartedNums.setObjectName(u"labelStartedNums")

        self.formLayoutMainNumbers.setWidget(4, QFormLayout.LabelRole, self.labelStartedNums)

        self.valueStartedNums = QLabel(self.groupBoxMainNumbers)
        self.valueStartedNums.setObjectName(u"valueStartedNums")

        self.formLayoutMainNumbers.setWidget(4, QFormLayout.FieldRole, self.valueStartedNums)


        self.horizontalLayout_2.addLayout(self.formLayoutMainNumbers)


        self.verticalLayout_2.addWidget(self.groupBoxMainNumbers)

        self.groupBoxArticles = QGroupBox(MarketStatistics)
        self.groupBoxArticles.setObjectName(u"groupBoxArticles")
        self.horizontalLayout_3 = QHBoxLayout(self.groupBoxArticles)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.chartArticles = QChartView(self.groupBoxArticles)
        self.chartArticles.setObjectName(u"chartArticles")
        sizePolicy.setHeightForWidth(self.chartArticles.sizePolicy().hasHeightForWidth())
        self.chartArticles.setSizePolicy(sizePolicy)
        self.chartArticles.setMinimumSize(QSize(0, 100))

        self.horizontalLayout_3.addWidget(self.chartArticles)

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


        self.horizontalLayout_3.addLayout(self.formLayoutArticles)


        self.verticalLayout_2.addWidget(self.groupBoxArticles)


        self.retranslateUi(MarketStatistics)

        QMetaObject.connectSlotsByName(MarketStatistics)
    # setupUi

    def retranslateUi(self, MarketStatistics):
        MarketStatistics.setWindowTitle(QCoreApplication.translate("MarketStatistics", u"Statistik", None))
        MarketStatistics.setStyleSheet(QCoreApplication.translate("MarketStatistics", u"QWidget { font-family: \"Segoe UI\", sans-serif; font-size: 10pt; background-color: #f0f0f0; }\n"
"QPushButton { border: none; padding: 6px 12px; border-radius: 4px; background-color: #0078d7; color: white; }\n"
"QPushButton:hover { background-color: #005a9e; }\n"
"QGroupBox { border: 1px solid #cccccc; border-radius: 4px; margin-top: 6px; }\n"
"QGroupBox::title { subcontrol-origin: margin; subcontrol-position: top left; padding: 0 6px; }\n"
"", None))
        self.groupBoxUsers.setTitle(QCoreApplication.translate("MarketStatistics", u"Benutzer", None))
        self.labelUserCount.setText(QCoreApplication.translate("MarketStatistics", u"Max. m\u00f6gliche Anzahl an Stammnummern:", None))
        self.labelUserCurrent.setText(QCoreApplication.translate("MarketStatistics", u"Aktuell verwendete Stammnummern:", None))
        self.labelUserMax.setText(QCoreApplication.translate("MarketStatistics", u"Anzahl freie Stammnummern:", None))
        self.groupBoxMainNumbers.setTitle(QCoreApplication.translate("MarketStatistics", u"Stammnummern", None))
        self.labelCompleteNums.setText(QCoreApplication.translate("MarketStatistics", u"Vollst\u00e4ndig:", None))
        self.labelAlmostNums.setText(QCoreApplication.translate("MarketStatistics", u"Fast fertig:", None))
        self.labelHalfNums.setText(QCoreApplication.translate("MarketStatistics", u"Halb fertig:", None))
        self.labelInProgressNums.setText(QCoreApplication.translate("MarketStatistics", u"In Arbeit:", None))
        self.labelStartedNums.setText(QCoreApplication.translate("MarketStatistics", u"Angefangen:", None))
        self.groupBoxArticles.setTitle(QCoreApplication.translate("MarketStatistics", u"Artikel", None))
        self.labelTotal.setText(QCoreApplication.translate("MarketStatistics", u"Gesamt:", None))
        self.labelComplete.setText(QCoreApplication.translate("MarketStatistics", u"Fertig:", None))
        self.labelPartial.setText(QCoreApplication.translate("MarketStatistics", u"Aktuell:", None))
        self.labelOpen.setText(QCoreApplication.translate("MarketStatistics", u"Offen:", None))
    # retranslateUi

