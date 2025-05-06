import sys
from typing import List, Optional

from data import SellerDataClass, MainNumberDataClass
from .seller import Seller
from .main_number import MainNumber

# --- Optional Import for the Logger ---
try:
    from log import CustomLogger # Replace if your logger class name is different
except ImportError:
    print("WARNING: Could not import 'CustomLogger' from 'log'. Logging features will be disabled.", file=sys.stderr)
    CustomLogger = None # Set to None, code will check for this

# --- Optional Import for the Output Interface ---
try:
    # Assuming you might want to use OutputInterfaceAbstraction in FleatMarket as well
    from src.display import OutputInterfaceAbstraction
except ImportError:
    print("WARNING: Could not import 'OutputInterfaceAbstraction' from 'output_interface_abstraction'. User output features will be disabled.", file=sys.stderr)
    OutputInterfaceAbstraction = None


class FleatMarket:
    """
    Manages collections of Seller and MainNumber objects for a flea market context.

    Provides methods to load data, retrieve lists, and access specific sellers.
    Can optionally integrate with a logging system and an output interface.
    """

    def __init__(self,
                 logger: Optional[CustomLogger] = None,
                 output_interface: Optional[OutputInterfaceAbstraction] = None) -> None:
        """
        Initializes a new FleatMarket instance.

        Args:
            logger (Optional[CustomLogger]): An instance of a CustomLogger.
            output_interface (Optional[OutputInterfaceAbstraction]): An instance of an OutputInterface.
        """
        self.__seller_list: List[Seller] = []
        self.__main_number_list: List[MainNumber] = []
        self._logger = logger
        self._output_interface = output_interface # Store the output interface

        self._log("info", "FleatMarket instance initialized.")

    def _log(self, level: str, message: str, on_verbose: bool = False, exc_info: bool = False) -> None:
        """
        Helper method to log a message if a logger is available.

        Args:
            level (str): The logging level (e.g., "debug", "info", "warning", "error").
            message (str): The message to log.
            on_verbose (bool): Passed to logger methods that support it (e.g., debug).
            exc_info (bool): If True, exception information is added to the logging message.
        """
        if not self._logger:
            return

        log_method = getattr(self._logger, level, None)
        if not log_method:
            self._logger.info(f"LOG ({level.upper()}): {message}") # Fallback
            return

        if level == "debug":
            log_method(message, on_verbose=on_verbose)
        elif level in ["error", "exception"]: # Some loggers might have 'exception'
             log_method(message, exc_info=exc_info)
        elif level in ["warning", "info", "critical"]:
            log_method(message)
        else: # Custom levels or fallback
            log_method(message)


    def _log_and_output(self,
                        log_level: str,
                        output_prefix: str,
                        base_message: str,
                        log_on_verbose: bool = False,
                        log_exc_info: bool = False) -> None:
        """
        Helper method to log a message AND output it to the user interface.

        Args:
            log_level (str): The logging level.
            output_prefix (str): A prefix for the user message (e.g., "USER_WARNING:", "NOTICE:").
            base_message (str): The core message content.
            log_on_verbose (bool): Passed to the logger for debug messages.
            log_exc_info (bool): If True, exception information is added to the logging message.
        """
        self._log(log_level, base_message, on_verbose=log_on_verbose, exc_info=log_exc_info)

        if self._output_interface:
            self._output_interface.write_message(f"{output_prefix} {base_message}")


    def set_seller_data(self, seller_data_list: List[SellerDataClass]) -> None:
        """
        Populates the internal seller list from a list of SellerDataClass objects.
        Clears the existing seller list and creates new Seller instances.
        """
        self._log("debug", f"Attempting to set seller data with {len(seller_data_list)} items.", on_verbose=True)

        new_seller_list = []
        try:
            # Create Seller instances.
            # If Seller class also needs logger/output_interface, pass them here:
            # new_seller_list = [
            #     Seller(seller_data, logger=self._logger, output_interface=self._output_interface)
            #     for seller_data in seller_data_list
            # ]
            # For now, assuming Seller doesn't require them or handles them internally
            new_seller_list = [
                Seller(seller_data) # Pass logger/output if Seller is updated to accept them
                for seller_data in seller_data_list
            ]
            self.__seller_list = new_seller_list
            self._log("info", f"Successfully set {len(self.__seller_list)} sellers.")
        except Exception as e:
            msg = f"Failed to create Seller instances from data. Error: {e}"
            # Log with exception info, output a user-friendly error
            self._log_and_output("error", "USER_ERROR:", msg, log_exc_info=True)
            # self.__seller_list = [] # Option: Clear list on error or revert

    def set_main_number_data(self, main_number_data_list: List[MainNumberDataClass]) -> None:
        """
        Populates the internal main number list from a list of MainNumberDataClass objects.
        Clears the existing main number list and creates new MainNumber instances.
        """
        self._log("debug", f"Attempting to set main number data with {len(main_number_data_list)} items.", on_verbose=True)

        new_main_number_list = []
        try:
            # Create MainNumber instances.
            # If MainNumber class also needs logger/output_interface, pass them here:
            # new_main_number_list = [
            #     MainNumber(main_number_data, logger=self._logger, output_interface=self._output_interface)
            #     for main_number_data in main_number_data_list
            # ]
            # For now, assuming MainNumber doesn't require them or handles them internally
            new_main_number_list = [
                MainNumber(main_number_data) # Pass logger/output if MainNumber is updated
                for main_number_data in main_number_data_list
            ]
            self.__main_number_list = new_main_number_list
            self._log("info", f"Successfully set {len(self.__main_number_list)} main numbers.")
        except Exception as e:
            msg = f"Failed to create MainNumber instances from data. Error: {e}"
            self._log_and_output("error", "USER_ERROR:", msg, log_exc_info=True)
            # self.__main_number_list = [] # Option: Clear list on error or revert

    def get_seller_list(self) -> List[Seller]:
        """
        Returns the current list of Seller objects.
        """
        self._log("debug", f"Accessing seller list (count: {len(self.__seller_list)}).", on_verbose=True)
        return self.__seller_list

    def get_main_number_list(self) -> List[MainNumber]:
        """
        Returns the current list of MainNumber objects.
        """
        self._log("debug", f"Accessing main number list (count: {len(self.__main_number_list)}).", on_verbose=True)
        return self.__main_number_list

    def get_seller_by_index(self, index: int) -> Optional[Seller]:
        """
        Retrieves a specific Seller object by its zero-based index in the list.
        """
        self._log("debug", f"Attempting to get seller at index {index}.", on_verbose=True)

        if 0 <= index < len(self.__seller_list):
            seller = self.__seller_list[index]
            self._log("debug", f"Found seller at index {index}: {seller}", on_verbose=True)
            return seller
        else:
            msg = f"Index {index} out of bounds for seller list (size: {len(self.__seller_list)})."
            # Log as warning, no direct user output for this as it's often a programmatic check
            self._log("warning", msg)
            # Could use _log_and_output if user notification is desired for out-of-bounds access:
            # self._log_and_output("warning", "NOTICE:", msg)
            return None