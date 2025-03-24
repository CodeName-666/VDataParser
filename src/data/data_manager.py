import sys
from pathlib import Path
from typing import Dict, List
from .base_data import BaseData


sys.path.insert(0, Path(__file__).parent.parent.parent.parent.__str__())  # NOQA: E402 pylint: disable=[C0413]
from .data_class_definition import MainNumberDataClass, SellerDataClass



class DataManager(BaseData):
    """
    DataManager erbt von BaseData und erweitert die Funktionalität,
    indem er zusätzliche Aggregations-Logik implementiert.

    - Aggregiert Verkäufer (Seller) anhand ihrer E-Mail.
    - Ordnet MainNumberDataClass-Instanzen (stnr‑Tabellen) den jeweiligen Verkäufern zu.
    """

    def __init__(self, json_file_path: str, error_handler=None) -> None:
        # BaseData lädt und konvertiert die JSON-Daten in die entsprechenden Dataclasses.
        super().__init__(json_file_path, error_handler)
        self.aggregate_data()

    def aggregate_data(self):
        """
        Führt die Aggregation der Daten durch:
        
        1. Aggregation der Main-Number-Tables (z. B. "stnr1", "stnr2", etc.) in ein Dictionary.
        2. Gruppierung der Verkäufer (Seller) anhand ihrer E-Mail.
        3. Zuordnung der stnr‑Tabellen zu den Verkäufern, wenn die Nummer aus dem Tabellennamen in der Verkäufer-ID enthalten ist.
        """
        # Aggregation der Main-Number-Tables (stnr‑Tabellen)
        self.main_number_tables: Dict[str, MainNumberDataClass] = {}
        for main in self.main_numbers_list:
            if main.name.startswith("stnr"):
                self.main_number_tables[main.name] = main

        # Aggregation der Verkäufer (Seller) anhand der E-Mail-Adresse
        self.users: Dict[str, Dict] = {}  # Schlüssel: E-Mail, Wert: {"info": SellerDataClass, "ids": [Seller-ID], "stamms": [MainNumberDataClass,...]}
        for seller in self.get_seller_list():
            key = seller.email
            if key not in self.users:
                self.users[key] = {"info": seller, "ids": [seller.id], "stamms": []}
            else:
                if seller.id not in self.users[key]["ids"]:
                    self.users[key]["ids"].append(seller.id)

        # Zuordnung der stnr‑Tabellen zu den Verkäufern, wenn die Nummer im Namen übereinstimmt.
        for main in self.main_numbers_list:
            if main.name.startswith("stnr"):
                stnr_num = main.name[4:]  # extrahiert z. B. "1" aus "stnr1"
                for user in self.users.values():
                    if stnr_num in user["ids"]:
                        user["stamms"].append(main)
        return None

    def get_aggregated_users(self) -> Dict[str, Dict]:
        """
        Gibt die aggregierten Benutzer zurück.
        
        Rückgabeformat:
            {
                "<email>": {
                    "info": SellerDataClass,
                    "ids": [Seller-ID, ...],
                    "stamms": [MainNumberDataClass, ...]
                },
                ...
            }
        """
        return self.users

    def get_main_number_tables(self) -> Dict[str, MainNumberDataClass]:
        """
        Gibt die stnr‑Tabellen als Dictionary zurück.
        
        Schlüssel: Name der Tabelle (z. B. "stnr1")
        """
        return self.main_number_tables
