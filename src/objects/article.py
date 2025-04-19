import sys
import dataclasses # Required for working with dataclass fields
from dataclasses import dataclass
from typing import Optional, Any
from data import ArticleDataClass


# --- Optional Import for the Logger ---
try:
    # Attempt to import your specific logger class
    from log import CustomLogger # Replace if your logger class name is different
except ImportError:
    # Fallback: Set to None if unavailable
    print("WARNING: Could not import 'CustomLogger' from 'log'. Logging features will be disabled.", file=sys.stderr)
    CustomLogger = None # Set to None, code will check for this

# --- Article Class Definition ---

class Article(ArticleDataClass):
    """
    Represents an article, inheriting data fields from ArticleDataClass
    and adding validation logic and optional logging.
    """

    def __init__(self, article_info: Optional[ArticleDataClass] = None, logger: Optional[CustomLogger] = None):
        """
        Initializes a new Article instance.

        It first initializes the base ArticleDataClass with default values,
        then optionally copies data from the provided `article_info` object
        using the `set_article_info` method.

        Args:
            article_info (Optional[ArticleDataClass]): An instance of ArticleDataClass
                containing the initial data for this article. If None, the article
                is initialized with default values.
            logger (Optional[CustomLogger]): An instance of a CustomLogger (or compatible logger).
                If None, no logging will be performed by this instance.
        """
        # Store the logger instance (can be None)
        self._logger = logger

        # Initialize the base dataclass attributes with default values first.
        # super().__init__() or ArticleDataClass.__init__(self) achieves this.
        super().__init__() # Use super() for cleaner inheritance calls

        # If initial article information is provided, apply it using set_article_info
        if article_info:
            self.set_article_info(article_info)
        # If article_info is None, the object retains the default values set by super().__init__()


    def set_article_info(self, article_info: ArticleDataClass) -> None:
        """
        Updates the article's attributes based on another ArticleDataClass instance.

        Copies values for all fields defined in ArticleDataClass from the
        provided `article_info` object to this instance.

        Args:
            article_info (ArticleDataClass): An instance of ArticleDataClass containing
                the article data to be copied. Must be of the correct type.
        """
        # Check if the provided object is a valid ArticleDataClass instance
        if article_info and isinstance(article_info, ArticleDataClass):
            try:
                # Iterate through the fields defined in the dataclass
                for field in dataclasses.fields(article_info):
                    # Get the value from the source object
                    value = getattr(article_info, field.name)
                    # Set the value on the current object (self)
                    setattr(self, field.name, value)

                if self._logger:
                    # Log successful update
                    self._logger.debug(f"Article info updated for number: '{self.number()}' using set_article_info.", on_verbose=True)

            except (AttributeError, TypeError) as e:
                # Catch potential errors during attribute access/setting
                 if self._logger:
                     self._logger.error(f"Failed to set article info using dataclass fields. Object might be malformed. Error: {e}")
        elif article_info:
             # Log a warning if a non-None object of the wrong type was passed
             if self._logger:
                 self._logger.warning(f"set_article_info called with incompatible type: {type(article_info)}. Expected ArticleDataClass.")
        else:
             # Log if None was passed explicitly (usually harmless)
             if self._logger:
                 self._logger.debug("set_article_info called with None, no changes made.", on_verbose=True)

    # --- Validation and Accessor Methods (Unchanged) ---

    def is_valid(self) -> bool:
        """
        Checks if the article is considered overall valid based on its description and price.

        Returns:
            bool: True if both description and price are valid according to their
                  respective validation methods (`description_valid` and `price_valid`),
                  False otherwise.
        """
        desc_valid = self.description_valid()
        price_valid = self.price_valid()
        valid = desc_valid and price_valid

        if self._logger:
            if valid:
                self._logger.debug(f"Article valid: '{self.description()}' (Num: {self.number()})", on_verbose=True)
            else:
                invalid_parts = []
                if not desc_valid: invalid_parts.append("Description")
                if not price_valid: invalid_parts.append("Price")
                self._logger.debug(f"Article invalid: '{self.description()}' (Num: {self.number()}). Invalid parts: {', '.join(invalid_parts)}", on_verbose=True)
        return valid

    def number(self) -> str:
        """Returns the article number (`self.artikelnummer`)."""
        return self.artikelnummer

    def price(self) -> str:
        """Returns the price of the article (`self.preis`) as a string."""
        return self.preis # Type is str as per ArticleDataClass

    def description(self) -> str:
        """Returns the description of the article (`self.beschreibung`)."""
        return self.beschreibung

    def number_valid(self) -> bool:
        """
        Checks if the article number is valid (not None and not an empty string).

        Returns:
            bool: True if the article number is valid, False otherwise.
        """
        num = self.number()
        valid = (num is not None and num != "") # Should always be str due to dataclass default
        if self._logger:
            self._logger.debug(f"Number validation: value='{num}' -> valid={valid}", on_verbose=True)
        return valid

    def price_valid(self) -> bool:
        """
        Checks if the price string is valid.

        A price string is considered invalid if it is None (shouldn't happen with
        dataclass default), an empty string (""), or the literal string "None".

        Returns:
            bool: True if the price string is considered valid, False otherwise.
        """
        price_value = self.price() # price_value is a string here

        # Perform the checks for invalid states on the string
        is_none = (price_value is None) # Defensive check, though unlikely with default
        is_empty_str = (price_value == "")
        is_literal_none_str = (price_value == "None")

        valid = not (is_none or is_empty_str or is_literal_none_str)

        if self._logger:
            self._logger.debug(
                f"Price validation: value='{price_value}' (type: {type(price_value).__name__}), "
                f"is_empty_str={is_empty_str}, is_literal_none_str={is_literal_none_str} "
                f"-> valid={valid}",
                on_verbose=True
            )
        return valid

    def description_valid(self) -> bool:
        """
        Checks if the description is valid (not None and not an empty string).

        Returns:
            bool: True if the description is valid, False otherwise.
        """
        desc = self.description()
        valid = (desc is not None and desc != "") # Should always be str due to dataclass default
        if self._logger:
            self._logger.debug(f"Description validation: value='{str(desc)[:50]}...' -> valid={valid}", on_verbose=True)
        return valid
