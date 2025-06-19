# DataView.py

import sys
from typing import Dict
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication, QTreeWidgetItem, QTableWidgetItem, QListWidget, QListWidgetItem
)
from .generated import DataViewUi  # Annahme: In __init__.py wurde der UI-Code als DataViewUi bereitgestellt.
from .base_ui import BaseUi

sys.path.insert(0, Path(__file__).parent.parent.parent.__str__())  # NOQA: E402 pylint: disable=[C0413]
from src.data import DataManager


class DataView(BaseUi):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = DataViewUi()
        # Aufbau der UI (erstellt alle Widgets und Layouts)
        self.market = None  # Zugriff auf das MarketWidget
        self.ui.setupUi(self)
        
        
      
    def setup_views(self, market_widget):
        """Initialisiert die Ansichten (Baum- und Listenansicht)."""
        self.market = market_widget
        self.listUsers = QListWidget()
        self.setup_connections()
        self.populate_user_tree()
        self.ui.verticalLayoutLeft.addWidget(self.listUsers)
        self.listUsers.hide()

    def setup_connections(self):
        """Verbindet UI-Elemente mit ihren Event-Handlern."""
        self.ui.btnToggleView.clicked.connect(self.toggle_view)
        self.ui.treeUsers.itemClicked.connect(self.user_item_clicked)
        self.listUsers.itemClicked.connect(self.user_list_item_clicked)

    def populate_user_tree(self):
        """
        Befüllt die Baumansicht mit aggregierten Verkäufern und ihren zugehörigen
        MainNumber-Tabellen (stnr‑Tabellen). Jeder Verkäufer wird über seine E‑Mail
        aggregiert und als Knoten dargestellt.
        """
        if not self.market_widget().get_aggregated_user():
            return
        
        self.ui.treeUsers.clear()
        users_list = self.market_widget().get_aggregated_user()
        for email, user in users_list.items():
            user_text = f'{user["info"].vorname} {user["info"].nachname} ({user["info"].email})'
            user_item = QTreeWidgetItem([user_text])
            # Füge als untergeordnete Elemente die zugehörigen MainNumber-Tabellen hinzu.
            for main_number in user["stamms"]:
                child = QTreeWidgetItem([main_number.name])
                user_item.addChild(child)
            self.ui.treeUsers.addTopLevelItem(user_item)

    def market_widget(self):
        return self.market

    def populate_user_list(self):
        """
        Populates the list widget with seller information retrieved from the data manager.
        This method first checks if the data manager is available. If not, it exits without performing
        any operations. Otherwise, it clears the current items in the user list widget and iterates
        through the collection of sellers provided by the data manager. For each seller, it formats a
        display string that includes the seller's index, first name, last name, and email address. A new
        QListWidgetItem is created with this display text, and the corresponding seller object is attached
        to the item using the Qt.UserRole, enabling later retrieval of the full seller data.
        Returns:
            None
        """
        
        if not self.market_widget().get_seller():
            return
        
        self.listUsers.clear()
        flat_users = self.market_widget().get_seller()
        for index, seller in enumerate(flat_users, start=1):
            text = f'{index}. {seller.vorname} {seller.nachname}'
            item = QListWidgetItem(text)
            item.setData(Qt.UserRole, seller)
            self.listUsers.addItem(item)

    def toggle_view(self):
       
        if self.ui.treeUsers.isVisible():
            self.ui.treeUsers.hide()
            self.populate_user_list()
            self.listUsers.show()
            self.ui.btnToggleView.setText("Baumansicht")
        else:
            self.listUsers.hide()
            self.ui.treeUsers.show()
            self.ui.btnToggleView.setText("Listenansicht")

    def user_item_clicked(self, item, column):
  
        if not self.market_widget().get_aggregated_user():
            return

        if item.parent() is not None:
            # Kindelement (stnr‑Tabelle) wurde angeklickt.
            stnr_name = item.text(0)
            entries = None
            users_list = self.market_widget().get_aggregated_user()
            for user in users_list.values():
                for main_number in user["stamms"]:
                    if main_number.name == stnr_name:
                        entries = main_number.data
                        break
                if entries is not None:
                    break
        else:
            # Verkäuferknoten wurde angeklickt: Alle zugehörigen Artikel zusammenfassen.
            entries = []
            user_text = item.text(0)
            users_list = self.market_widget().get_aggregated_user()
            for user in users_list.values():
                #info_text = f'{user["info"].vorname} {user["info"].nachname} ({user["info"].email})'
                info_text = f'{user["info"].vorname} {user["info"].nachname}'
                if info_text == user_text:
                    for main_number in user["stamms"]:
                        entries.extend(main_number.data)
                    break
        self.populate_entry_table(entries)

    def user_list_item_clicked(self, item):
        """
        Reagiert auf Klicks in der flachen Listenansicht:
        Anhand der Verkäufer-ID wird die zugehörige stnr‑Tabelle ermittelt und
        deren Artikel angezeigt.
        """
        if not self.market_widget().get_main_numbers():
            return
        
        seller = item.data(Qt.UserRole)
        target_stnr = "stnr" + seller.id
        strnr_tables = self.market_widget().get_main_numbers()
        main_number = strnr_tables.get(target_stnr)
        entries = main_number.data if main_number else []
        self.populate_entry_table(entries)

    def populate_entry_table(self, entries):
        """
        Befüllt das Tabellen-Widget mit den Detail-Artikeln.
        Dabei wird auf die Artikelattribute (aus ArticleDataClass) über Attribute zugegriffen.
        """
        #headers = ["artikelnummer", "beschreibung", "groesse", "preis", "created_at"]
        headers = ["Beschreibung", "Groesse", "Preis", "Created_At"]
        self.ui.tableEntries.clearContents()
        self.ui.tableEntries.setColumnCount(len(headers))
        self.ui.tableEntries.setHorizontalHeaderLabels(headers)
        
        if not entries:
            self.ui.tableEntries.setRowCount(0)
            return
        self.ui.tableEntries.setRowCount(len(entries))
        
        for row, entry in enumerate(entries):
            #self.ui.tableEntries.setItem(row, 0, QTableWidgetItem(getattr(entry, "artikelnummer", "")))
            self.ui.tableEntries.setItem(row, 0, QTableWidgetItem(getattr(entry, "beschreibung", "")))
            self.ui.tableEntries.setItem(row, 1, QTableWidgetItem(getattr(entry, "groesse", "")))
            self.ui.tableEntries.setItem(row, 2, QTableWidgetItem(getattr(entry, "preis", "")))
            self.ui.tableEntries.setItem(row, 3, QTableWidgetItem(getattr(entry, "created_at", "")))

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = DataView()
    window.show()
    sys.exit(app.exec())