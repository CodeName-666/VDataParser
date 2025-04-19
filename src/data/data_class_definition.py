from dataclasses import dataclass, field
from typing import List


@dataclass
class ChangeLogEntry:
    id: str
    timestamp: str
    action: str
    target: str
    description: str

@dataclass
class HeaderDataClass:
    type: str
    version: str
    comment: str

@dataclass
class BaseInfoDataClass:
    type: str 
    name: str

@dataclass
class ArticleDataClass:
    artikelnummer: str
    beschreibung: str
    groesse: str
    preis: str
    created_at: str
    updated_at: str

@dataclass
class MainNumberDataClass:
    type: str
    name: str
    database: str
    data: List[ArticleDataClass]

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
    id: str
    vorname: str
    nachname: str
    telefon: str
    email: str
    passwort: str
    created_at: str
    updated_at: str

@dataclass
class SellerListDataClass:
    type: str
    name: str
    database: str
    data: List[SellerDataClass]

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
    main_numbers_list: List[MainNumberDataClass]
    sellers: SellerListDataClass
