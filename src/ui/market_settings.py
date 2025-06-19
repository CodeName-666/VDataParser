from .base_ui import BaseUi
from .generated import MarketSettingUi
from PySide6.QtCore import QDate, QDateTime




class MarketSetting(BaseUi):

    def __init__(self, parent = None):
        super().__init__(parent)
        self.ui = MarketSettingUi()
        self.market = None
        self.default_settings = {}
        self.ui.setupUi(self)
        self.connect_signals()

    def connect_signals(self):
        """Verbindet die Signale der UI-Elemente mit den entsprechenden Methoden."""
        #self.ui.btnSaveSettings.clicked.connect(self.save_settings)
        #self.ui.btnResetSettings.clicked.connect(self.reset_settings)
        pass 

    def set_default_settings(self, settings: dict):
        self.default_settings = settings

    def setup_views(self, market_widget):
        """Initialisiert die Einstellungen für das MarketWidget."""
        self.market = market_widget
        self.load_settings()

    def load_settings(self):
        """Lädt die Einstellungen aus dem DataManager und aktualisiert die UI."""
        settings = self.market_widget().get_settings()
        
        if settings.is_all_empty():
            settings = self.default_settings

        max_stammnummern = settings.get('max_stammnummern', '')
        max_artikel = settings.get('max_artikel', '')
        datum_counter = settings.get('datum_counter', '')
        flohmarkt_nr = settings.get('flohmarkt_nr', '')
        psw_laenge = settings.get('psw_laenge', '') # Passwortlänge
        tabellen_prefix = settings.get('tabellen_prefix', '')
        verkaufer_liste = settings.get('verkaufer_liste', '')
        datum_flohmarkt = settings.get('datum_flohmarkt', '')
        max_user_ids = settings.get('max_user_ids', '')
    
        self.ui.spinMaxStammnummer.setValue(int(max_stammnummern) if max_stammnummern.isdigit() else 0)
        self.ui.spinMaxArtikel.setValue(int(max_artikel) if max_artikel.isdigit() else 0)
        self.ui.dateTimeEditFlohmarktCountDown.setDateTime(QDateTime.fromString(datum_counter))
        self.ui.spinFlohmarktNummer.setValue(int(flohmarkt_nr) if flohmarkt_nr.isdigit() else 0)
        self.ui.spinMaxIdPerUser.setValue(int(max_user_ids) if max_user_ids.isdigit() else 0)
        self.ui.spinPwLength.setValue(int(psw_laenge) if psw_laenge.isdigit() else 0)
        self.ui.lineEditTabellePrefix.setText(tabellen_prefix)
        self.ui.lineEditTabelleVerkaeufer.setText(verkaufer_liste)
        self.ui.dateTimeEditFlohmarkt.setDate(QDate.fromString(datum_flohmarkt))
    

    def save_settings(self):
        """Speichert die aktuellen Einstellungen in den DataManager."""
        settings = {
            'setting1': self.ui.lineEditSetting1.text(),
            'setting2': self.ui.lineEditSetting2.text(),
            # Weitere Einstellungen können hier gespeichert werden
        }
        self.market_widget().save_settings(settings)
        self.load_settings()


    def reset_settings(self):
        """Setzt die Einstellungen auf die Standardwerte zurück."""
        self.market_widget().reset_settings()
        self.load_settings()
        # Optional: Zeige eine Bestätigungsmeldung an
        

    def market_widget(self):
        """Gibt eine Referenz auf das MarketWidget zurück."""
        return self.market