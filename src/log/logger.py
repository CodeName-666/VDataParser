import logging
import inspect
from typing import List

LOG_DISABLED = 0
LOG_VERBOSE = 1
LOG_LOGGING = 2

_levelToInterface = {
    logging.INFO: logging.info,
    logging.WARNING: logging.warning,
    logging.DEBUG: logging.debug,
    logging.ERROR: logging.error
}

__verbose__ = False
__indendation_value__ = '..'  # Indentation value for log messages

class OneLineData:
    """
    A class to store one-line log data.
    
    Attributes:
    -----------
    __enabled : bool
        Indicates if one-line logging is enabled.
    __data : str
        The log data.
    """
    
    def __init__(self, enabled: bool = False, data: str = "") -> None:
        """
        Initializes the OneLineData with enabled status and data.
        
        Parameters:
        -----------
        enabled : bool, optional
            Indicates if one-line logging is enabled (default is False).
        data : str, optional
            The log data (default is "").
        """
        self.__enabled: bool = enabled        
        self.__data: str = data

    @property
    def enabled(self):
        """
        Gets the enabled status.
        
        Returns:
        --------
        bool
            The enabled status.
        """
        return self.__enabled
    
    @enabled.setter
    def enabled(self, status: bool):
        """
        Sets the enabled status.
        
        Parameters:
        -----------
        status : bool
            The enabled status.
        """
        self.__enabled = status

    @property
    def data(self):
        """
        Gets the log data.
        
        Returns:
        --------
        str
            The log data.
        """
        return self.__data
    
    @data.setter
    def data(self, data: str):
        """
        Sets the log data.
        
        Parameters:
        -----------
        data : str
            The log data.
        """
        self.__data = data


class LogHelper:
    """
    A helper class for managing log data.
    
    Attributes:
    -----------
    __one_line_info : List[OneLineData]
        List of one-line info log data.
    __one_line_warn : List[OneLineData]
        List of one-line warning log data.
    __one_line_debug : List[OneLineData]
        List of one-line debug log data.
    __one_line_error : List[OneLineData]
        List of one-line error log data.
    __one_line_data : dict
        Dictionary mapping log types to their respective one-line data lists.
    __skip_logging : dict
        Dictionary indicating whether logging is skipped for each log type.
    """
    
    def __init__(self) -> None:
        """
        Initializes the LogHelper with empty one-line data lists and skip logging flags.
        """
        self.__one_line_info: List[OneLineData] = []
        self.__one_line_warn: List[OneLineData] = []
        self.__one_line_debug: List[OneLineData] = []
        self.__one_line_error: List[OneLineData] = []

        self.__one_line_data = {
            "INFO": self.__one_line_info, 
            "WARNING": self.__one_line_warn,
            "DEBUG": self.__one_line_debug,
            "ERROR": self.__one_line_error
        }

        self.__skip_logging = {
            "INFO": False,
            "WARNING": False,
            "DEBUG": False,
            "ERROR": False
        }
   
    def __get_one_line_data_list(self, type: str) -> List[OneLineData]:
        """
        Gets the one-line data list for the specified log type.
        
        Parameters:
        -----------
        type : str
            The log type.
        
        Returns:
        --------
        List[OneLineData]
            The one-line data list for the specified log type.
        """
        return self.__one_line_data[type]

    def log_new_one_line(self, type: str):
        """
        Starts a new one-line log for the specified log type.
        
        Parameters:
        -----------
        type : str
            The log type.
        """
        data = self.__get_one_line_data_list(type)
        new_data = OneLineData(enabled=True)
        data.append(new_data)

    def log(self, type: str, data: str):
        """
        Logs data to the current one-line log of the specified log type.
        
        Parameters:
        -----------
        type : str
            The log type.
        data : str
            The log data.
        """
        if not self.logging_skiped(type):
            log_data: List[OneLineData] = self.__get_one_line_data_list(type)
            log_data[-1].data += data

    def log_enabled(self, type: str) -> bool:
        """
        Checks if one-line logging is enabled for the specified log type.
        
        Parameters:
        -----------
        type : str
            The log type.
        
        Returns:
        --------
        bool
            True if one-line logging is enabled, False otherwise.
        """
        log_list: List[OneLineData] = self.__get_one_line_data_list(type)
        if len(log_list) > 0:
            log_data: OneLineData = log_list[-1]
            return log_data.enabled
        return False

    def stop_line_log(self, type: str) -> str:
        """
        Stops the current one-line log for the specified log type and returns the log data.
        
        Parameters:
        -----------
        type : str
            The log type.
        
        Returns:
        --------
        str
            The log data.
        """
        log_data = ''
        data_list = self.__get_one_line_data_list(type)
        if len(data_list) > 0:
            one_line_data: OneLineData = data_list[-1]
            log_data = one_line_data.data
            one_line_data.enabled = False

        return log_data
    
    def delete_line_log(self, type: str):
        """
        Deletes the current one-line log for the specified log type.
        
        Parameters:
        -----------
        type : str
            The log type.
        """
        data_list = self.__get_one_line_data_list(type)
        if len(data_list) > 0:
            data_list.pop()
    
    def skip_logging(self, type: str, status: bool):
        """
        Sets the skip logging status for the specified log type.
        
        Parameters:
        -----------
        type : str
            The log type.
        status : bool
            The skip logging status.
        """
        self.__skip_logging[type] = status
        
    def logging_skiped(self, type: str) -> bool:
        """
        Checks if logging is skipped for the specified log type.
        
        Parameters:
        -----------
        type : str
            The log type.
        
        Returns:
        --------
        bool
            True if logging is skipped, False otherwise.
        """
        return self.__skip_logging[type]

__log_helper = LogHelper()

def __get(type: str):
    """
    Gets the logging interface for the specified log type.
    
    Parameters:
    -----------
    type : str
        The log type.
    
    Returns:
    --------
    function
        The logging interface function.
    """
    lvl = logging._nameToLevel[type]
    return _levelToInterface[lvl]

def setup(log_level = "INFO", verbose_enabled = False) -> None:
    """
    Sets up the logging configuration.
    
    Parameters:
    -----------
    log_level : str, optional
        The log level (default is "INFO").
    verbose_enabled : bool, optional
        Indicates if verbose logging is enabled (default is False).
    """
    global __verbose__ 
    logging.basicConfig(level=log_level, format='%(levelname)s: %(message)s')
    __verbose__ = verbose_enabled

def indentation_depth() -> str:
    """
    Calculates the indentation depth based on the call stack.
    
    Returns:
    --------
    str
        The indentation string.
    """
    depth = len(inspect.stack()) - 12
    indentation = ''
    for i in range(depth):
        indentation += __indendation_value__  # Four spaces per indentation level
    return indentation

def skip_logging(type: str, status: bool):
    """
    Sets the skip logging status for the specified log type.
    
    Parameters:
    -----------
    type : str
        The log type.
    status : bool
        The skip logging status.
    """
    global __log_helper
    __log_helper.skip_logging(type, status)

def log(type: str, msg: str, on_verbose = False):
    """
    Logs a message of the specified log type.
    
    Parameters:
    -----------
    type : str
        The log type.
    msg : str
        The log message.
    on_verbose : bool, optional
        Indicates if the message should be logged only in verbose mode (default is False).
    """
    global __log_helper
    if on_verbose and not verbose():
        return

    if not __log_helper.log_enabled(type):
        if msg != '' and not __log_helper.logging_skiped(type):
            interface = __get(type)
            interface(msg)
        __log_helper.delete_line_log(type)
    else:
        __log_helper.log(type, msg)
        
def log_one_line(type: str, enabled: bool = True):
    """
    Starts or stops one-line logging for the specified log type.
    
    Parameters:
    -----------
    type : str
        The log type.
    enabled : bool, optional
        Indicates if one-line logging should be enabled (default is True).
    """
    global __log_helper

    if enabled:
        __log_helper.log_new_one_line(type)
    else: 
        log_data = __log_helper.stop_line_log(type)
        log(type, log_data)
      
def verbose() -> bool:
    """
    Checks if verbose logging is enabled.
    
    Returns:
    --------
    bool
        True if verbose logging is enabled, False otherwise.
    """
    global __verbose__
    return __verbose__

def debug(msg: str, on_verbose = False):
    """
    Logs a debug message.
    
    Parameters:
    -----------
    msg : str
        The debug message.
    on_verbose : bool, optional
        Indicates if the message should be logged only in verbose mode (default is False).
    """
    log("DEBUG", msg, on_verbose)
    
def info(msg: str, on_verbose = False):
    """
    Logs an info message.
    
    Parameters:
    -----------
    msg : str
        The info message.
    on_verbose : bool, optional
        Indicates if the message should be logged only in verbose mode (default is False).
    """
    log("INFO", msg, on_verbose)

def warning(msg: str, on_verbose = False):
    """
    Logs a warning message.
    
    Parameters:
    -----------
    msg : str
        The warning message.
    on_verbose : bool, optional
        Indicates if the message should be logged only in verbose mode (default is False).
    """
    log("WARNING", msg, on_verbose)

def error(msg: str, on_verbose = False):
    """
    Logs an error message.
    
    Parameters:
    -----------
    msg : str
        The error message.
    on_verbose : bool, optional
        Indicates if the message should be logged only in verbose mode (default is False).
    """
    log("ERROR", msg, on_verbose)
