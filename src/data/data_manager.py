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

    def _aggregate_main_number_tables(self):
        """
        Aggregiert alle MainNumberDataClass-Instanzen, deren Name mit "stnr" beginnt,
        in ein Dictionary.
        """
        main_number_tables: Dict[str, MainNumberDataClass] = {}
        for main in self.main_numbers_list:
            if main.name.startswith("stnr"):
                main_number_tables[main.name] = main

        return main_number_tables

    def _aggregate_sellers(self):
        """
        Gruppiert die Verkäufer anhand ihrer E-Mail-Adresse.
        
        Es entsteht ein Dictionary, in dem der Schlüssel die E-Mail ist und
        der Wert ein Dictionary mit "info" (SellerDataClass),
        "ids" (Liste der Verkäufer-IDs) und "stamms" (später zugeordnete stnr‑Tabellen) enthält.
        """
        users: Dict[str, Dict] = {}
        for seller in self.get_seller_list():
            key = seller.email
            if key not in users:
                users[key] = {"info": seller, "ids": [seller.id], "stamms": []}
            else:
                if seller.id not in users[key]["ids"]:
                    users[key]["ids"].append(seller.id)
        return users

    def _assign_main_numbers_to_sellers(self):
        """
        Ordnet die stnr‑Tabellen den Verkäufern zu, wenn die Nummer im Tabellennamen 
        in der Liste der Verkäufer-IDs enthalten ist.
        """
        sellers = self._aggregate_sellers()

        for main in self.main_numbers_list:
            if main.name.startswith("stnr"):
                stnr_num = main.name[4:]  # z. B. "1" aus "stnr1"
                for user in sellers.values():
                    if stnr_num in user["ids"]:
                        user["stamms"].append(main)
        return sellers

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
        return self._assign_main_numbers_to_sellers()

    def get_main_number_tables(self) -> Dict[str, MainNumberDataClass]:
        """
        Gibt die stnr‑Tabellen als Dictionary zurück.
        
        Schlüssel: Name der Tabelle (z. B. "stnr1")
        """
        return self._aggregate_main_number_tables()
