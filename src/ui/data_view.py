# DataView.py

import sys
from typing import Dict
from pathlib import Path

from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtWidgets import (
    QApplication, QTreeWidgetItem, QTableWidgetItem, QListWidget, QListWidgetItem,
    QMenu
)
from .generated import DataViewUi  # Annahme: In __init__.py wurde der UI-Code als DataViewUi bereitgestellt.
from .base_ui import BaseUi

sys.path.insert(0, Path(__file__).parent.parent.parent.__str__())  # NOQA: E402 pylint: disable=[C0413]
from src.data import DataManager, MarketFacade


class DataView(BaseUi):
    """Widget used to browse seller and article information."""

    data_changed = Signal(bool)

    def __init__(self, parent=None):
        """Create UI elements and initialise state.

        Parameters
        ----------
        parent:
            Optional Qt parent widget.
        """
        super().__init__(parent)
        self.ui = DataViewUi()
        self.market = None  # reference to the Market widget
        self.ui.setupUi(self)


        # context menu for deletion
        self.ui.treeUsers.setContextMenuPolicy(Qt.CustomContextMenu)
        self.ui.treeUsers.customContextMenuRequested.connect(
            self._tree_context_menu)
        
        
      
    def setup_views(self, market_widget):
        """Initialise tree and list views.

        Parameters
        ----------
        market_widget:
            The :class:`Market` widget providing data access.
        """
        self.market = market_widget
        self.listUsers = QListWidget()
        self.setup_connections()
        self.populate_user_tree()
        self.ui.verticalLayoutLeft.addWidget(self.listUsers)
        self.listUsers.hide()

    def setup_connections(self):
        """Connect UI widgets to their event handlers."""
        self.ui.btnToggleView.clicked.connect(self.toggle_view)
        self.ui.treeUsers.itemClicked.connect(self.user_item_clicked)
        self.listUsers.itemClicked.connect(self.user_list_item_clicked)

    def populate_user_tree(self):
        """Fill the tree view with aggregated sellers and their tables."""
        if not self.market_widget().get_aggregated_user():
            return
        
        self.ui.treeUsers.clear()
        users_list = self.market_widget().get_aggregated_user()
        for email, user in users_list.items():
            info = user["info"]
            name = f"{info.vorname} {info.nachname}".strip()
            if DataManager.seller_is_empty(info):
                name = "<Leer>"
            user_text = name
            user_item = QTreeWidgetItem([user_text])
            # Füge als untergeordnete Elemente die zugehörigen MainNumber-Tabellen hinzu.
            for main_number in user["stamms"]:
                child = QTreeWidgetItem([main_number.name])
                user_item.addChild(child)
            self.ui.treeUsers.addTopLevelItem(user_item)

    def market_widget(self):
        """Return the associated :class:`Market` instance."""
        return self.market

    def populate_user_list(self):
        """Fill the list widget with seller information.

        The method uses :func:`Market.get_seller` to obtain the data. Each
        seller is formatted as ``"{index}. {first} {last}"`` and attached to a
        :class:`QListWidgetItem` via :data:`Qt.UserRole` for later retrieval.
        """
        
        if not self.market_widget().get_seller():
            return
        
        self.listUsers.clear()
        flat_users = self.market_widget().get_seller()
        for index, seller in enumerate(flat_users, start=1):
            name = f"{seller.vorname} {seller.nachname}".strip()
            if DataManager.seller_is_empty(seller):
                name = "<Leer>"
            text = f"{index}. {name}"
            item = QListWidgetItem(text)
            item.setData(Qt.UserRole, seller)
            self.listUsers.addItem(item)

    def toggle_view(self):
        """Switch between tree and list representations."""
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
        """Handle clicks on items inside the tree view.

        Parameters
        ----------
        item:
            The clicked :class:`QTreeWidgetItem`.
        column:
            Column index where the click occurred.
        """
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
                info = user["info"]
                info_text = f"{info.vorname} {info.nachname}".strip()
                if DataManager.seller_is_empty(info):
                    info_text = "<Leer>"
                if info_text == user_text:
                    for main_number in user["stamms"]:
                        entries.extend(main_number.data)
                    break
        self.populate_entry_table(entries)

    def user_list_item_clicked(self, item):
        """Handle clicks in the plain list view.

        Parameters
        ----------
        item:
            The clicked :class:`QListWidgetItem` containing seller data.
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
        """Populate the table widget with article details.

        Parameters
        ----------
        entries:
            Iterable of objects providing ``beschreibung``, ``groesse``,
            ``preis`` and ``created_at`` attributes.
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

    # ------------------------------------------------------------------
    # Delete/Save helpers
    # ------------------------------------------------------------------

    def _current_stammnummer(self):
        """Return the currently selected stammnummer if available."""
        if self.ui.treeUsers.isVisible():
            item = self.ui.treeUsers.currentItem()
            if item and item.parent() is not None:
                text = item.text(0)
                return text[4:] if text.startswith("stnr") else text
        else:
            item = self.listUsers.currentItem()
            if item:
                seller = item.data(Qt.UserRole)
                return seller.id
        return None

    @Slot()
    def delete_selected_dataset(self):
        stamm = self._current_stammnummer()
        if not stamm:
            return
        dm = self.market_widget().get_data_manager()
        try:
            dm.delete_dataset(stamm)
            dm.synchornize_data_class_change_to_json()
        except Exception:
            return
        self.populate_user_tree()
        if self.listUsers.isVisible():
            self.populate_user_list()
        self.data_changed.emit(True)

    def _tree_context_menu(self, pos):
        item = self.ui.treeUsers.itemAt(pos)
        if not item or item.parent() is None:
            return
        menu = QMenu(self)
        delete_action = menu.addAction("Stammnummer löschen")
        action = menu.exec(self.ui.treeUsers.viewport().mapToGlobal(pos))
        if action == delete_action:
            self.ui.treeUsers.setCurrentItem(item)
            self.delete_selected_dataset()

    @Slot()
    def save_project(self):
        facade = MarketFacade()
        project_dir = facade.get_project_dir(self.market_widget())
        if project_dir:
            facade.save_project(self.market_widget(), project_dir)
            self.data_changed.emit(False)

    @Slot()
    def restore_changes(self):
        dm = self.market_widget().get_data_manager()
        dm.reset_all_changes()
        dm.synchornize_data_class_change_to_json()
        self.populate_user_tree()
        if self.listUsers.isVisible():
            self.populate_user_list()
        self.data_changed.emit(False)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = DataView()
    window.show()
    sys.exit(app.exec())