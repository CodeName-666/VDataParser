from .base_ui import BaseUi
from .generated import UserInfoUi

from data import DataManager



class UserInfo(BaseUi):

    def __init__(self, parent = None):
        super().__init__(parent)
        self.ui = UserInfoUi()
        self.ui.setupUi(self)
        self.setup_connections()


    def set_data(self, data_manager: DataManager):
        """Setzt den DataManager und führt die Initialisierung durch."""
        self.data_manager = data_manager
        # Erhalte die Verkäuferdaten aus dem DataManager
        # Für den nicht aggregierten Modus: konvertiere jeden SellerDataClass-Eintrag in ein Dictionary.
        self.users = [self.convert_seller_to_dict(seller) for seller in self.data_manager.get_seller_list()]
        
        # Für den aggregierten Modus: hole die aggregierten Daten (als Dictionary) und konvertiere sie in eine Liste.
        aggregated_dict = self.data_manager.get_aggregated_users()  # {email: {info: SellerDataClass, ids: [...], stamms: [...]}}
        self.aggregated_users = [self.convert_aggregated_user(email, data) for email, data in aggregated_dict.items()]
        
        # Standardmäßig werden alle (nicht aggregierten) Einträge angezeigt.
        self.current_user_list = self.users
        
        
        self.refresh_user_list()
        if self.ui.listWidgetUsers.count() > 0:
            self.ui.listWidgetUsers.setCurrentRow(0)


    def convert_seller_to_dict(self, seller):
        """Konvertiert einen SellerDataClass-Eintrag in ein Dictionary mit den benötigten Schlüsseln."""
        return {
            "vorname": seller.vorname,
            "nachname": seller.nachname,
            "telefon": seller.telefon,
            "email": seller.email,
            "created_at": seller.created_at,
            "updated_at": seller.updated_at,
            "id": seller.id
        }
    
    def convert_aggregated_user(self, email, data):
        """
        Konvertiert einen aggregierten Seller aus dem DataManager in das
        Format, das von der UI erwartet wird.
        """
        seller = data["info"]
        return {
            "vorname": seller.vorname,
            "nachname": seller.nachname,
            "telefon": seller.telefon,
            "email": seller.email,
            "created_at": seller.created_at,
            "updated_at": seller.updated_at,
            "ids": data["ids"]
        }

    def setup_connections(self):
        """Verbindet die UI-Signale mit den entsprechenden Methoden."""
        self.ui.checkboxUnique.toggled.connect(self.refresh_user_list)
        self.ui.listWidgetUsers.currentRowChanged.connect(self.display_user_details)

    def refresh_user_list(self):
        """Aktualisiert die ListWidget-Anzeige basierend auf dem Status der Checkbox."""
        self.ui.listWidgetUsers.clear()
        if self.ui.checkboxUnique.isChecked():
            self.current_user_list = self.aggregated_users
            for user in self.current_user_list:
                count_ids = len(user.get("ids", []))
                text = f"{user.get('vorname', '')} {user.get('nachname', '')} ({count_ids})"
                self.ui.listWidgetUsers.addItem(text)
        else:
            self.current_user_list = self.users
            for user in self.current_user_list:
                text = f"{user.get('vorname', '')} {user.get('nachname', '')}"
                self.ui.listWidgetUsers.addItem(text)
        if self.ui.listWidgetUsers.count() > 0:
            self.ui.listWidgetUsers.setCurrentRow(0)
        else:
            self.clear_details()

    def clear_details(self):
        """Leert alle Detailfelder."""
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
            # Aggregierter Modus: Alle IDs, durch "|" getrennt
            ids = user.get("ids", [])
            self.ui.valueIDs.setText("|".join(ids))
        else:
            self.ui.valueIDs.setText(user.get("id", ""))
