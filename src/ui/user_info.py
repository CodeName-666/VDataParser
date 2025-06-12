from .base_ui import BaseUi
from .generated import UserInfoUi

class UserInfo(BaseUi):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = UserInfoUi()
        self.ui.setupUi(self)
        self.setup_signals()

    def setup_views(self):
        """Setzt den DataManager und initialisiert die Anzeige."""
        self.users_data = self.market_widget().get_user_data()
        self.aggregated_users_data = self.market_widget().get_aggregated_user_data()

        # Standardmäßig werden die nicht aggregierten Einträge angezeigt.
        self.current_user_list = self.users_data

        self.refresh_user_list()
        if self.ui.listWidgetUsers.count() > 0:
            self.ui.listWidgetUsers.setCurrentRow(0)


    def market_widget(self):
        return self.parent().parent().parent().parent()

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

                text = f"{user.get('vorname', '')} {user.get('nachname', '')} ({count_ids})"
                self.ui.listWidgetUsers.addItem(text)
        else:
            self.current_user_list = self.users_data
            for user in self.current_user_list:
                text = f"{user.get('vorname', '')} {user.get('nachname', '')}"
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
        self.ui.valueIDs.setText("")

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
            # Aggregierter Modus: Alle IDs, kommasepariert
            ids = user.get("ids", [])
            self.ui.valueIDs.setText(", ".join(ids))
        else:
            self.ui.valueIDs.setText(user.get("id", ""))
