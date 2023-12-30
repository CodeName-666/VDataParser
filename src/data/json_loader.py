import json
import inspect
from typing import Union, Dict, List



class JsonLoader():
    """
    JsonLoader is a utility class to load JSON configuration files and retrieve deeply nested values from them.

    Attributes:
        json_data (Union[str, Dict]): The loaded JSON data as a dictionary or an empty string if an error occurs.

    Methods:
        __init__(self, sw_factory_cfg: str, error_handler_cbk: Optional[Callable] = None) -> None:
            Initializes the JsonLoader with the path to the JSON configuration file and an optional error handler.

        __load_json_file__(self, json_file_path: str) -> Union[str, Dict]:
            Loads a JSON file from the given path and returns the loaded JSON data as a dictionary or an empty string if an error occurs.

        error_handler(self, error_handler_cbk: Optional[Callable]) -> None:
            Sets the error handler function to handle errors when they occur.

        __handle_error__(self, method_name: str, error_msg: str) -> None:
            Handles errors using the provided error handler function or prints the error message if no error handler is set.

        __get_key_value__(self, keys: List[str], data: dict = None):
            Retrieves a deeply nested value in a nested dictionary using a list of keys representing the path to the desired value.
            Returns the found value or None if the value is not found.
    """

    def __init__(self, json_file_path: str, error_handler  = None) -> None:
        """
        Initialize the JsonLoader.

        :param json_file_path: The path to the JSON configuration file.
        :type json_file_path: str
        :param error_handler: The optional error handling module or class that will be called when an error occurs.
        :type error_handler: 
        """
        # Initialize the error handler function
        self.__error_handler = error_handler

        # Load the JSON data from the provided configuration file path
        self.json_data = self.load_json_file(json_file_path)

    def load_json_file(self, json_file_path: str) -> Union[str, Dict]:
        """
        Load a JSON file.

        :param json_file_path: The path to the JSON file.
        :type json_file_path: str
        :return: The loaded JSON data as a dictionary, or an empty string if an error occurs.
        :rtype: Union[str, Dict]
        """
        json_data: Union[str, Dict] = ''
        try:
            # Attempt to open and load the JSON file
            with open(json_file_path, 'r', encoding='utf-8') as json_file:
                json_data = json.load(json_file)
        except json.decoder.JSONDecodeError as e:
            # Handle JSON decoding errors
            error_msg = f"JSON file structure error: {str(e)}"
            self.__handle_error("load_json_file", error_msg)
            return None
        except FileNotFoundError as e:
            # Handle file not found errors
            error_msg = f"JSON file not found error: {str(e)}"
            self.__handle_error("load_json_file", error_msg)
            return None
        return json_data

    def error_handler(self, error_handler) -> None:
        """
        Set the error handler function.

        :param error_handler_cbk: The error handler function.
        :type error_handler_cbk: Optional[Callable]
        """
        self.__error_handler = error_handler

    def error_handler(self):
        return self.__error_handler

    def __handle_error(self, type: str ,method_name: str, error_msg: str) -> None:
        """
        Handle the error using the error handler function, if provided.
        If no error handler is set, it prints the error message to the console.

        :param method_name: The name of the method where the error occurred.
        :type method_name: str
        :param error_msg: The error message.
        :type error_msg: str
        """
        error_handler_msg = f'"{method_name}", Line {inspect.currentframe().f_back.f_lineno}: {error_msg}'

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
        # If 'data' is not provided, use the loaded JSON data
        if data is None:
            internal_data = self.json_data
        else:
            internal_data = data

        try:
            key = keys[0]
            if len(keys) == 1:
                # If the key list has only one element, return the corresponding value
                return_data = internal_data.get(key, None)
                if return_data is None:
                    # If the key does not exist, raise a KeyError
                    raise KeyError(f"Unknown Key {key} requested")
                return return_data
            else:
                # If the key list has multiple elements, recursively traverse the nested dictionary
                next_level_data = internal_data.get(key, None)
                if next_level_data:
                    return self.get_key_value(keys[1:], next_level_data)
                else:
                    # If the key does not exist, raise a KeyError
                    raise KeyError(f"Unknown Key {key} requested")
        except Exception as e:
            # Handle any exception that may occur during the process and call the error handler
            error_msg = f"Key Error: {str(e)}"
            self.__handle_error("get_key_value", error_msg)
            return ''

    def get_data(self):
        return self.json_data