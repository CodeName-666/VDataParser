# --- START OF FILE json_handler.py ---

import json
import inspect
import copy
import sys # For stderr fallback
from typing import Union, Dict, List, Optional, Any # Added Optional, Any
from pathlib import Path
import os

from log import CustomLogger, LogType # Import LogType if used
import requests
from urllib.parse import urlparse, urlunparse

class JsonHandler():
    """
    JsonHandler is a utility class to load, modify, and save JSON configuration files,
    with optional logging support via CustomLogger.

    Attributes:
        json_data (Optional[Union[Dict, List]]): The loaded JSON data. None if loading failed or not yet loaded.
        logger (Optional[CustomLogger]): Logger instance for logging messages and errors.
    """

    def __init__(self, json_path_or_data: Optional[Union[str, Dict, List]] = None, logger: Optional[CustomLogger] = None) -> None:
        """
        Initialize the JsonHandler.

        Args:
            json_path_or_data (Optional[Union[str, Dict, List]]): Path/URL to the JSON file or pre-loaded JSON data.
            logger (Optional[CustomLogger]): An optional CustomLogger instance.
        """
        self.logger = logger
        self._storage_path: str = '' # Initialize path as None
        self.json_data: Optional[Union[Dict, List]] = None # Initialize as None

        if isinstance(json_path_or_data, str):
            # Load data if path/URL is provided
            self.load(json_path_or_data)
        elif isinstance(json_path_or_data, Path):
            # Load data if Path object is provided
            self.load(json_path_or_data.__str__())
        elif isinstance(json_path_or_data, (dict, list)):
            # Use provided data directly (create a deep copy)
            self.json_data = copy.deepcopy(json_path_or_data)
            self._log("DEBUG", "JsonHandler initialized with provided data object.")
        elif json_path_or_data is not None:
             self._log("WARNING", f"JsonHandler initialized with unsupported data type: {type(json_path_or_data)}. Ignored.")
        # If json_path_or_data is None, json_data remains None


    def _log(self, level: str, message: str, on_verbose: bool = False) -> None:
        """ Helper method for conditional logging. """
        if self.logger and CustomLogger: # Check if logger exists and is the correct type
            log_method = getattr(self.logger, level.lower(), None)
            if log_method and callable(log_method):
                 try:
                     if level.lower() in ["debug", "info", "warning", "error"]:
                          log_method(message, verbose=on_verbose)
                     else:
                          log_method(message)
                 except Exception as e:
                      print(f"LOGGING FAILED ({level}): {message} | Error: {e}", file=sys.stderr)
        # No print fallback for general logs, only for errors via _log_error

    def _log_error(self, method_name: str, error_msg: str, exception: Optional[Exception] = None) -> None:
        """
        Handles error logging using the logger or prints to stderr as a fallback.

        Args:
            method_name (str): The name of the method where the error occurred.
            error_msg (str): The primary error message.
            exception (Optional[Exception]): The exception object, if available.
        """
        # Try to get line number where the *caller* of _log_error is
        line_info = ""
        try:
            frame = inspect.currentframe()
            if frame and frame.f_back:
                 line_info = f"Line {frame.f_back.f_lineno}: "
        except Exception:
            pass # Ignore errors getting frame info

        # Format the final message
        full_error_msg = f"{method_name}: {line_info}{error_msg}"
        if exception:
             # Add exception type and message for more context
             full_error_msg += f" | Exception: {type(exception).__name__}: {exception}"

        if self.logger and CustomLogger:
             # Log using the ERROR level
             self.logger.error(full_error_msg)
             # Optionally log traceback if logger supports exc_info or similar
             # self.logger.error(full_error_msg, exc_info=True) # If logger supports it
        else:
             # Fallback if no logger is available
             print(f"ERROR: {full_error_msg}", file=sys.stderr)


    def load(self, path_or_url: str) -> bool:
        """
        Load JSON data from a path or URL and store it in self.json_data.
        Resets self.json_data to None if loading fails.

        Args:
            path_or_url (str): The path or URL to the JSON file.
        """
        ret: bool = False # 
        self._log("INFO", f"Attempting to load JSON from: {path_or_url}")
        self.json_data = None # Reset before loading
        try:
            parsed = urlparse(path_or_url)
            if parsed.scheme and parsed.netloc:
                # Handle URL
                self.json_data = self.load_from_url(path_or_url)
            else:
                # Handle local path
                self.json_data = self.load_from_local(path_or_url)

            if self.json_data is not None:
                 self._log("INFO", "JSON data loaded successfully.")
                 ret = True
            # else: error already logged in load_from_url/local

        except Exception as e:
             # Catch potential errors from urlparse or other unexpected issues
             self._log_error("load", f"Unexpected error during loading preparation for '{path_or_url}'", e)
             self.json_data = None
             ret = False
             
        return ret

    def load_from_url(self, json_url: str) -> Optional[Union[Dict, List]]:
        """
        Load JSON data from a URL.

        Args:
            json_url (str): The URL to the JSON file.

        Returns:
            Optional[Union[Dict, List]]: Loaded JSON data or None if an error occurs.
        """
        if requests is None:
            self._log_error("load_from_url", "Cannot load from URL because 'requests' library is not installed.")
            return None

        try:
            response = requests.get(json_url, timeout=10) # Added timeout
            response.raise_for_status() # Raises HTTPError for bad responses (4xx or 5xx)
            # Use response.json() for automatic decoding and parsing
            self.set_path_or_url(urlparse(json_url))
            return response.json()
        except requests.exceptions.Timeout:
            self._log_error("load_from_url", f"Request timed out for URL: {json_url}")
            return None
        except requests.exceptions.RequestException as e:
            self._log_error("load_from_url", f"HTTP request failed for URL: {json_url}", e)
            return None
        except json.JSONDecodeError as e:
            self._log_error("load_from_url", f"JSON decoding failed for URL: {json_url}", e)
            return None
        except Exception as e: # Catch other unexpected errors
            self._log_error("load_from_url", f"Unexpected error loading from URL: {json_url}", e)
            return None

    def load_from_local(self, json_file_path: str) -> Optional[Union[Dict, List]]:
        """
        Load a JSON file from a local path.

        Args:
            json_file_path (str): The path to the JSON file.

        Returns:
            Optional[Union[Dict, List]]: Loaded JSON data or None if an error occurs.
        """
        try:
            # Ensure path is resolved and exists before opening
            p = Path(json_file_path).resolve()
            if not p.is_file():
                 raise FileNotFoundError(f"File not found at resolved path: {p}")

            with open(p, 'r', encoding='utf-8') as json_file: # Specify UTF-8
                self.set_path_or_url(json_file_path)
                return json.load(json_file)
        except FileNotFoundError as e:
            self._log_error("load_from_local", f"JSON file not found", e)
            return None
        except json.JSONDecodeError as e:
            self._log_error("load_from_local", f"JSON decoding failed for file: {json_file_path}", e)
            return None
        except IOError as e: # Catch other file reading errors
            self._log_error("load_from_local", f"Could not read file: {json_file_path}", e)
            return None
        except Exception as e: # Catch other unexpected errors
            self._log_error("load_from_local", f"Unexpected error loading local file: {json_file_path}", e)
            return None

    def set_path_or_url(self, path_or_url: str) -> None:
        """
        Set the path or URL for the JSON data.

        Args:
            path_or_url (str): The path or URL to set.
        """
        if not isinstance(path_or_url, str):
            self._log("ERROR", "set_path_or_url requires a string path or URL.")
            return
        self._storage_path = path_or_url
        self._log("DEBUG", f"Path or URL set to: {str(self._storage_path)}")
    # get_value method seems unused, can be removed or kept if needed elsewhere
    # def get_value(self, data: Union[Dict, List], key: Union[str, int]) -> Optional[Any]: ...

    def get_key_value(self, keys: List[Union[str, int]], data: Optional[Union[Dict, List]] = None) -> Optional[Any]:
        """
        Retrieve a deeply nested value using a list of keys/indices.

        Args:
            keys (List[Union[str, int]]): Path to the desired value (strings for dict keys, ints for list indices).
            data (Optional[Union[Dict, List]]): Dictionary or list to search in (defaults to self.json_data).

        Returns:
            Optional[Any]: Found value or None if path is invalid or not found.
        """
        current_data = data if data is not None else self.json_data

        if current_data is None:
             self._log("WARNING", "get_key_value called but no JSON data is loaded.")
             return None
        if not keys: # Empty keys list
             return current_data # Return the current level data

        key = keys[0]
        remaining_keys = keys[1:]

        try:
            if isinstance(current_data, dict):
                if isinstance(key, str):
                    next_level_data = current_data.get(key) # Use .get for safety
                    if next_level_data is None and key in current_data: # Handle explicit None value
                         return None if not remaining_keys else self.get_key_value(remaining_keys, None)
                    elif next_level_data is None and key not in current_data:
                         raise KeyError(f"Key '{key}' not found")
                else:
                    raise TypeError(f"Cannot use key of type {type(key).__name__} to access a dictionary")

            elif isinstance(current_data, list):
                if isinstance(key, int):
                    if 0 <= key < len(current_data):
                        next_level_data = current_data[key]
                    else:
                        raise IndexError(f"Index {key} out of range (size {len(current_data)})")
                else:
                    raise TypeError(f"Cannot use key of type {type(key).__name__} to access a list")
            else:
                # Cannot traverse further if current level is not dict or list
                raise TypeError(f"Cannot traverse key '{key}'; current data level is of type {type(current_data).__name__}")

            # Recursive call or return final value
            if not remaining_keys:
                return next_level_data
            else:
                return self.get_key_value(remaining_keys, next_level_data)

        except (KeyError, IndexError, TypeError) as e:
            path_str = " -> ".join(map(str, keys[:keys.index(key)+1]))
            self._log_error("get_key_value", f"Error accessing path '{path_str}'", e)
            return None
        except Exception as e: # Catch other unexpected errors
             path_str = " -> ".join(map(str, keys))
             self._log_error("get_key_value", f"Unexpected error accessing path '{path_str}'", e)
             return None


    def set_key_value(self, keys: List[Union[str, int]], value: Any, data: Optional[Union[Dict, List]] = None) -> bool:
        """
        Set a value for a deeply nested key/index. Creates path if it does not exist.

        Args:
            keys (List[Union[str, int]]): Path to the desired key/index.
            value (Any): Value to set.
            data (Optional[Union[Dict, List]]): Dictionary/list to modify (defaults to self.json_data).

        Returns:
            bool: True if successful, False otherwise.
        """
        current_data = data if data is not None else self.json_data

        if current_data is None:
             self._log("ERROR", "set_key_value called but no JSON data is loaded or provided.")
             return False
        if not keys:
             self._log("ERROR", "set_key_value requires a non-empty list of keys.")
             return False

        key = keys[0]
        remaining_keys = keys[1:]

        try:
            if not remaining_keys: # Last key in the path
                if isinstance(current_data, dict) and isinstance(key, str):
                    current_data[key] = value
                    return True
                elif isinstance(current_data, list) and isinstance(key, int):
                    if 0 <= key < len(current_data):
                        current_data[key] = value
                        return True
                    elif key == len(current_data): # Allow appending
                        current_data.append(value)
                        return True
                    else:
                        raise IndexError(f"Index {key} out of range for setting value (size {len(current_data)})")
                else:
                    raise TypeError(f"Cannot set value at final key '{key}' with current data type {type(current_data).__name__}")
            else: # Traverse or create next level
                next_key = remaining_keys[0]
                if isinstance(current_data, dict) and isinstance(key, str):
                    if key not in current_data:
                        # Create next level based on the type of the *next* key
                        current_data[key] = [] if isinstance(next_key, int) else {}
                    elif not isinstance(current_data[key], (dict, list)):
                         # Overwrite if existing value is not traversable, log warning?
                         self._log("WARNING", f"Overwriting non-traversable value at key '{key}' during set_key_value.")
                         current_data[key] = [] if isinstance(next_key, int) else {}
                    return self.set_key_value(remaining_keys, value, current_data[key])

                elif isinstance(current_data, list) and isinstance(key, int):
                    if key == len(current_data): # Need to append a new level
                         current_data.append([] if isinstance(next_key, int) else {})
                    elif not (0 <= key < len(current_data)):
                        raise IndexError(f"Index {key} out of range for traversal (size {len(current_data)})")

                    if not isinstance(current_data[key], (dict, list)):
                        # Overwrite if existing value is not traversable
                        self._log("WARNING", f"Overwriting non-traversable value at index {key} during set_key_value.")
                        current_data[key] = [] if isinstance(next_key, int) else {}
                    return self.set_key_value(remaining_keys, value, current_data[key])
                else:
                     raise TypeError(f"Cannot traverse key '{key}' (type {type(key).__name__}) on data type {type(current_data).__name__}")

        except (KeyError, IndexError, TypeError) as e:
            path_str = " -> ".join(map(str, keys[:keys.index(key)+1]))
            self._log_error("set_key_value", f"Error setting value at path '{path_str}'", e)
            return False
        except Exception as e: # Catch other unexpected errors
            path_str = " -> ".join(map(str, keys))
            self._log_error("set_key_value", f"Unexpected error setting value at path '{path_str}'", e)
            return False

    def save(self, path_or_url: str = "") -> None:
        """ Saves the current JSON data to the specified local path or URL. """
        if self.json_data is None:
            self._log("ERROR", "Cannot save, no JSON data loaded.")
            return

        if not path_or_url:
            path_or_url = str(self._storage_path)
            self._log("INFO", f"No path or URL provided. Use {str(self._storage_path)} to save.")
            

        self._log("INFO", f"Attempting to save JSON data to: {path_or_url}")
        try:
            parsed = urlparse(path_or_url)
            if parsed.scheme and parsed.netloc:
                self.save_to_url(path_or_url)
            else:
                self.save_to_local(path_or_url)

            self.set_path_or_url(path_or_url)
            
        except Exception as e:
             self._log_error("save", f"Unexpected error during save preparation for '{path_or_url}'", e)

    def save_to_url(self, json_url: str) -> None:
        """ Saves JSON data to a URL using a PUT request. """
        if requests is None:
            self._log_error("save_to_url", "Cannot save to URL because 'requests' library is not installed.")
            return
        if self.json_data is None: return # Already logged by save()

        try:
            # Consider adding headers if required by the endpoint
            response = requests.put(json_url, json=self.json_data, timeout=10)
            response.raise_for_status()
            self._log("INFO", f"JSON data successfully saved to URL: {json_url}")
        except requests.exceptions.Timeout:
            self._log_error("save_to_url", f"Request timed out saving to URL: {json_url}")
        except requests.exceptions.RequestException as e:
            self._log_error("save_to_url", f"HTTP request failed saving to URL: {json_url}", e)
        except Exception as e: # Catch other unexpected errors
            self._log_error("save_to_url", f"Unexpected error saving to URL: {json_url}", e)


    def save_to_local(self, json_file_path: str) -> None:
        """ Saves JSON data to a local file. """
        if self.json_data is None: return # Already logged by save()

        try:
            p = Path(json_file_path)
            # Ensure the parent directory exists
            p.parent.mkdir(parents=True, exist_ok=True)
            with open(p, 'w', encoding='utf-8') as json_file:
                json.dump(self.json_data, json_file, indent=4, ensure_ascii=False) # ensure_ascii=False for non-latin chars
            self._log("INFO", f"JSON data successfully saved to local file: {p.resolve()}")
        except IOError as e:
            self._log_error("save_to_local", f"Could not write to file: {json_file_path}", e)
        except Exception as e: # Catch other unexpected errors
            self._log_error("save_to_local", f"Unexpected error saving local file: {json_file_path}", e)

    def get_data(self) -> Optional[Union[Dict, List]]:
        """ Returns the loaded JSON data. """
        return self.json_data
    
    def data_equal(self, other: 'JsonHandler') -> bool:
        """
        Compare this JsonHandler's data with another JsonHandler's data.

        Args:
            other (JsonHandler): Another instance of JsonHandler to compare with.

        Returns:
            bool: True if both JSON data are equal, False otherwise.
        """
        if not isinstance(other, JsonHandler):
            self._log("ERROR", "compare_data requires another JsonHandler instance.")
            return False
        return self.json_data == other.get_data()
    
    def split_path_and_filename(path_str: str) -> tuple[str, str]:
        """
        Teilt einen String (URL oder lokaler Pfad) in
        (restlichen Pfad, Dateiname).
        
        Für URLs (scheme + netloc vorhanden):
        • entfernt Query und Fragment
        • gibt base_url (inkl. scheme://host/…/) und filename zurück
        
        Für lokale Pfade:
        • nutzt os.path.split
        • hängt am Ende des Verzeichnisteils einen os.sep an (wenn nicht schon vorhanden)
        """
        parsed = urlparse(path_str)
        # Wenn scheme und netloc vorhanden sind, behandeln wir es als URL
        if parsed.scheme and parsed.netloc:
            # parsed.path ist der reine Pfad-Teil ("/foo/bar/file.txt")
            dirpath, filename = os.path.split(parsed.path)
            # sicherstellen, dass der Verzeichnis-Teil mit "/" endet
            if dirpath and not dirpath.endswith('/'):
                dirpath += '/'
            # Query und Fragment entfernen, path auf dirpath anpassen
            new_parsed = parsed._replace(path=dirpath, params='', query='', fragment='')
            base_url = urlunparse(new_parsed)
            return base_url, filename
        
        # sonst lokaler Pfad
        dirpath, filename = os.path.split(path_str)
        # Verzeichnis mit trailing separator
        if dirpath and not (dirpath.endswith(os.sep) or dirpath.endswith('/')):
            dirpath += os.sep
        return dirpath, filename

    def update_json_data(self, other: 'JsonHandler') -> None:
        """
        Update the current JSON data with data from another JsonHandler object.

        Args:
            other (JsonHandler): Another JsonHandler instance whose data will be used.
        """
        if not isinstance(other, JsonHandler):
            self._log("ERROR", "update_data requires a JsonHandler instance.")
            return
        self.json_data = copy.deepcopy(other.get_data())
        self._log("INFO", "JSON data updated successfully from another JsonHandler.")

    def get_storage_full_path(self) -> str:
        
        return self._storage_path

    def get_storage_file_name(self) -> str:
        _ , name =  self.split_path_and_filename(self._storage_path)
        return name
    
    def get_storage_path(self) -> str:
        dir , _ =  self.split_path_and_filename(self._storage_path)
        return dir

# --- END OF FILE json_handler.py ---