import sys
from pathlib import Path
from typing import Dict, List, Optional
from copy import deepcopy
import uuid
from dataclasses import asdict, dataclass, fields
from datetime import datetime
try:
    from PySide6.QtCore import QObject, Signal
except Exception:  # pragma: no cover - optional PySide6
    class QObject:  # type: ignore
        pass

    class Signal:  # type: ignore
        def __init__(self, *args, **kwargs) -> None:
            pass

        def emit(self, *args, **kwargs) -> None:
            pass

        def connect(self, *_a, **_k) -> None:
            pass

sys.path.insert(0, Path(__file__).parent.parent.parent.parent.__str__())  # NOQA: E402 pylint: disable=[C0413]
from .base_data import BaseData
from objects import (
    MainNumberDataClass,
    SellerDataClass,
    ArticleDataClass,
    ChangeLogEntry,
    SettingsContentDataClass)


class DataManager(QObject, BaseData):
    """
    DataManager inherits from BaseData and extends its functionality by implementing additional aggregation logic.

    - Aggregates sellers based on their email addresses.
    - Assigns MainNumberDataClass instances (stnr tables) to the respective sellers.
    """
    status_info = Signal(str, str)
    data_loaded = Signal(object)  # Signal to notify when data is loaded

    def __init__(self, json_file_path: str = None, error_handler=None) -> None:
        """
        Initializes the DataManager instance.

        Args:
            json_file_path (str): Path to the JSON data file.
            error_handler (optional): Optional error handler callback.
        """
        # BaseData loads and converts JSON data into the corresponding dataclasses.
        QObject.__init__(self)  # Initialize QObject first
        BaseData.__init__(self, json_file_path, error_handler)

        self._unsaved_changes: bool = False
        self._change_log: List[ChangeLogEntry] = []

    @staticmethod
    def seller_is_empty(seller: SellerDataClass) -> bool:
        """Return ``True`` if the seller has no identifying information."""
        return not any(
            getattr(seller, attr).strip() for attr in [
                "vorname",
                "nachname",
                "telefon",
                "email",
                "passwort",
            ]
        )

    def convert_seller_to_dict(self, seller: SellerDataClass) -> dict:
        """
        Converts a SellerDataClass entry into a dictionary with required keys.

        Args:
            seller (SellerDataClass): A seller data entry.

        Returns:
            dict: Dictionary containing seller information.
        """
        empty = self.seller_is_empty(seller)
        return {
            "vorname": "<Leer>" if empty else seller.vorname,
            "nachname": "" if empty else seller.nachname,
            "telefon": seller.telefon,
            "email": seller.email,
            "created_at": seller.created_at,
            "updated_at": seller.updated_at,
            "id": seller.id
        }

    def convert_aggregated_user(self, email: str, data: dict) -> dict:
        """
        Converts an aggregated seller into the format expected by the UI.

        Args:
            email (str): The seller's email.
            data (dict): Aggregated data containing "info" and "ids".

        Returns:
            dict: UI-friendly seller data.
        """
        seller = data["info"]
        empty = self.seller_is_empty(seller)
        return {
            "vorname": "<Leer>" if empty else seller.vorname,
            "nachname": "" if empty else seller.nachname,
            "telefon": seller.telefon,
            "email": seller.email,
            "created_at": seller.created_at,
            "updated_at": seller.updated_at,
            "ids": data["ids"]
        }

    def _aggregate_main_number_tables(self) -> Dict[str, MainNumberDataClass]:
        """
        Aggregates all MainNumberDataClass instances whose names start with "stnr" into a dictionary.

        Returns:
            Dict[str, MainNumberDataClass]: Dictionary with table name as key and instance as value.
        """
        main_number_tables: Dict[str, MainNumberDataClass] = {}
        for main in self.main_numbers_list:
            if main.name.startswith("stnr"):
                main_number_tables[main.name] = main
        return main_number_tables

    def _aggregate_sellers(self) -> Dict[str, Dict]:
        """
        Groups sellers based on their email address.

        Returns:
            Dict[str, Dict]: Dictionary with email as key and a dict containing "info", "ids", and "stamms" as value.
        """
        users: Dict[str, Dict] = {}
        empty_key = "<LEER>"

        def is_empty(s: SellerDataClass) -> bool:
            return not any(
                getattr(s, attr).strip() for attr in [
                    "vorname",
                    "nachname",
                    "telefon",
                    "email",
                    "passwort",
                ]
            )

        for seller in self.get_seller_as_list():
            key = seller.email if not is_empty(seller) else empty_key
            if key not in users:
                users[key] = {"info": seller, "ids": [seller.id], "stamms": []}
            else:
                if seller.id not in users[key]["ids"]:
                    users[key]["ids"].append(seller.id)
        users = self.__move_empty_to_end(users)
        
        return users

    def _assign_main_numbers_to_sellers(self) -> Dict[str, Dict]:
        """
        Assigns stnr tables to sellers if the number in the table name is in the seller's IDs.

        Returns:
            Dict[str, Dict]: Sellers dictionary with assigned stnr tables in "stamms".
        """
        sellers = self._aggregate_sellers()
        empty_key = "<LEER>"
        for main in self.main_numbers_list:
            if not main.name.startswith("stnr"):
                continue
            stnr_num = main.name[4:]  # e.g. "1" from "stnr1"
            assigned = False
            for user in sellers.values():
                if stnr_num in user["ids"]:
                    user["stamms"].append(main)
                    assigned = True
                    break
            if not assigned:
                if empty_key not in sellers:
                    sellers[empty_key] = {
                        "info": SellerDataClass(),
                        "ids": [],
                        "stamms": [],
                    }
                sellers[empty_key]["ids"].append(stnr_num)
                sellers[empty_key]["stamms"].append(main)

        sellers = self.__move_empty_to_end(sellers)
        return sellers

    def get_aggregated_users(self) -> Dict[str, Dict]:
        """
        Returns the aggregated user information.

        Returns:
            Dict[str, Dict]: Aggregated users grouped by email with "info", "ids", and "stamms".
        """
        sellers = self._assign_main_numbers_to_sellers()
        sellers = self.__move_empty_to_end(sellers)
        return sellers

    def get_main_number_tables(self) -> Dict[str, MainNumberDataClass]:
        """
        Returns stnr tables as a dictionary.

        Returns:
            Dict[str, MainNumberDataClass]: Dictionary with table name (e.g., "stnr1") as key.
        """
        return self._aggregate_main_number_tables()

    def get_users_data(self) -> List[dict]:
        """
        Returns seller data as a list of dictionaries (non-aggregated).

        Returns:
            List[dict]: List of seller dictionaries.
        """
        return [self.convert_seller_to_dict(seller) for seller in self.get_seller_as_list()]

    def _article_status_counts(self, stnr_id: str) -> Dict[str, int]:
        """Return counts for complete, partial and open articles for ``stnr_id``."""
        tables = self.get_main_number_tables()
        key = stnr_id if stnr_id.startswith("stnr") else f"stnr{stnr_id}"
        table = tables.get(key)
        counts = {"vollstaendig": 0, "teilweise": 0, "offen": 0}
        if not table:
            return counts
        for article in getattr(table, "data", []):
            desc = bool(getattr(article, "beschreibung", "").strip())
            preis_raw = getattr(article, "preis", None)
            preis = preis_raw not in (None, "", "None")
            if desc and preis:
                counts["vollstaendig"] += 1
            elif desc or preis:
                counts["teilweise"] += 1
            else:
                counts["offen"] += 1
        return counts

    def get_article_count(self, stnr_id: str) -> int:
        """Return the number of *complete* articles for the given ``stnr`` table."""
        return self._article_status_counts(stnr_id)["vollstaendig"]

    def get_partial_article_count(self, stnr_id: str) -> int:
        """Return the number of partially filled articles for ``stnr_id``."""
        return self._article_status_counts(stnr_id)["teilweise"]

    def get_open_article_count(self, stnr_id: str) -> int:
        """Return the number of open (empty) articles for ``stnr_id``."""
        return self._article_status_counts(stnr_id)["offen"]

    def get_article_sum(self, stnr_id: str) -> float:
        """Return the total price of all articles for the given ``stnr`` table."""
        tables = self.get_main_number_tables()
        key = stnr_id if stnr_id.startswith("stnr") else f"stnr{stnr_id}"
        table = tables.get(key)
        if not table:
            return 0.0
        total = 0.0
        for article in getattr(table, "data", []):
            try:
                total += float(article.preis)
            except (ValueError, TypeError):
                continue
        return round(total, 2)

    def get_aggregated_users_data(self) -> List[dict]:
        """
        Returns aggregated seller data as a list of dictionaries.

        Returns:
            List[dict]: List of aggregated seller data dictionaries.
        """
        aggregated_dict = self.get_aggregated_users()
        result = [self.convert_aggregated_user(email, data) for email, data in aggregated_dict.items()]
        return result

    def _log_change(self, action: str, target: str, description: str, old_value: Optional[dict] = None):
        """
        Logs a change action for audit purposes.

        Args:
            action (str): The type of action performed.
            target (str): The target of the action.
            description (str): A description of the change.
        """
        entry = ChangeLogEntry(
            id=str(uuid.uuid4()),
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            action=action,
            target=target,
            description=description,
            old_value=old_value
        )
        self._change_log.append(entry)
        self._unsaved_changes = True

    def update_article(self, stnr_id: str, artikelnummer: str, beschreibung: str, groesse: str, preis: str) -> Optional[ArticleDataClass]:
        """
        Updates an article within the given stnr table.

        Args:
            stnr_id (str): ID of the stnr table.
            artikelnummer (str): Article number.
            beschreibung (str): New description.
            groesse (str): New size.
            preis (str): New price.

        Returns:
            Optional[ArticleDataClass]: The updated ArticleDataClass instance.

        Raises:
            ValueError: If the stnr table or article is not found.
        """
        table = self.get_main_number_tables().get(f"stnr{stnr_id}")
        if not table:
            raise ValueError(f"Keine Artikelliste für stnr{stnr_id} gefunden.")
        for article in table.data:
            if article.artikelnummer == artikelnummer:
                old_values = (article.beschreibung,
                              article.groesse, article.preis)
                article.beschreibung = beschreibung
                article.groesse = groesse
                article.preis = preis
                article.updated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                self._log_change(
                    action="UPDATE",
                    target=f"stnr{stnr_id}:{artikelnummer}",
                    description=(
                        f"Artikel geändert von {old_values} zu ({beschreibung}, {groesse}, {preis})"
                    ),
                    old_value={
                        "beschreibung": old_values[0],
                        "groesse": old_values[1],
                        "preis": old_values[2],
                    },
                )
                return article
        raise ValueError(
            f"Artikelnummer {artikelnummer} nicht gefunden in stnr{stnr_id}.")

    def delete_article(self, stnr_id: str, artikelnummer: str):
        """
        Deletes an article by updating its properties to empty/default values.

        Args:
            stnr_id (str): ID of the stnr table.
            artikelnummer (str): Article number to delete.

        Returns:
            Optional[ArticleDataClass]: The article after deletion.
        """
        return self.update_article(stnr_id, artikelnummer, "", "0", "0.00")

    def delete_seller(self, seller_id: str):
        """
        Deletes a seller by clearing out their data.

        Args:
            seller_id (str): The ID of the seller to delete.

        Returns:
            SellerDataClass: The seller instance with cleared data.

        Raises:
            ValueError: If no seller with the given ID is found.
        """
        for seller in self.get_seller_as_list():
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
                    description=f"Verkäuferdaten gelöscht: {old_data}",
                    old_value=asdict(old_data)
                )
                return seller
        raise ValueError(f"Verkäufer mit ID {seller_id} nicht gefunden.")

    def delete_article_list(self, stnr_id: str):
        """
        Deletes all articles in the specified stnr table by resetting their values.

        Args:
            stnr_id (str): ID of the stnr table.

        Returns:
            MainNumberDataClass: The stnr table after articles have been cleared.

        Raises:
            ValueError: If no stnr table with the given ID is found.
        """
        table = self.get_main_number_tables().get(f"stnr{stnr_id}")
        if not table:
            raise ValueError(f"Keine Artikelliste für stnr{stnr_id} gefunden.")
        old_articles = [asdict(article) for article in table.data]
        for article in table.data:
            article.beschreibung = ""
            article.groesse = "0"
            article.preis = "0.00"
            article.updated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self._log_change(
            action="DELETE",
            target=f"stnr{stnr_id}",
            description="Alle Artikelinhalte gelöscht.",
            old_value={"articles": old_articles}
        )
        return table

    def delete_dataset(self, seller_id: str):
        """
        Deletes the complete dataset (seller and their article list) based on seller ID.

        Args:
            seller_id (str): The ID of the seller whose dataset should be deleted.
        """
        old_seller = next(
            (deepcopy(s) for s in self.get_seller_as_list() if s.id == seller_id),
            None,
        )
        table = self.get_main_number_tables().get(f"stnr{seller_id}")
        old_articles = [asdict(a) for a in table.data] if table else []
        self.delete_seller(seller_id)
        self.delete_article_list(seller_id)
        self._log_change(
            action="DELETE",
            target=f"dataset:{seller_id}",
            description="Kompletter Datensatz (Verkäufer + Artikelliste) gelöscht.",
            old_value={
                "seller": asdict(old_seller) if old_seller else None,
                "articles": old_articles,
            }
        )

    def validate_structure(self) -> bool:
        """
        Validates that the structure is consistent by comparing seller IDs with stnr table IDs.

        Returns:
            bool: True if seller IDs match stnr table IDs, False otherwise.
        """
        seller_ids = {seller.id for seller in self.get_seller_as_list()}
        stnr_ids = {table.name[4:] for table in self.get_main_number_as_list(
        ) if table.name.startswith("stnr")}
        return seller_ids == stnr_ids

    def has_unsaved_changes(self) -> bool:
        """
        Checks if there are unsaved changes.

        Returns:
            bool: True if there are unsaved changes, False otherwise.
        """
        return self._unsaved_changes

    def get_change_log(self) -> List[Dict]:
        """
        Retrieves the change log as a list of dictionaries.

        Returns:
            List[Dict]: List containing the change log entries.
        """
        return [asdict(entry) for entry in self._change_log]

    def export_to_json(self) -> List[dict]:
        """
        Exports the data to a JSON-compatible list of dictionaries.

        Returns:
            List[dict]: A list of dictionaries representing the header, base info, tables, and sellers.
        """
        json_data = [
            asdict(self.export_header),
            asdict(self.base_info),
            asdict(self.settings)
        ]
        for table in self.main_numbers_list:
            json_data.append(asdict(table))
        json_data.append(asdict(self.sellers))
        return json_data

    def load(self, path_or_url: str) -> bool:
        """
        Load JSON data from a file or URL and parse it into data classes.

        Args:
            path_or_url (str): Path to the JSON file or URL.
        """
        ret = super().load(path_or_url)
        if ret:
            self.data_loaded.emit(self)
        return ret

    def reset_change(self, change_id: str) -> bool:
        """Revert a change from the log identified by ``change_id``."""
        entry = next((e for e in self._change_log if e.id == change_id), None)
        if not entry or not entry.old_value:
            return False

        if entry.target.startswith("stnr"):
            # Artikel zurücksetzen
            parts = entry.target.split(":")
            if len(parts) == 2:
                stnr_id, artikelnummer = parts[0][4:], parts[1]
                table = self.get_main_number_tables().get(f"stnr{stnr_id}")
                if table:
                    for article in table.data:
                        if article.artikelnummer == artikelnummer:
                            article.beschreibung = entry.old_value.get(
                                "beschreibung", "")
                            article.groesse = entry.old_value.get(
                                "groesse", "0")
                            article.preis = entry.old_value.get(
                                "preis", "0.00")
                            article.updated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            return True

        elif entry.target.startswith("verkaeufer:"):
            seller_id = entry.target.split(":")[1]
            for seller in self.get_seller_as_list():
                if seller.id == seller_id:
                    seller.vorname = entry.old_value.get("vorname", "")
                    seller.nachname = entry.old_value.get("nachname", "")
                    seller.telefon = entry.old_value.get("telefon", "")
                    seller.email = entry.old_value.get("email", "")
                    seller.passwort = entry.old_value.get("passwort", "")
                    seller.updated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    return True
        elif entry.target.startswith("settings:"):
            key = entry.target.split(":")[1]
            if hasattr(self.settings.data, key) and key in entry.old_value:
                setattr(self.settings.data, key, entry.old_value[key])
                return True

        return False
    
    def __move_empty_to_end(self, data_list):
        empty_key = "<LEER>"
        if empty_key in data_list:
            empty_entry = data_list.pop(empty_key)
            data_list[empty_key] = empty_entry
        return data_list

    def update_setting(self, key: str, new_value: str) -> bool:
        """Update a setting value and log the modification."""
        if hasattr(self.settings.data, key):
            old_value = getattr(self.settings.data, key)
            setattr(self.settings.data, key, new_value)
            self._log_change(
                action="UPDATE",
                target=f"settings:{key}",
                description=f"Setting '{key}' geändert von {old_value} zu {new_value}",
                old_value={key: old_value}
            )
            return True
        return False
    
    def settings_available(self) -> bool:
        return not self.settings.is_all_empty()

   
    def set_new_settings(self, new_settings: SettingsContentDataClass):
        """
        Setzt die Default-Werte für die Settings (überschreibt alle Felder).
        """
        # Wenn noch keine Settings vorhanden sind, neu anlegen und Änderungen protokollieren
        if not self.settings.data:
            self.settings.data.append(new_settings)
            for field_ in fields(new_settings):
                value = getattr(new_settings, field_.name)
                self._log_change(
                    action="CREATE",
                    target=f"settings:{field_.name}",
                    description=f"Setting '{field_.name}' auf {value} gesetzt",
                )
        else:
            # Ansonsten alle Felder der ersten Settings-Instanz überschreiben und Änderungen loggen
            current_settings = self.settings.data[0]
            for field_ in fields(new_settings):
                old_value = getattr(current_settings, field_.name)
                new_value = getattr(new_settings, field_.name)
                if old_value != new_value:
                    setattr(current_settings, field_.name, new_value)
                    self._log_change(
                        action="UPDATE",
                        target=f"settings:{field_.name}",
                        description=f"Setting '{field_.name}' geändert von {old_value} zu {new_value}",
                        old_value={field_.name: old_value}
                    )

        self.synchornize_data_class_change_to_json()
            
   
    def reset_all_changes(self) -> int:
        """Reset all logged changes and return the number of reverted entries."""
        # Wichtig: Um Konflikte zu vermeiden, rückwärts iterieren
        successful_resets = 0
        for entry in reversed(self._change_log):
            if self.reset_change(entry.id):
                successful_resets += 1
        self._change_log.clear()
        self._unsaved_changes = True  # weil Änderungen am Zustand erfolgt sind
        return successful_resets


    def synchornize_data_class_change_to_json(self):
        self.json_data = self.export_to_json()
