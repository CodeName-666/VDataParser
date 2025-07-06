# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'main_window.ui'
##
## Created by: Qt User Interface Compiler version 6.8.2
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
    QMenuBar, QSizePolicy, QToolBar, QWidget)
import ressources_rc

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(770, 450)
        self.action_create_pdf = QAction(MainWindow)
        self.action_create_pdf.setObjectName(u"action_create_pdf")
        icon = QIcon()
        icon.addFile(u":/icons/file-type-pdf.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.action_create_pdf.setIcon(icon)
        self.action_create_pdf.setMenuRole(QAction.NoRole)
        self.action_generate_data = QAction(MainWindow)
        self.action_generate_data.setObjectName(u"action_generate_data")
        icon1 = QIcon()
        icon1.addFile(u":/icons/radioactive.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.action_generate_data.setIcon(icon1)
        self.action_generate_data.setMenuRole(QAction.NoRole)
        self.action_generate_add = QAction(MainWindow)
        self.action_generate_add.setObjectName(u"action_generate_add")
        icon2 = QIcon()
        icon2.addFile(u":/icons/radioactive_filled.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.action_generate_add.setIcon(icon2)
        self.action_generate_add.setMenuRole(QAction.NoRole)
        self.action_save_project = QAction(MainWindow)
        self.action_save_project.setObjectName(u"action_save_project")
        icon3 = QIcon()
        icon3.addFile(u":/icons/file-database.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.action_save_project.setIcon(icon3)
        self.action_save_project.setMenuRole(QAction.NoRole)
        self.action_save_project_as = QAction(MainWindow)
        self.action_save_project_as.setObjectName(u"action_save_project_as")
        icon4 = QIcon()
        icon4.addFile(u":/icons/database-export.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.action_save_project_as.setIcon(icon4)
        self.action_save_project_as.setMenuRole(QAction.NoRole)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.horizontalLayout = QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 770, 22))
        self.menu_file = QMenu(self.menubar)
        self.menu_file.setObjectName(u"menu_file")
        self.menu_help = QMenu(self.menubar)
        self.menu_help.setObjectName(u"menu_help")
        MainWindow.setMenuBar(self.menubar)
        self.tool_export = QToolBar(MainWindow)
        self.tool_export.setObjectName(u"tool_export")
        self.tool_export.setFloatable(True)
        MainWindow.addToolBar(Qt.ToolBarArea.LeftToolBarArea, self.tool_export)
        self.tool_project = QToolBar(MainWindow)
        self.tool_project.setObjectName(u"tool_project")
        MainWindow.addToolBar(Qt.ToolBarArea.LeftToolBarArea, self.tool_project)
        self.toolBar = QToolBar(MainWindow)
        self.toolBar.setObjectName(u"toolBar")
        MainWindow.addToolBar(Qt.ToolBarArea.LeftToolBarArea, self.toolBar)

        self.menubar.addAction(self.menu_file.menuAction())
        self.menubar.addAction(self.menu_help.menuAction())
        self.menu_file.addAction(self.action_save_project)
        self.menu_file.addAction(self.action_save_project_as)
        self.menu_file.addSeparator()
        self.tool_export.addAction(self.action_create_pdf)
        self.tool_export.addAction(self.action_generate_data)
        self.tool_export.addAction(self.action_generate_add)
        self.tool_project.addAction(self.action_save_project)
        self.tool_project.addAction(self.action_save_project_as)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"Benutzer\u00fcbersicht", None))
        MainWindow.setStyleSheet(QCoreApplication.translate("MainWindow", u"QWidget { font-family: \"Segoe UI\", sans-serif; font-size: 10pt; background-color: #f0f0f0; }\n"
"QPushButton { border: none; padding: 6px 12px; border-radius: 4px; background-color: #0078d7; color: white; }\n"
"QPushButton:hover { background-color: #005a9e; }\n"
"QGroupBox { border: 1px solid #cccccc; border-radius: 4px; margin-top: 6px; }\n"
"QGroupBox::title { subcontrol-origin: margin; subcontrol-position: top left; padding: 0 6px; }", None))
        self.action_create_pdf.setText(QCoreApplication.translate("MainWindow", u"&Create PDF", None))
#if QT_CONFIG(tooltip)
        self.action_create_pdf.setToolTip(QCoreApplication.translate("MainWindow", u"PDF erstellen", None))
#endif // QT_CONFIG(tooltip)
        self.action_generate_data.setText(QCoreApplication.translate("MainWindow", u"&Daten Generieren", None))
#if QT_CONFIG(tooltip)
        self.action_generate_data.setToolTip(QCoreApplication.translate("MainWindow", u"Daten generieren", None))
#endif // QT_CONFIG(tooltip)
        self.action_generate_add.setText(QCoreApplication.translate("MainWindow", u"&Alles generieren", None))
#if QT_CONFIG(tooltip)
        self.action_generate_add.setToolTip(QCoreApplication.translate("MainWindow", u"Alles generieren", None))
#endif // QT_CONFIG(tooltip)
        self.action_save_project.setText(QCoreApplication.translate("MainWindow", u"&Projekt speichern", None))
#if QT_CONFIG(tooltip)
        self.action_save_project.setToolTip(QCoreApplication.translate("MainWindow", u"Projekt speichern", None))
#endif // QT_CONFIG(tooltip)
        self.action_save_project_as.setText(QCoreApplication.translate("MainWindow", u"&Projekt speichern unter", None))
#if QT_CONFIG(tooltip)
        self.action_save_project_as.setToolTip(QCoreApplication.translate("MainWindow", u"Projekt speichern unter", None))
#endif // QT_CONFIG(tooltip)
        self.menu_file.setTitle(QCoreApplication.translate("MainWindow", u"File", None))
        self.menu_help.setTitle(QCoreApplication.translate("MainWindow", u"Help", None))
        self.tool_export.setWindowTitle(QCoreApplication.translate("MainWindow", u"toolBar", None))
        self.tool_project.setWindowTitle(QCoreApplication.translate("MainWindow", u"toolBar", None))
        self.toolBar.setWindowTitle(QCoreApplication.translate("MainWindow", u"toolBar", None))
    # retranslateUi

