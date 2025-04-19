import logging
import threading
from typing import List, Dict, Optional, Final # Added Optional, Final

# Define valid log types as constants for better maintainability and validation
VALID_LOG_TYPES: Final = ("INFO", "WARNING", "DEBUG", "ERROR")
LogType = str # Define a type alias for clarity

class OneLineData:
    """
    Stores data for a single active one-line logging session.

    Attributes:
        data (List[str]): A list accumulating log message parts.
                          Using a list is often more efficient for appends
                          than string concatenation in a loop.
    """
    def __init__(self) -> None:
        # Store parts as a list, join them at the end
        self.data: List[str] = []

    def append(self, msg: str) -> None:
        """Appends a message part."""
        self.data.append(msg)

    def get_log_message(self) -> str:
        """Returns the final concatenated log message."""
        # Consider a different separator if needed (e.g., ' ')
        return "".join(self.data)


class LogHelper:
    """
    Manages the state for one-line logging sessions, ensuring thread safety.

    Internal stack-based structure allows for nested one-line logs per type.
    """
    def __init__(self) -> None:
        # Use a stack (list) for each log type to handle nested calls
        self._one_line_stacks: Dict[LogType, List[OneLineData]] = {
            level: [] for level in VALID_LOG_TYPES
        }
        self._skip_logging: Dict[LogType, bool] = {
            level: False for level in VALID_LOG_TYPES
        }
        self._lock = threading.Lock()

    def _validate_log_type(self, log_type: LogType) -> None:
        """Raises ValueError if log_type is invalid."""
        if log_type not in VALID_LOG_TYPES:
            raise ValueError(f"Invalid log_type: {log_type}. Must be one of {VALID_LOG_TYPES}")

    def start_new_one_line(self, log_type: LogType) -> None:
        """Starts a new one-line log session for the specified type."""
        self._validate_log_type(log_type)
        with self._lock:
            self._one_line_stacks[log_type].append(OneLineData())

    def append_to_one_line(self, log_type: LogType, data: str) -> None:
        """Appends data to the currently active one-line log session."""
        self._validate_log_type(log_type)
        with self._lock:
            # Only append if logging is not skipped and a session is active
            if not self._skip_logging.get(log_type, False) and self._one_line_stacks[log_type]:
                # Append to the latest (top of the stack) session
                self._one_line_stacks[log_type][-1].append(data)

    def is_one_line_active(self, log_type: LogType) -> bool:
        """Checks if a one-line log session is currently active for the type."""
        self._validate_log_type(log_type)
        with self._lock:
            # Active if the stack for this type is not empty
            return bool(self._one_line_stacks[log_type])

    def stop_one_line(self, log_type: LogType) -> str:
        """
        Stops the most recent one-line log session for the type and returns
        the accumulated log message. Removes the session from the stack.
        Returns an empty string if no session was active.
        """
        self._validate_log_type(log_type)
        with self._lock:
            if self._one_line_stacks[log_type]:
                # Pop the latest session from the stack
                one_line_session = self._one_line_stacks[log_type].pop()
                return one_line_session.get_log_message()
            return "" # No active session to stop

    def skip_logging(self, log_type: LogType, status: bool) -> None:
        """Sets whether logging should be skipped for a specific type."""
        self._validate_log_type(log_type)
        with self._lock:
            self._skip_logging[log_type] = status

    def is_logging_skipped(self, log_type: LogType) -> bool:
        """Checks if logging is currently skipped for the specified type."""
        self._validate_log_type(log_type)
        with self._lock:
            # Use .get() to be safe, though validation should prevent KeyErrors
            return self._skip_logging.get(log_type, False)


class CustomLogger:
    """
    An enhanced logger supporting standard and one-line logging modes.

    This logger instance manages its own configuration (level, handlers, formatters)
    without interfering with the global logging state, unless explicitly desired.
    It uses LogHelper internally for thread-safe one-line log management.
    """
    def __init__(
        self,
        name: str = __name__, # Allow naming the logger
        log_level: str = "INFO",
        verbose_enabled: bool = False,
        log_format: str = '%(asctime)s - %(name)s - %(levelname)s - %(message)s', # Configurable format
        date_format: str = '%Y-%m-%d %H:%M:%S', # Configurable date format
        handler: Optional[logging.Handler] = None # Allow injecting a handler
    ) -> None:
        """
        Initializes the CustomLogger.

        Args:
            name (str): The name for the logger instance.
            log_level (str): The minimum log level (e.g., "DEBUG", "INFO").
            verbose_enabled (bool): If True, messages logged with on_verbose=True are processed.
            log_format (str): The format string for log messages.
            date_format (str): The format string for the date/time part of logs.
            handler (Optional[logging.Handler]): An optional pre-configured handler.
                                                 If None, a default StreamHandler (console) is created.
        """
        self._verbose = verbose_enabled
        self._log_helper = LogHelper()

        # --- Improved Logger Configuration ---
        self._logger = logging.getLogger(name)
        # Prevent duplicate messages if the root logger is also configured
        self._logger.propagate = False

        # Set level based on input string
        numeric_level = getattr(logging, log_level.upper(), logging.INFO)
        self._logger.setLevel(numeric_level)

        # Configure handler and formatter
        if handler:
            self._handler = handler
        else:
            # Default to console output if no handler is provided
            self._handler = logging.StreamHandler() # Outputs to stderr by default

        formatter = logging.Formatter(log_format, datefmt=date_format)
        self._handler.setFormatter(formatter)

        # Add the handler only if the logger doesn't already have handlers
        # This prevents adding duplicate handlers if the logger instance is reused
        if not self._logger.handlers:
            self._logger.addHandler(self._handler)
        # --- End Logger Configuration ---

        # Map string level names to logging constants
        self._level_mapping: Dict[LogType, int] = {
            "INFO": logging.INFO,
            "WARNING": logging.WARNING,
            "DEBUG": logging.DEBUG,
            "ERROR": logging.ERROR
        }

    def set_level(self, log_level: str) -> None:
        """Changes the logging level dynamically."""
        numeric_level = getattr(logging, log_level.upper(), None)
        if numeric_level is not None:
            self._logger.setLevel(numeric_level)
        else:
            self.warning(f"Attempted to set invalid log level: {log_level}")

    def skip_logging(self, log_type: LogType, status: bool) -> None:
        """
        Enables or disables skipping of logs for the specified type.
        Affects both standard and one-line logs.
        """
        try:
            self._log_helper.skip_logging(log_type, status)
        except ValueError as e:
            self.error(f"Configuration error: {e}") # Log the validation error

    def _log(self, log_type: LogType, msg: str, on_verbose: bool = False) -> None:
        """Internal log handling method."""
        if on_verbose and not self._verbose:
            return # Skip if verbose mode required but not enabled

        try:
            if self._log_helper.is_logging_skipped(log_type):
                return # Skip if this log type is globally skipped

            if self._log_helper.is_one_line_active(log_type):
                # Append to the active one-line log session
                self._log_helper.append_to_one_line(log_type, msg)
            else:
                # Log directly using the standard logger
                level = self._level_mapping.get(log_type, logging.INFO) # Default to INFO if somehow invalid
                self._logger.log(level, msg)

        except ValueError as e:
             # Log validation errors from LogHelper methods
             # Use standard error logging to ensure visibility
             self._logger.error(f"Logging error: {e}")
        except Exception as e:
             # Catch unexpected errors during logging
             self._logger.error(f"Unexpected logging failure: {e}", exc_info=True)


    def one_line_log(self, log_type: LogType, start: bool) -> None:
        """
        Starts or stops a one-line logging session for the specified type.

        Args:
            log_type (LogType): The type of log ("INFO", "DEBUG", etc.).
            start (bool): If True, starts a new one-line session.
                          If False, stops the current session and logs the
                          accumulated message.
        """
        try:
            if start:
                self._log_helper.start_new_one_line(log_type)
            else:
                # Stop the session and get the accumulated data
                log_data = self._log_helper.stop_one_line(log_type)
                # Log the accumulated data as a single standard log entry
                # Check if log_data is not empty before logging
                if log_data and not self._log_helper.is_logging_skipped(log_type):
                     level = self._level_mapping.get(log_type, logging.INFO)
                     self._logger.log(level, log_data)
        except ValueError as e:
            self.error(f"Configuration error: {e}")

    # --- Public Logging Methods ---

    def debug(self, msg: str, on_verbose: bool = False) -> None:
        """Logs a Debug message."""
        self._log("DEBUG", msg, on_verbose)

    def info(self, msg: str, on_verbose: bool = False) -> None:
        """Logs an Info message."""
        self._log("INFO", msg, on_verbose)

    def warning(self, msg: str, on_verbose: bool = False) -> None:
        """Logs a Warning message."""
        self._log("WARNING", msg, on_verbose)

    def error(self, msg: str, on_verbose: bool = False) -> None:
        """Logs an Error message."""
        self._log("ERROR", msg, on_verbose)

    @property
    def verbose(self) -> bool:
        """Returns True if verbose logging is enabled."""
        return self._verbose

    # --- Example Usage ---
if __name__ == "__main__":
    # Create logger instance - verbosity enabled, level DEBUG
    # Uses the default console handler and format
    logger = CustomLogger(name="MyTestApp", log_level="DEBUG", verbose_enabled=True)

    print("--- Standard Logging ---")
    logger.info("This is a standard info message.")
    logger.debug("This is a standard debug message.") # Will show because level is DEBUG
    logger.info("This verbose info message WILL appear.", on_verbose=True)

    # Test verbose disabled
    logger_non_verbose = CustomLogger(name="QuietApp", log_level="INFO", verbose_enabled=False)
    logger_non_verbose.info("This info message WILL appear.")
    logger_non_verbose.info("This verbose info message WILL NOT appear.", on_verbose=True)
    logger_non_verbose.debug("This debug message WILL NOT appear (level INFO).")


    print("\n--- One-Line Logging ---")
    logger.one_line_log("INFO", start=True)
    logger.info("Processing item 1...") # Appended
    logger.info("Item 1 done. ")        # Appended
    logger.info("Processing item 2...") # Appended
    logger.debug("This is a debug message during one-line INFO - logs separately.")
    logger.info("Item 2 done.")         # Appended
    logger.one_line_log("INFO", start=False) # Stops and logs the accumulated INFO message

    print("\n--- Nested One-Line Logging ---")
    logger.one_line_log("DEBUG", start=True) # Outer debug session
    logger.debug("Outer part 1...")
    logger.one_line_log("DEBUG", start=True) # Inner debug session
    logger.debug("Inner part A...")
    logger.debug("Inner part B...")
    logger.one_line_log("DEBUG", start=False) # Stop inner session -> logs "Inner part A...Inner part B..."
    logger.debug("Outer part 2...")
    logger.one_line_log("DEBUG", start=False) # Stop outer session -> logs "Outer part 1...Outer part 2..."


    print("\n--- Skipping Logging ---")
    logger.skip_logging("INFO", True)
    logger.info("This INFO message will be skipped.")
    logger.one_line_log("INFO", start=True)
    logger.info("This part of one-line INFO will be skipped...")
    logger.info("...and this part too.")
    logger.one_line_log("INFO", start=False) # Stops, but logging is skipped, so nothing appears
    logger.warning("This WARNING message is NOT skipped.")
    logger.skip_logging("INFO", False) # Re-enable INFO logging
    logger.info("This INFO message appears again.")


    print("\n--- Invalid Log Type Handling ---")
   
    # This part correctly demonstrates the handling of invalid types via the public API:
    try:
        # Attempt to use an invalid type with a public method that accepts log_type
        logger.one_line_log("WRONG_TYPE", start=True)
    except ValueError as e:
         # The logger itself should log an error message internally due to the try/except
         # block within one_line_log. Catching it here is optional for demonstration.
         print(f"Caught expected ValueError in example block: {e}")
    # You could also test skip_logging:
    logger.skip_logging("ANOTHER_BAD_TYPE", True) # This will also log an error internally