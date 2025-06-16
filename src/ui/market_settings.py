from .base_ui import BaseUi
from .generated import MarketSettingUi




class MarketSetting(BaseUi):

    def __init__(self, parent = None):
        super().__init__(parent)
        self.ui = MarketSettingUi()
        self.market = None
        self.ui.setupUi(self)

    def setup_views(self, market_widget):
        """Initialisiert die Einstellungen für das MarketWidget."""
        self.market = market_widget
        self.ui.btnSaveSettings.clicked.connect(self.save_settings)
        self.ui.btnResetSettings.clicked.connect(self.reset_settings)
        self.load_settings()

    def load_settings(self):
        """Lädt die Einstellungen aus dem DataManager und aktualisiert die UI."""
        settings = self.market_widget().get_settings()
        if settings:
            self.ui.lineEditSetting1.setText(settings.get('setting1', ''))
            self.ui.lineEditSetting2.setText(settings.get('setting2', ''))
            # Weitere Einstellungen können hier geladen werden
        else:
            self.ui.lineEditSetting1.clear()
            self.ui.lineEditSetting2.clear()

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
        self.ui.statusLabel.setText("Einstellungen wurden auf Standardwerte zurückgesetzt.")

    def market_widget(self):
        """Gibt eine Referenz auf das MarketWidget zurück."""
        return self.market