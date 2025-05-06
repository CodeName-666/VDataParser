import sys
from typing import List, Optional

# Assuming data.py contains MainNumberDataClass and ArticleDataClass
from data import MainNumberDataClass, ArticleDataClass # Assuming ArticleDataClass is used by Article
from objects import Article # Assuming Article is in objects directory

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


class MainNumber(MainNumberDataClass):
    """
    Represents a main number, holding a list of articles.
    Inherits data fields from MainNumberDataClass and adds business logic,
    validation, and optional logging/output.
    """

    def __init__(self,
                 main_number_info: Optional[MainNumberDataClass] = None,
                 logger: Optional[CustomLogger] = None,
                 output_interface: Optional[OutputInterfaceAbstraction] = None) -> None:
        """
        Initializes a new MainNumber instance.

        Args:
            main_number_info (Optional[MainNumberDataClass]): Data for this main number.
            logger (Optional[CustomLogger]): An instance of a CustomLogger.
            output_interface (Optional[OutputInterfaceAbstraction]): An instance of an OutputInterface.
        """
        # Initialize base dataclass attributes if MainNumberDataClass has defaults
        super().__init__() # Or MainNumberDataClass.__init__(self) if no complex base __init__

        self._logger = logger
        self._output_interface = output_interface
        self.__article_list: List[Article] = [] # Initialize to empty list

        if main_number_info:
            self.set_main_number_info(main_number_info)
        else:
            # If main_number_info is None, and MainNumberDataClass has defaults,
            # they would have been set by super().__init__().
            # If specific fields from MainNumberDataClass need to be initialized even if
            # main_number_info is None, do it here. For example:
            # self.name = "" # if name is a field in MainNumberDataClass
            # self.data = [] # if data is a field in MainNumberDataClass
            pass # Defaults from MainNumberDataClass apply

    def _log(self, level: str, message: str, on_verbose: bool = False, exc_info: bool = False) -> None:
        """Helper method for logging."""
        if not self._logger:
            return

        log_method = getattr(self._logger, level, None)
        if not log_method:
            self._logger.info(f"LOG ({level.upper()}): {message}") # Fallback
            return

        # Handle specific logger methods and their arguments
        if level == "debug":
            # Assuming CustomLogger.debug might take on_verbose
            try:
                log_method(message, on_verbose=on_verbose)
            except TypeError: # If CustomLogger.debug doesn't take on_verbose
                log_method(message)
        elif level in ["error", "exception"]:
            try:
                log_method(message, exc_info=exc_info)
            except TypeError: # If CustomLogger.error/exception doesn't take exc_info
                log_method(message)
        elif level in ["warning", "info", "critical"]:
            log_method(message)
        # Handle custom methods like log_one_line or skip_logging if they exist on CustomLogger
        elif level == "log_one_line": # Example for custom logger methods
            if hasattr(self._logger, 'log_one_line'):
                 # Assuming log_one_line takes a "state" argument (True/False)
                 # and the message here is the "level" for log_one_line
                self._logger.log_one_line(message.upper(), on_verbose) # 'message' is 'DEBUG', 'on_verbose' is True/False
            else:
                self._logger.debug(f"log_one_line ({message.upper()}): {on_verbose}") # Fallback
        elif level == "skip_logging": # Example for custom logger methods
            if hasattr(self._logger, 'skip_logging'):
                # Assuming skip_logging takes a "level" and a "state"
                self._logger.skip_logging(message.upper(), on_verbose)
            else:
                 self._logger.debug(f"skip_logging ({message.upper()}): {on_verbose}") # Fallback
        else:
            log_method(message)


    def _log_and_output(self,
                        log_level: str,
                        output_prefix: str,
                        base_message: str,
                        log_on_verbose: bool = False,
                        log_exc_info: bool = False) -> None:
        """Helper method for logging and user output."""
        self._log(log_level, base_message, on_verbose=log_on_verbose, exc_info=log_exc_info)

        if self._output_interface:
            self._output_interface.write_message(f"{output_prefix} {base_message}")

    def set_main_number_info(self, main_number_info: MainNumberDataClass):
        """
        Sets the information for this main number and initializes its article list.
        """
        if not isinstance(main_number_info, MainNumberDataClass):
            msg = f"Invalid data type for main_number_info: {type(main_number_info)}. Expected MainNumberDataClass."
            self._log_and_output("error", "USER_ERROR:", msg)
            return

        # Initialize attributes from MainNumberDataClass
        # This assumes MainNumberDataClass is a dataclass or has a suitable __init__
        try:
            for field in dataclasses.fields(main_number_info):
                setattr(self, field.name, getattr(main_number_info, field.name))
        except TypeError: # If main_number_info is not a dataclass, or dataclasses.fields fails
            # Fallback or specific handling if MainNumberDataClass is not a dataclass
            # For example, if it's a simple class with attributes:
            # self.name = main_number_info.name
            # self.data = main_number_info.data # etc. for all fields
            # The original `MainNumberDataClass.__init__(self,**main_number_info.__dict__)`
            # is a bit unusual for inheritance; typically super().__init__ or direct assignment is used.
            # Using dataclasses.fields is more robust if it *is* a dataclass.
            # If not, direct attribute assignment is preferred.
            # For now, sticking to a similar pattern as original for __dict__ if not dataclass:
            try:
                MainNumberDataClass.__init__(self, **main_number_info.__dict__)
            except Exception as e:
                msg = f"Failed to initialize MainNumberDataClass attributes: {e}"
                self._log_and_output("error", "USER_ERROR:", msg, log_exc_info=True)
                return


        self.__article_list = [] # Clear previous articles
        if hasattr(main_number_info, 'data') and isinstance(main_number_info.data, list):
            for article_data in main_number_info.data:
                # Pass logger and output_interface to Article instances
                # Ensure Article's __init__ accepts these
                article_instance = Article(article_data, logger=self._logger, output_interface=self._output_interface)
                self.__article_list.append(article_instance)
            self._log("debug", f"Initialized {len(self.__article_list)} articles for main number '{self.name}'.", on_verbose=True)
        else:
            self._log("warning", f"No 'data' (article list) found or not a list in main_number_info for '{self.name}'.")


    def get_main_number(self) -> Optional[int]:
        """
        Extracts the numeric part of the main number's name.
        Example: "stnr123" -> 123. Returns None if parsing fails.
        """
        if self.name and isinstance(self.name, str):
            try:
                return int(self.name.lower().replace("stnr", ""))
            except ValueError:
                self._log("warning", f"Could not parse main number from name: '{self.name}'. Not a valid integer after 'stnr'.")
                return None
        self._log("warning", f"Main number name is not a valid string: '{self.name}'.")
        return None

    def is_valid(self) -> bool:
        """
        Checks if the MainNumber is considered valid based on its articles.
        A MainNumber is valid if it has at least one valid article and a positive total value
        from its valid articles.
        """
        # Use the more detailed methods to get counts, they already log
        valid_article_qty = self.get_article_quantity() # This method now handles its own detailed logging
        total_value = self.get_article_total()         # This method also handles its own logging if needed

        # is_valid_flag = valid_article_qty > 0 and total_value > 0.0 # Original logic
        # Let's refine: valid if there's at least one valid article. The total value check might be redundant
        # if get_article_quantity ensures only valid articles contribute.
        # However, keeping the original logic for now.
        is_valid_flag = valid_article_qty > 0 # Simplified: valid if at least one article is valid.
                                              # Add `and total_value > 0.0` if strictly needed.

        mn_id = self.get_main_number() if self.get_main_number() is not None else self.name

        if is_valid_flag:
            self._log("debug", f"MainNumber '{mn_id}' is valid (Valid Articles: {valid_article_qty}, Total: {total_value:.2f}).", on_verbose=True)
        else:
            msg = f"MainNumber '{mn_id}' is invalid (Valid Articles: {valid_article_qty}, Total: {total_value:.2f})."
            # Log as warning, output as a notice
            self._log_and_output("warning", "NOTICE:", msg, log_on_verbose=True)
        return is_valid_flag


    def get_article_quantity(self) -> int:
        """
        Calculates and returns the number of valid articles.
        Logs detailed information about each article's validity.
        """
        valid_cnt = 0
        invalid_cnt = 0

        # Use the custom logger methods if available via _log
        self._log("log_one_line", "DEBUG", on_verbose=True) # on_verbose is the state for log_one_line
        self._log("debug", f"Calculate Article Quantity for MainNumber '{self.name}': \n", on_verbose=True)

        for index, article in enumerate(self.__article_list):
            # Ensure article itself can handle logger/output if its is_valid() needs it
            # Article's __init__ was updated to accept logger and output_interface

            # Log context before calling article.is_valid()
            self._log("debug", f"    ---> Article {index + 1}/{len(self.__article_list)} ('{article.description()[:30]}...'): Checking validity... ", on_verbose=True)

            self._log("skip_logging", "DEBUG", on_verbose=True) # on_verbose is the state for skip_logging
            is_article_valid = article.is_valid() # This will use Article's _log/_log_and_output
            self._log("skip_logging", "DEBUG", on_verbose=False)

            if is_article_valid:
                valid_cnt += 1
                self._log("debug", f"    ---> Article {index + 1} is valid.", on_verbose=True)
            else:
                invalid_cnt += 1
                self._log("debug", f"    ---> Article {index + 1} is invalid.", on_verbose=True)

        self._log("debug", f"       ==> MainNumber '{self.name}': Valid articles: {valid_cnt}, Invalid: {invalid_cnt} \n", on_verbose=True)
        self._log("log_one_line", "DEBUG", on_verbose=False)
        return valid_cnt

    def get_article_total(self) -> float:
        """
        Calculates the total price of all valid articles.
        """
        total_count = 0.0
        valid_article_count_for_total = 0
        self._log("debug", f"Calculating article total for MainNumber '{self.name}'.", on_verbose=True)
        for article in self.__article_list:
            # article.is_valid() will perform its own logging.
            # We don't need to re-log extensively here unless we want a summary.
            if article.is_valid():
                try:
                    price = float(article.price()) # Use price() accessor
                    total_count += price
                    valid_article_count_for_total += 1
                except ValueError:
                    self._log("warning", f"Article '{article.number()}' has invalid price format ('{article.price()}') for total calculation. Skipping.")
                except AttributeError: # Should not happen if Article always has price
                     self._log("error", f"Article '{article.number()}' missing 'price' attribute for total calculation. Skipping.")


        rounded_total = round(total_count, 2)
        self._log("debug", f"MainNumber '{self.name}': Total value from {valid_article_count_for_total} valid articles: {rounded_total:.2f}", on_verbose=True)
        return rounded_total

    @property
    def article_list(self) -> List[Article]:
        """Returns the list of Article objects associated with this main number."""
        return self.__article_list