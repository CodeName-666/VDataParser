from PySide6.QtWidgets import QTableWidgetItem
from .base_ui import BaseUi
from .generated import UserInfoUi

class UserInfo(BaseUi):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = UserInfoUi()
        self.market = None  # Zugriff auf das MarketWidget
        self.ui.setupUi(self)

        headers = ["StNr.", "Fertig", "Offen","Leer"," Summe"]
        self.ui.tableIDs.setColumnCount(len(headers))
        self.ui.tableIDs.setHorizontalHeaderLabels(headers)
        self.setup_signals()

    def setup_views(self, market_widget):
        """Setzt den DataManager und initialisiert die Anzeige."""
        self.market = market_widget
        self.users_data = self.market_widget().get_user_data()
        self.aggregated_users_data = self.market_widget().get_aggregated_user_data()

        # Standardmäßig werden die nicht aggregierten Einträge angezeigt.
        self.current_user_list = self.users_data

        self.refresh_user_list()
        if self.ui.listWidgetUsers.count() > 0:
            self.ui.listWidgetUsers.setCurrentRow(0)


    def market_widget(self):
        return self.market

    def setup_signals(self):
        """Verbindet die UI-Signale mit den entsprechenden Methoden."""
        self.ui.checkboxUnique.toggled.connect(self.refresh_user_list)
        self.ui.listWidgetUsers.currentRowChanged.connect(self.display_user_details)

    def refresh_user_list(self):
        """Aktualisiert die ListWidget-Anzeige basierend auf dem Status der Checkbox."""
        self.ui.listWidgetUsers.clear()
        if self.ui.checkboxUnique.isChecked():
            self.current_user_list = self.aggregated_users_data
            for user in self.current_user_list:
                count_ids = len(user.get("ids", []))
                name = f"{user.get('vorname', '')} {user.get('nachname', '')}".strip()
                text = f"{name} ({count_ids})"
                self.ui.listWidgetUsers.addItem(text)
        else:
            self.current_user_list = self.users_data
            for idx, user in enumerate(self.current_user_list):
                name = f"{user.get('vorname', '')} {user.get('nachname', '')}".strip()
                text = f"{idx+1}: {name}"
                self.ui.listWidgetUsers.addItem(text)
        if self.ui.listWidgetUsers.count() > 0:
            self.ui.listWidgetUsers.setCurrentRow(0)
        else:
            self.clear_details()

    def clear_details(self):
        """Leert alle Detailfelder der UI."""
        self.ui.valueVorname.setText("")
        self.ui.valueNachname.setText("")
        self.ui.valueTelefon.setText("")
        self.ui.valueEmail.setText("")
        self.ui.valueCreatedAt.setText("")
        self.ui.valueUpdatedAt.setText("")
        self.ui.tableIDs.clearContents()
        self.ui.tableIDs.setRowCount(0)

    def display_user_details(self, index):
        """Aktualisiert die Detailfelder mit den Daten des ausgewählten Benutzers."""
        if index < 0 or index >= len(self.current_user_list):
            return
        user = self.current_user_list[index]
        self.ui.valueVorname.setText(user.get("vorname", ""))
        self.ui.valueNachname.setText(user.get("nachname", ""))
        self.ui.valueTelefon.setText(user.get("telefon", ""))
        self.ui.valueEmail.setText(user.get("email", ""))
        self.ui.valueCreatedAt.setText(user.get("created_at", ""))
        self.ui.valueUpdatedAt.setText(user.get("updated_at", ""))
        if self.ui.checkboxUnique.isChecked():
            ids = user.get("ids", [])
        else:
            ids = [user.get("id", "")]

        dm = self.market_widget().data_manager_ref
        self.ui.tableIDs.setRowCount(len(ids))
        for row, id_ in enumerate(ids):
            voll = dm.get_article_count(id_) if dm else 0
            teil = dm.get_partial_article_count(id_) if dm else 0
            offen = dm.get_open_article_count(id_) if dm else 0
            total = dm.get_article_sum(id_) if dm else 0.0
            self.ui.tableIDs.setItem(row, 0, QTableWidgetItem(str(id_)))
            self.ui.tableIDs.setItem(row, 1, QTableWidgetItem(str(voll)))
            self.ui.tableIDs.setItem(row, 2, QTableWidgetItem(str(teil)))
            self.ui.tableIDs.setItem(row, 3, QTableWidgetItem(str(offen)))
            self.ui.tableIDs.setItem(row, 4, QTableWidgetItem(f"{total:.2f}"))
