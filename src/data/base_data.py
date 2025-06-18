# --- START OF FILE base_data.py ---

from typing import Optional, Callable, Dict, List, Any # Added Any
import sys
import time
from pathlib import Path # Import Path from pathlib

from .json_handler import JsonHandler
from log import CustomLogger, LogType
from objects.data_class_definition import * 



class BaseData(JsonHandler, JSONData):
    """
    Handles loading, parsing, and verifying the base JSON data structure.
    Acts as a singleton. Inherits JSON loading/logging from JsonHandler.
    """

    def __init__(self, json_file_path: str = None, logger: Optional[CustomLogger] = None) -> None:
        """
        Initializes BaseData by loading JSON and parsing it into data classes.

        Args:
            json_file_path (str): Path or URL to the main JSON data file.
            logger (Optional[CustomLogger]): Logger instance for logging.
        """
        # Initialize JsonHandler first to load data and set up logger
        # The logger passed here will be available as self.logger
        super().__init__(json_path_or_data=json_file_path, logger=logger)


        # Check if data loading was successful in JsonHandler's __init__
        if self.json_data is None:
            self._log("ERROR", f"BaseData initialization failed: Could not load JSON data from {json_file_path}.")
            # Initialize JSONData with defaults even if loading failed, to prevent AttributeErrors later
            JSONData.__init__(self, export_header=HeaderDataClass(), base_info=BaseInfoDataClass(),
                              settings=SettingDataClass(), main_numbers_list=[], sellers=SellerListDataClass())
            return # Stop further processing if data loading failed
        
        # Proceed with parsing if data loaded successfully
        self._parse_json_data()


    def _log(self, level: str, message: str, on_verbose: bool = False) -> None:
        """ Helper method for conditional logging within BaseData. """
        # Reuse the helper logic, checking self.logger
        if self.logger and CustomLogger:
            log_method = getattr(self.logger, level.lower(), None)
            if log_method and callable(log_method):
                 try:
                     if level.lower() in ["debug", "info", "warning", "error"]:
                          log_method(message, verbose=on_verbose)
                     else:
                          log_method(message)
                 except Exception as e:
                      print(f"BASE_DATA LOGGING FAILED ({level}): {message} | Error: {e}", file=sys.stderr)


    def _parse_json_data(self) -> bool:
        """ Parses the loaded self.json_data into the data class structure. """
        
        ret: bool = False
        self._log("INFO", "Parsing loaded JSON data into data classes...")
        json_data = self.get_data() # Already loaded by JsonHandler.__init__

        # Ensure json_data is a list as expected by the original logic
        if not isinstance(json_data, list):
             self._log("ERROR", f"JSON data structure error: Expected a List, got {type(json_data).__name__}. Cannot parse.")
             # Initialize JSONData with defaults
             JSONData.__init__(self, export_header=HeaderDataClass(), base_info=BaseInfoDataClass(),
                              settings=SettingDataClass(), main_numbers_list=[], sellers=SellerListDataClass())
             return ret

        try:
            # Use .get() with default values for safe access
            header_dict = json_data[0] if len(json_data) >= 1 and isinstance(json_data[0], dict) else {}
            _export_header = HeaderDataClass(**header_dict)

            base_info_dict = json_data[1] if len(json_data) >= 2 and isinstance(json_data[1], dict) else {}
            _base_info = BaseInfoDataClass(**base_info_dict)
            
            settings_dict = json_data[2] if len(json_data) >= 3 and isinstance(json_data[2], dict) else {}
            _settings= SettingDataClass(**settings_dict)

            _main_numbers = []
            _sellers_dict = {}
            if len(json_data) >= 4:
                # Assume main numbers are all dicts between index 2 and the last element
                main_number_dicts = [item for item in json_data[3:-1] if isinstance(item, dict)]
                _main_numbers = [MainNumberDataClass(**table) for table in main_number_dicts]
                # Log if non-dict items were skipped
                skipped_mn = len(json_data[3:-1]) - len(main_number_dicts)
                if skipped_mn > 0:
                     self._log("WARNING", f"Skipped {skipped_mn} non-dictionary items in main numbers section.")

                # Sellers are the last element, if it's a dict
                _sellers_dict = json_data[-1] if isinstance(json_data[-1], dict) else {}
            # Else: _main_numbers remains [] and _sellers_dict remains {}

            _sellers = SellerListDataClass(**_sellers_dict)

            # Initialize the JSONData part of the class
            JSONData.__init__(self, export_header=_export_header, base_info=_base_info, settings = _settings,
                              main_numbers_list=_main_numbers, sellers=_sellers)
            self._log("INFO", "JSON data parsed successfully.")
            ret = True
        except TypeError as e:
            # Catch errors often related to unexpected data types in **kwargs
            self._log("ERROR", f"Data structure error during parsing (likely unexpected data type): {e}")
            JSONData.__init__(self, export_header=HeaderDataClass(), base_info=BaseInfoDataClass(),
                              settings=SettingDataClass(), main_numbers_list=[], sellers=SellerListDataClass()) # Reset to defaults
            ret = False
        except Exception as e:
            self._log("ERROR", f"Unexpected error during JSON parsing: {e}")
            # Reset to default state in case of partial parsing failure
            JSONData.__init__(self, export_header=HeaderDataClass(), base_info=BaseInfoDataClass(),
                              settings=SettingDataClass(), main_numbers_list=[], sellers=SellerListDataClass())
            ret = False

        return ret

    def reload_data(self, json_file_path: str) -> bool:
        """ Explicitly reloads JSON data from the given path and reparses it. """
        self._log("INFO", f"Reloading data from {json_file_path}...")
        # Use the load method from JsonHandler (which also updates self.json_data)
        self.load(json_file_path)
        if self.json_data is not None:
            return self._parse_json_data() # Reparse the newly loaded data
        else:
            self._log("ERROR", "Reload failed: Could not load new JSON data.")
            # Keep the old parsed data or reset? Resetting might be safer.
            JSONData.__init__(self, export_header=HeaderDataClass(), base_info=BaseInfoDataClass(),
                               main_numbers_list=[], sellers=SellerListDataClass())
            return False

    def get_seller_as_list(self) -> List[SellerDataClass]:
        """ Returns the list of seller data objects. """
        # Ensure sellers attribute exists from JSONData initialization
        return getattr(self, 'sellers', SellerListDataClass()).data

    def get_main_number_as_list(self) -> List[MainNumberDataClass]:
        """ Returns the list of main number data objects. """
        # Ensure main_numbers_list attribute exists
        return getattr(self, 'main_numbers_list', [])

    def get_settings(self):
        return getattr(self, 'settings', SettingDataClass()).data[0]

    def verify_data(self):
        """ Performs a basic check comparing the number of sellers and main number lists. """
        self._log("INFO", "Prüfe Datenbank:")
        # time.sleep(1) # Reduced sleep time, logging provides separation

        # Handle potential AttributeError if initialization failed badly
        try:
             seller_quantity = len(self.get_seller_as_list())
             article_list_quantity = len(self.get_main_number_as_list())
             status = ">> Datenbank OK" if seller_quantity == article_list_quantity else ">> Datenbank FEHLER: Anzahl Verkäufer und Artikellisten stimmt nicht überein!"
             mismatch = "" if seller_quantity == article_list_quantity else f" (Differenz: {abs(seller_quantity - article_list_quantity)})"

             log_message = ("========================\n" +
                           f"         >> Anzahl Verkäufer: {seller_quantity}\n" +
                           f"         >> Anzahl Artikel Listen: {article_list_quantity}{mismatch}\n"+
                           f"         {status}\n"+
                           "      ========================")
             # Log INFO if OK, WARNING if mismatch
             log_level = "INFO" if seller_quantity == article_list_quantity else "WARNING"
             self._log(log_level, log_message)

        except AttributeError as e:
             self._log("ERROR", f"Fehler bei Datenüberprüfung: Attribute nicht initialisiert. {e}")
        except Exception as e:
             self._log("ERROR", f"Unerwarteter Fehler bei Datenüberprüfung: {e}")

        # time.sleep(1) # Reduced sleep time

    def load(self, path_or_url: str) -> bool:
        """
        Load JSON data from a file or URL and parse it into data classes.

        Args:
            path_or_url (str): Path to the JSON file or URL.
        """
        ret: bool = False
        self._log("INFO", f"Loading JSON data from {path_or_url}...")
        ret = super().load(path_or_url)
        if ret:
           ret = self._parse_json_data()
        return ret


# --- END OF FILE base_data.py ---