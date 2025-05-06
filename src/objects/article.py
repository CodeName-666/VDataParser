import sys
import dataclasses
from typing import Optional, Any

# Assuming ArticleDataClass is defined in data.py
from data import ArticleDataClass

# --- Optional Import for the Logger ---
try:
    from log import CustomLogger
except ImportError:
    print("WARNING: Could not import 'CustomLogger' from 'log'. Logging features will be disabled.", file=sys.stderr)
    CustomLogger = None

# --- Optional Import for the Output Interface ---
try:
    from src.display import OutputInterfaceAbstraction
except ImportError:
    print("WARNING: Could not import 'OutputInterfaceAbstraction' from 'output_interface_abstraction'. User output features will be disabled.", file=sys.stderr)
    OutputInterfaceAbstraction = None


class Article(ArticleDataClass):
    """
    Represents an article, inheriting data fields from ArticleDataClass
    and adding validation logic, optional logging, and an optional output interface
    through consolidated logging/output methods.
    """

    def __init__(self,
                 article_info: Optional[ArticleDataClass] = None,
                 logger: Optional[CustomLogger] = None,
                 output_interface: Optional[OutputInterfaceAbstraction] = None):
        self._logger = logger
        self._output_interface = output_interface

        super().__init__()

        if article_info:
            self.set_article_info(article_info)

    def _log(self, level: str, message: str, on_verbose: bool = False) -> None:
        """
        Helper method to log a message if a logger is available.

        Args:
            level (str): The logging level (e.g., "debug", "info", "warning", "error").
            message (str): The message to log.
            on_verbose (bool): Passed to logger methods that support it (e.g., debug).
        """
        if not self._logger:
            return

        if level == "debug":
            self._logger.debug(message, on_verbose=on_verbose)
        elif level == "info":
            self._logger.info(message) # Assuming info doesn't use on_verbose
        elif level == "warning":
            self._logger.warning(message)
        elif level == "error":
            self._logger.error(message)
        else:
            # Fallback or raise error for unknown level
            self._logger.info(f"LOG ({level.upper()}): {message}")


    def _log_and_output(self,
                        log_level: str,
                        output_prefix: str,
                        base_message: str,
                        log_on_verbose: bool = False) -> None:
        """
        Helper method to log a message AND output it to the user interface.

        Args:
            log_level (str): The logging level.
            output_prefix (str): A prefix for the user message (e.g., "USER_WARNING:", "NOTICE:").
            base_message (str): The core message content.
            log_on_verbose (bool): Passed to the logger.
        """
        self._log(log_level, base_message, on_verbose=log_on_verbose)

        if self._output_interface:
            self._output_interface.write_message(f"{output_prefix} {base_message}")


    def set_article_info(self, article_info: ArticleDataClass) -> None:
        """
        Updates the article's attributes based on another ArticleDataClass instance.
        Informs the user via output_interface on failure or incompatible type.
        """
        current_article_id_for_error_msg = self.number() if self.number_valid() else "unknown article (pre-update)"

        if not isinstance(article_info, ArticleDataClass):
            if article_info is None:
                self._log("debug", "set_article_info called with None, no changes made.", on_verbose=True)
            else:
                msg = (f"Attempted to update article with incompatible data type: {type(article_info)}. "
                       f"Expected ArticleDataClass. No changes made. (Article: {current_article_id_for_error_msg})")
                self._log_and_output("warning", "USER_WARNING:", msg)
            return

        try:
            for field in dataclasses.fields(article_info):
                value = getattr(article_info, field.name)
                setattr(self, field.name, value)
            self._log("debug", f"Article info updated for number: '{self.number()}' using set_article_info.", on_verbose=True)
        except (AttributeError, TypeError) as e:
            msg = f"Could not update article information for '{current_article_id_for_error_msg}'. Data issue: {e}"
            self._log_and_output("error", "USER_ERROR:", msg)


    def is_valid(self) -> bool:
        """
        Checks if the article is overall valid. Informs user if invalid.
        """
        desc_valid = self.description_valid()
        price_valid = self.price_valid()
        valid = desc_valid and price_valid

        article_id_str = self.number() if self.number_valid() else "Unknown Article"
        desc_preview = (self.description()[:30] + "...") if self.description() and self.description().strip() else "No Description"

        if not valid:
            invalid_parts = []
            if not desc_valid: invalid_parts.append("Description")
            if not price_valid: invalid_parts.append("Price")

            msg = f"Article '{article_id_str}' ('{desc_preview}') is invalid. Issues: {', '.join(invalid_parts)}."
            # Log as debug, but output as a user notice
            self._log_and_output("debug", "NOTICE:", msg, log_on_verbose=True)
        else:
            self._log("debug", f"Article '{article_id_str}' ('{desc_preview}') is valid.", on_verbose=True)
        
        return valid

    # --- Accessor Methods ---
    def number(self) -> str:
        return self.artikelnummer

    def price(self) -> str:
        return self.preis

    def description(self) -> str:
        return self.beschreibung

    # --- Validation Methods (now mostly use _log) ---
    def number_valid(self) -> bool:
        num = self.number()
        valid = (num is not None and num.strip() != "")
        log_context_num_val = self.artikelnummer if self.artikelnummer else "N/A"
        self._log("debug", f"Number validation (for article: '{log_context_num_val}'): value='{num}' -> valid={valid}", on_verbose=True)
        return valid

    def price_valid(self) -> bool:
        price_value = self.price()
        is_none_val = (price_value is None)
        is_empty_or_whitespace_str = (price_value is not None and price_value.strip() == "")
        is_literal_none_str = (price_value == "None")
        valid = not (is_none_val or is_empty_or_whitespace_str or is_literal_none_str)

        log_context_num = self.artikelnummer if self.artikelnummer else "N/A"
        self._log(
            "debug",
            f"Price validation (for article: '{log_context_num}'): value='{price_value}' (type: {type(price_value).__name__}), "
            f"is_none_val={is_none_val}, is_empty_or_whitespace_str={is_empty_or_whitespace_str}, "
            f"is_literal_none_str={is_literal_none_str} -> valid={valid}",
            on_verbose=True
        )
        return valid

    def description_valid(self) -> bool:
        desc = self.description()
        valid = (desc is not None and desc.strip() != "")
        log_context_num = self.artikelnummer if self.artikelnummer else "N/A"
        desc_preview_log = str(desc)[:50] + '...' if desc else 'None/Empty'
        self._log("debug", f"Description validation (for article: '{log_context_num}'): value='{desc_preview_log}' -> valid={valid}", on_verbose=True)
        return valid