from dataclasses import dataclass, field
from typing import List

@dataclass
class HeaderDataClass:
    type: str
    version: str
    comment: str

@dataclass
class BaseInfoDataClass:
    type:str 
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
        self.data = [ArticleDataClass(**article) for article in self.data if type(article) == dict ]

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
        self.data = [SellerDataClass(**seller_data) for seller_data in self.data if type(seller_data) == dict]

      

@dataclass
class JSONData:
    export_header: HeaderDataClass
    base_info: BaseInfoDataClass
    main_numbers_list: List[MainNumberDataClass]
    sellers: SellerListDataClass  