# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'main_window.ui'
##
## Created by: Qt User Interface Compiler version 6.8.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QAction, QBrush, QColor, QConicalGradient,
    QCursor, QFont, QFontDatabase, QGradient,
    QIcon, QImage, QKeySequence, QLinearGradient,
    QPainter, QPalette, QPixmap, QRadialGradient,
    QTransform)
from PySide6.QtWidgets import (QApplication, QHBoxLayout, QMainWindow, QMenu,
    QMenuBar, QSizePolicy, QStatusBar, QToolBar,
    QWidget)
import ressources_rc

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(754, 695)
        self.action_tool = QAction(MainWindow)
        self.action_tool.setObjectName(u"action_tool")
        self.action_close = QAction(MainWindow)
        self.action_close.setObjectName(u"action_close")
        self.action_open_export = QAction(MainWindow)
        self.action_open_export.setObjectName(u"action_open_export")
        icon = QIcon()
        icon.addFile(u":/icons/folder-open.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.action_open_export.setIcon(icon)
        self.actionToolbars = QAction(MainWindow)
        self.actionToolbars.setObjectName(u"actionToolbars")
        self.action_Export_Data = QAction(MainWindow)
        self.action_Export_Data.setObjectName(u"action_Export_Data")
        icon1 = QIcon()
        icon1.addFile(u":/icons/file-database.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.action_Export_Data.setIcon(icon1)
        self.action_Export_Data.setMenuRole(QAction.NoRole)
        self.actionCreate_PDF = QAction(MainWindow)
        self.actionCreate_PDF.setObjectName(u"actionCreate_PDF")
        icon2 = QIcon()
        icon2.addFile(u":/icons/file-type-pdf.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.actionCreate_PDF.setIcon(icon2)
        self.actionCreate_PDF.setMenuRole(QAction.NoRole)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.horizontalLayout = QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 754, 22))
        self.menu_file = QMenu(self.menubar)
        self.menu_file.setObjectName(u"menu_file")
        self.menu_help = QMenu(self.menubar)
        self.menu_help.setObjectName(u"menu_help")
        self.menuVies = QMenu(self.menubar)
        self.menuVies.setObjectName(u"menuVies")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.tool_export = QToolBar(MainWindow)
        self.tool_export.setObjectName(u"tool_export")
        self.tool_export.setFloatable(True)
        MainWindow.addToolBar(Qt.ToolBarArea.TopToolBarArea, self.tool_export)

        self.menubar.addAction(self.menu_file.menuAction())
        self.menubar.addAction(self.menuVies.menuAction())
        self.menubar.addAction(self.menu_help.menuAction())
        self.menu_file.addAction(self.action_open_export)
        self.menu_file.addSeparator()
        self.menu_file.addAction(self.action_close)
        self.menu_help.addAction(self.action_tool)
        self.menuVies.addAction(self.actionToolbars)
        self.tool_export.addAction(self.action_open_export)
        self.tool_export.addSeparator()
        self.tool_export.addAction(self.action_Export_Data)
        self.tool_export.addAction(self.actionCreate_PDF)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"Benutzer\u00fcbersicht", None))
        self.action_tool.setText(QCoreApplication.translate("MainWindow", u"&About Flohmarktmanager", None))
        self.action_close.setText(QCoreApplication.translate("MainWindow", u"&Beenden", None))
        self.action_open_export.setText(QCoreApplication.translate("MainWindow", u"&Eport Daten \u00f6ffnen", None))
        self.actionToolbars.setText(QCoreApplication.translate("MainWindow", u"Toolbars", None))
        self.action_Export_Data.setText(QCoreApplication.translate("MainWindow", u"$Export Data", None))
        self.actionCreate_PDF.setText(QCoreApplication.translate("MainWindow", u"Create PDF", None))
        self.menu_file.setTitle(QCoreApplication.translate("MainWindow", u"File", None))
        self.menu_help.setTitle(QCoreApplication.translate("MainWindow", u"Help", None))
        self.menuVies.setTitle(QCoreApplication.translate("MainWindow", u"View", None))
        self.tool_export.setWindowTitle(QCoreApplication.translate("MainWindow", u"toolBar", None))
    # retranslateUi

