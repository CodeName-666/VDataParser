from dataclasses import dataclass,field, fields
from typing import List, Optional


@dataclass
class CoordinatesConfig:
    x1: float
    y1: float
    x2: float
    y2: float
    x3: float
    y3: float
    font_size: int = 12

@dataclass
class ChangeLogEntry:
    id: str
    timestamp: str
    action: str
    target: str
    description: str
    old_value: Optional[dict] = None  # hinzugefügt für Rücksetzfunktion

@dataclass
class HeaderDataClass:
    type: str = "header"
    version: str = "5.2.1"
    comment: str = "Export to JSON plugin for PHPMyAdmin"

@dataclass
class BaseInfoDataClass:
    type: str = "database"
    name: str = ""

@dataclass
class SettingsContentDataClass:
    max_stammnummern: str = ""
    max_artikel: str = ""
    datum_counter: str = ""
    flohmarkt_nr: str = ""
    psw_laenge: str = ""
    tabellen_prefix: str = ""
    verkaufer_liste: str = ""
    max_user_ids: str = ""
    datum_flohmarkt: str = ""   
    flohmarkt_aktiv:str = ""
    login_aktiv:str = ""

@dataclass
class SettingDataClass:
    type: str = "table"
    name: str = "einstellungen"
    database: str = ""
    data: List[SettingsContentDataClass] = field(default_factory=list)

    def is_all_empty(self) -> bool:
        if not self.data:
            return True  # Leere Liste gilt als 'alles leer'

        settings = self.data[0]
        for field_ in fields(settings):
            value = getattr(settings, field_.name)
            if value not in ("", 0, None):
                return False
        return True
   
    def __post_init__(self):
        converted_settings = []
        for setting in self.data:
            if isinstance(setting, dict):
                cSetting = SettingsContentDataClass(**setting)
                converted_settings.append(cSetting)
        
        self.data = converted_settings
       #elif not isinstance(self.data, SettingsContentDataClass):
       #    raise TypeError("data must be a SettingsDataClassList or a dict")

@dataclass
class ArticleDataClass:
    artikelnummer: str = ""
    beschreibung: str = ""
    groesse: str  = ""
    preis: str = ""
    created_at: str = ""
    updated_at: str = ""

@dataclass
class MainNumberDataClass:
    type: str = "table"
    name: str = ""
    database: str = ""
    data: List[ArticleDataClass] = field(default_factory=list)

    def __post_init__(self):
        converted_articles = []
        for article in self.data:
            if isinstance(article, dict):
                converted_article = ArticleDataClass(
                    artikelnummer=str(article.get('artikelnummer', '')),
                    beschreibung=str(article.get('beschreibung', '')),
                    groesse=str(article.get('groesse', '')),
                    preis=str(article.get('preis', '')),
                    created_at=str(article.get('created_at', '')),
                    updated_at=str(article.get('updated_at', ''))
                )
                converted_articles.append(converted_article)
            else:
                converted_articles.append(article)
        self.data = converted_articles

@dataclass
class SellerDataClass:
    id: str = ""
    vorname: str = ""
    nachname: str = ""
    telefon: str = ""
    email: str = ""
    passwort: str = ""
    created_at: str = ""
    updated_at: str = ""

@dataclass
class SellerListDataClass:
    type: str = "table"
    name: str = "verkaeufer"
    database: str = ""
    data: List[SellerDataClass] = field(default_factory=list)

    def __post_init__(self):
        converted_sellers = []
        for seller in self.data:
            if isinstance(seller, dict):
                converted_seller = SellerDataClass(
                    id=str(seller.get('id', '')),
                    vorname=str(seller.get('vorname', '')),
                    nachname=str(seller.get('nachname', '')),
                    telefon=str(seller.get('telefon', '')),
                    email=str(seller.get('email', '')),
                    passwort=str(seller.get('passwort', '')),
                    created_at=str(seller.get('created_at', '')),
                    updated_at=str(seller.get('updated_at', ''))
                )
                converted_sellers.append(converted_seller)
            else:
                converted_sellers.append(seller)
        self.data = converted_sellers

@dataclass
class JSONData:
    export_header: HeaderDataClass
    base_info: BaseInfoDataClass
    settings: SettingDataClass
    main_numbers_list: List[MainNumberDataClass]
    sellers: SellerListDataClass
