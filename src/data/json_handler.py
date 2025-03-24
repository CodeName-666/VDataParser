import json
import inspect
import copy
from typing import Union, Dict, List
from urllib.parse import urlparse
import requests


class JsonHandler():
    """
    JsonHandler is a utility class to load, modify, and save JSON configuration files.

    Attributes:
        json_data (Union[str, Dict]): The loaded JSON data as a dictionary or an empty string if an error occurs.

    Methods:
        __init__(self, sw_factory_cfg: str, error_handler_cbk: Optional[Callable] = None) -> None:
            Initializes the JsonHandler with the path to the JSON configuration file and an optional error handler.

        load(self, path_or_url: str) -> Union[str, Dict]:
            Loads a JSON file from a path or URL and returns the loaded JSON data.

        load_from_url(self, json_url: str) -> Union[str, Dict]:
            Loads a JSON file from a URL and returns the loaded JSON data.

        load_from_local(self, json_file_path: str) -> Union[str, Dict]:
            Loads a JSON file from a local path and returns the loaded JSON data.

        error_handler(self, error_handler: Callable) -> None:
            Sets the error handler function to handle errors when they occur.

        __handle_error(self, method_name: str, error_msg: str) -> None:
            Handles errors using the provided error handler function or prints the error message if no error handler is set.

        get_key_value(self, keys: List[str], data: dict = None):
            Retrieves a deeply nested value in a nested dictionary using a list of keys representing the path to the desired value.
            Returns the found value or None if the value is not found.

        set_key_value(self, keys: List[str], value, data: dict = None) -> None:
            Sets a value for a deeply nested key in a nested dictionary. Creates the key if it does not exist.

        save(self, path_or_url: str) -> None:
            Saves the current JSON data to the specified local path or URL.
    """

    def __init__(self, json_path_or_data: Union[str, Dict] = None, error_handler=None) -> None:
        """
        Initialize the JsonHandler.

        :param json_path_or_data: The path or data to the JSON configuration file.
        :type json_path_or_data: str
        :param error_handler: The optional error handling module or class that will be called when an error occurs.
        :type error_handler: Callable, optional
        """
        self.__error_handler = error_handler
        self.json_data = None

        if isinstance(json_path_or_data,str):
            self.load(json_path_or_data)
        elif isinstance(json_path_or_data,Dict):
            self.json_data = copy.deepcopy(json_path_or_data)
        else: 
            pass

        
    def load(self, path_or_url: str) -> Union[str, Dict]:
        """
        Load JSON data from a path or URL.

        :param path_or_url: The path or URL to the JSON file.
        :type path_or_url: str
        :return: The loaded JSON data as a dictionary, or an empty string if an error occurs.
        :rtype: Union[str, Dict]
        """
        parsed = urlparse(path_or_url)
        if parsed.scheme and parsed.netloc:
            self.json_data =  self.load_from_url(path_or_url)
        else:
            self.json_data =  self.load_from_local(path_or_url)

    def load_from_url(self, json_url: str) -> Union[str, Dict]:
        """
        Load JSON data from a URL.

        :param json_url: The URL to the JSON file.
        :type json_url: str
        :return: The loaded JSON data as a dictionary, or an empty string if an error occurs.
        :rtype: Union[str, Dict]
        """
        json_data = ''
        try:
            response = requests.get(json_url)
            json_data = json.loads(response.content.decode('utf-8'))
        except json.decoder.JSONDecodeError as e:
            error_msg = f"JSON file structure error: {str(e)}"
            self.__handle_error("load_from_url", error_msg)
        except requests.exceptions.HTTPError as e:
            error_msg = f"File not found with error: {str(e)}"
            self.__handle_error("load_from_url", error_msg)
        return json_data

    def load_from_local(self, json_file_path: str) -> Union[str, Dict]:
        """
        Load a JSON file from a local path.

        :param json_file_path: The path to the JSON file.
        :type json_file_path: str
        :return: The loaded JSON data as a dictionary, or an empty string if an error occurs.
        :rtype: Union[str, Dict]
        """
        json_data: Union[str, Dict] = ''
        try:
            with open(json_file_path, 'r', encoding='utf-8') as json_file:
                json_data = json.load(json_file)
        except json.decoder.JSONDecodeError as e:
            error_msg = f"JSON file structure error: {str(e)}"
            self.__handle_error("load_from_local", error_msg)
            return None
        except FileNotFoundError as e:
            error_msg = f"JSON file not found error: {str(e)}"
            self.__handle_error("load_from_local", error_msg)
            return None
        return json_data

    def error_handler(self, error_handler) -> None:
        """
        Set the error handler function.

        :param error_handler: The error handler function.
        :type error_handler: Callable
        """
        self.__error_handler = error_handler

    def error_handler(self):
        return self.__error_handler

    def __handle_error(self, method_name: str, error_msg: str) -> None:
        """
        Handle the error using the error handler function, if provided.
        If no error handler is set, it prints the error message to the console.

        :param method_name: The name of the method where the error occurred.
        :type method_name: str
        :param error_msg: The error message.
        :type error_msg: str
        """
        error_handler_msg = f'"{method_name}", Line {inspect.currentframe().f_back.f_lineno}: {error_msg}'
        if self.__error_handler:
            self.__error_handler(method_name, error_msg)
        else:
            print(error_handler_msg)

    def get_value(self, data: Dict, key):
        return_value = None
        if isinstance(key, str):
            return_value = data.get(key, None)
        elif isinstance(key, int):
            return_value = data[key]
        else:
            return_value = None
        
        return return_value


    def get_key_value(self, keys: List[str], data: dict = None):
        """
        Retrieve a deeply nested value in a nested dictionary.

        :param keys: A list of keys representing the path to the desired value.
        :type keys: List[str]
        :param data: The dictionary to search in (default is the loaded JSON data).
        :type data: Optional[dict]
        :return: The found value or None if the value is not found.
        :rtype: Union[object, None]
        """
        if data is None:
            internal_data = self.json_data
        else:
            internal_data = data

        try:
            key = keys[0]
            if len(keys) == 1:
                return_data = self.get_value(internal_data, key)
                if return_data is None:
                    raise KeyError(f"Unknown Key {key} requested")
                return return_data
            else:
                next_level_data = self.get_value(internal_data,key)
                if next_level_data:
                    return self.get_key_value(keys[1:], next_level_data)
                else:
                    raise KeyError(f"Unknown Key {key} requested")
        except Exception as e:
            error_msg = f"Key Error: {str(e)}"
            self.__handle_error("get_key_value", error_msg)
            return None

    def set_key_value(self, keys: List[str], value, data: dict = None) -> bool:
        """
        Set a value for a deeply nested key in a nested dictionary.
        Creates the key if it does not exist.

        :param keys: A list of keys representing the path to the desired key.
        :type keys: List[str]
        :param value: The value to set at the specified key path.
        :type value: Any
        :param data: The dictionary to modify (default is the loaded JSON data).
        :type data: Optional[dict]
        """
        if data == None:
            data = self.json_data

        key = keys[0]

        if len(keys) == 1:
            try:
                data[key] = value
                return True
            except Exception as e: 
                error_msg = f"Key Error: {str(e)}"
                self.__handle_error("get_key_value", error_msg)
                return False
        else:
            if isinstance(data,dict):
                if key not in data:
                    data[key] = {}

            elif isinstance(data, list):
                if isinstance(key,int):
                    if len(data) < key:
                        raise IndexError("Wrong index was requested")
                else:
                    raise TypeError(f"Wrong type of paramter are given, Integer expected, got {type(key)} ")
            else:
                raise NotImplementedError("This case is not implemented yes")
            
            return self.set_key_value(keys[1:], value, data[key])
        

    def save(self, path_or_url: str) -> None:
        """
        Save the current JSON data to the specified local path or URL.

        :param path_or_url: The path or URL to save the JSON data.
        :type path_or_url: str
        """
        parsed = urlparse(path_or_url)
        if parsed.scheme and parsed.netloc:
            self.save_to_url(path_or_url)
        else:
            self.save_to_local(path_or_url)

    def save_to_url(self, json_url: str) -> None:
        """
        Save JSON data to a URL using a PUT request.

        :param json_url: The URL to save the JSON data.
        :type json_url: str
        """
        try:
            response = requests.put(json_url, json=self.json_data)
            response.raise_for_status()
        except Exception as e:
            error_msg = f"Failed to save JSON data to URL: {str(e)}"
            self.__handle_error("save_to_url", error_msg)

    def save_to_local(self, json_file_path: str) -> None:
        """
        Save JSON data to a local file.

        :param json_file_path: The path to the local JSON file.
        :type json_file_path: str
        """
        try:
            with open(json_file_path, 'w', encoding='utf-8') as json_file:
                json.dump(self.json_data, json_file, indent=4)
        except Exception as e:
            error_msg = f"Failed to save JSON data to local file: {str(e)}"
            self.__handle_error("save_to_local", error_msg)

    def get_data(self):
        return self.json_data

