import sys
from pathlib import Path
from typing import Dict, List
from .base_data import BaseData
import uuid
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Dict, List, Optional
from copy import deepcopy
import uuid

sys.path.insert(0, Path(__file__).parent.parent.parent.parent.__str__())  # NOQA: E402 pylint: disable=[C0413]
from .data_class_definition import MainNumberDataClass, SellerDataClass, ArticleDataClass

@dataclass
class ChangeLogEntry:
    id: str
    timestamp: str
    action: str
    target: str
    description: str


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
        self._unsaved_changes: bool = False
        self._change_log: List[ChangeLogEntry] = []

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


    def _log_change(self, action: str, target: str, description: str):
        entry = ChangeLogEntry(
            id=str(uuid.uuid4()),
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            action=action,
            target=target,
            description=description
        )
        self._change_log.append(entry)
        self._unsaved_changes = True

    def update_article(self, stnr_id: str, artikelnummer: str, beschreibung: str, groesse: str, preis: str) -> Optional[ArticleDataClass]:
        table = self.get_main_number_tables().get(f"stnr{stnr_id}")
        if not table:
            raise ValueError(f"Keine Artikelliste für stnr{stnr_id} gefunden.")

        for article in table.data:
            if article.artikelnummer == artikelnummer:
                old_values = (article.beschreibung, article.groesse, article.preis)
                article.beschreibung = beschreibung
                article.groesse = groesse
                article.preis = preis
                article.updated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                self._log_change(
                    action="UPDATE",
                    target=f"stnr{stnr_id}:{artikelnummer}",
                    description=f"Artikel geändert von {old_values} zu ({beschreibung}, {groesse}, {preis})"
                )
                return article
        raise ValueError(f"Artikelnummer {artikelnummer} nicht gefunden in stnr{stnr_id}.")

    def delete_article(self, stnr_id: str, artikelnummer: str):
        return self.update_article(stnr_id, artikelnummer, "", "0", "0.00")

    def delete_seller(self, seller_id: str):
        for seller in self.get_seller_list():
            if seller.id == seller_id:
                old_data = deepcopy(seller)
                seller.vorname = ""
                seller.nachname = ""
                seller.telefon = ""
                seller.email = ""
                seller.passwort = ""
                seller.updated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                self._log_change(
                    action="DELETE",
                    target=f"verkaeufer:{seller_id}",
                    description=f"Verkäuferdaten gelöscht: {old_data}"
                )
                return seller
        raise ValueError(f"Verkäufer mit ID {seller_id} nicht gefunden.")

    def delete_article_list(self, stnr_id: str):
        table = self.get_main_number_tables().get(f"stnr{stnr_id}")
        if not table:
            raise ValueError(f"Keine Artikelliste für stnr{stnr_id} gefunden.")

        for article in table.data:
            article.beschreibung = ""
            article.groesse = "0"
            article.preis = "0.00"
            article.updated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        self._log_change(
            action="DELETE",
            target=f"stnr{stnr_id}",
            description="Alle Artikelinhalte gelöscht."
        )
        return table

    def delete_dataset(self, seller_id: str):
        self.delete_seller(seller_id)
        self.delete_article_list(seller_id)
        self._log_change(
            action="DELETE",
            target=f"dataset:{seller_id}",
            description="Kompletter Datensatz (Verkäufer + Artikelliste) gelöscht."
        )

    def validate_structure(self) -> bool:
        seller_ids = {seller.id for seller in self.get_seller_list()}
        stnr_ids = {table.name[4:] for table in self.get_main_number_list() if table.name.startswith("stnr")}
        return seller_ids == stnr_ids

    def has_unsaved_changes(self) -> bool:
        return self._unsaved_changes

    def get_change_log(self) -> List[Dict]:
        return [asdict(entry) for entry in self._change_log]

    def export_to_json(self) -> List[dict]:
        json_data = [
            asdict(self.export_header),
            asdict(self.base_info)
        ]
        for table in self.main_numbers_list:
            json_data.append(asdict(table))
        json_data.append(asdict(self.sellers))
        return json_data

