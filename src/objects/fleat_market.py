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

# --- FleatMarket Class Definition ---

class FleatMarket:
    """
    Manages collections of Seller and MainNumber objects for a flea market context.

    Provides methods to load data, retrieve lists, and access specific sellers.
    Can optionally integrate with a logging system.
    """

    def __init__(self, logger: Optional[CustomLogger] = None) -> None:
        """
        Initializes a new FleatMarket instance.

        Args:
            logger (Optional[CustomLogger]): An instance of a CustomLogger (or compatible logger).
                If None, no logging will be performed by this instance.
        """
        self.__seller_list: List[Seller] = []
        self.__main_number_list: List[MainNumber] = []
        self._logger = logger # Store the logger instance (can be None)

        if self._logger:
            self._logger.info("FleatMarket instance initialized.")

    def set_seller_data(self, seller_data_list: List[SellerDataClass]) -> None:
        """
        Populates the internal seller list from a list of SellerDataClass objects.

        Clears the existing seller list and creates new Seller instances
        for each item in the input list, passing the logger to them if available.

        Args:
            seller_data_list (List[SellerDataClass]): A list of data objects,
                each containing the information for one seller.
        """
        if self._logger:
            self._logger.debug(f"Attempting to set seller data with {len(seller_data_list)} items.")

        new_seller_list = []
        try:
            # Create Seller instances, passing the logger down
            new_seller_list = [
                Seller(seller_data, logger=self._logger)
                for seller_data in seller_data_list
            ]
            self.__seller_list = new_seller_list # Assign only after successful creation
            if self._logger:
                self._logger.info(f"Successfully set {len(self.__seller_list)} sellers.")
        except Exception as e:
            # Catch errors during Seller instantiation
            if self._logger:
                self._logger.error(f"Failed to create Seller instances from data. Error: {e}", exc_info=True)
            # Keep the old list or an empty list depending on desired error handling
            # self.__seller_list = [] # Option: Clear list on error

    def set_main_number_data(self, main_number_data_list: List[MainNumberDataClass]) -> None:
        """
        Populates the internal main number list from a list of MainNumberDataClass objects.

        Clears the existing main number list and creates new MainNumber instances
        for each item in the input list, passing the logger to them if available.

        Args:
            main_number_data_list (List[MainNumberDataClass]): A list of data objects,
                each containing the information for one main number.
        """
        if self._logger:
            self._logger.debug(f"Attempting to set main number data with {len(main_number_data_list)} items.")

        new_main_number_list = []
        try:
             # Create MainNumber instances, passing the logger down
            new_main_number_list = [
                MainNumber(main_number_data, logger=self._logger)
                for main_number_data in main_number_data_list
            ]
            self.__main_number_list = new_main_number_list # Assign only after successful creation
            if self._logger:
                self._logger.info(f"Successfully set {len(self.__main_number_list)} main numbers.")
        except Exception as e:
             # Catch errors during MainNumber instantiation
             if self._logger:
                self._logger.error(f"Failed to create MainNumber instances from data. Error: {e}", exc_info=True)
             # Keep the old list or an empty list
             # self.__main_number_list = [] # Option: Clear list on error


    def get_seller_list(self) -> List[Seller]:
        """
        Returns the current list of Seller objects.

        Returns:
            List[Seller]: The internal list of initialized Seller instances.
        """
        if self._logger:
            self._logger.debug(f"Accessing seller list (count: {len(self.__seller_list)}).")
        return self.__seller_list

    def get_main_number_list(self) -> List[MainNumber]:
        """
        Returns the current list of MainNumber objects.

        Returns:
            List[MainNumber]: The internal list of initialized MainNumber instances.
        """
        # Corrected method name from get_main_number_list to match convention
        if self._logger:
            self._logger.debug(f"Accessing main number list (count: {len(self.__main_number_list)}).")
        return self.__main_number_list

    def get_seller_by_index(self, index: int) -> Optional[Seller]:
        """
        Retrieves a specific Seller object by its zero-based index in the list.

        Args:
            index (int): The zero-based index of the seller to retrieve.

        Returns:
            Optional[Seller]: The Seller object at the specified index, or None if
                              the index is out of bounds.
        """
        # Renamed 'main_number' parameter to 'index' for clarity, as it's used as a list index.
        # Corrected boundary check: indices are 0 to len-1.
        if self._logger:
            self._logger.debug(f"Attempting to get seller at index {index}.")

        if 0 <= index < len(self.__seller_list):
            seller = self.__seller_list[index]
            if self._logger:
                self._logger.debug(f"Found seller at index {index}: {seller}")
            return seller
        else:
            if self._logger:
                self._logger.warning(f"Index {index} out of bounds for seller list (size: {len(self.__seller_list)}).")
            return None # Return None for invalid index

