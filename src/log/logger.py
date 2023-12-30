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
__indendation_value__ = '..' 

class OneLineData:
    
    def __init__(self, enabled: bool = False, data:str = "") -> None:
        
        self.__enabled: bool = enabled        
        self.__data: str = data

    @property
    def enabled(self):
        return self.__enabled
    
    @enabled.setter
    def enabled(self,status:bool):
        self.__enabled = status

    @property
    def data(self):
        return self.__data
    
    @data.setter
    def data(self,data:str):
        self.__data = data


class LogHelper:

    def __init__(self) -> None:
       
        self.__one_line_info: OneLineData = []
        self.__one_line_warn: OneLineData = []
        self.__one_line_debug: OneLineData = []
        self.__one_line_error: OneLineData = []

        self.__one_line_data = {
            "INFO"   : self.__one_line_info, 
            "WARNING": self.__one_line_warn,
            "DEBUG"  : self.__one_line_debug,
            "ERROR"  : self.__one_line_error
        }

        self.__skip_logging = {
            "INFO"   : True,
            "WARNING": True,
            "DEBUG"  : True,
            "ERROR"  : True
        }
   
    def __get_one_line_data_list(self, type):
        return self.__one_line_data[type]

    def log_new_one_line(self, type: str):
        data = self.__get_one_line_data_list(type)
        new_data = OneLineData(enabled=True)
        data.append(new_data)

    def log(self,type:str, data: str):
        if self.logging_skiped(type) == False:
            log_data: List[OneLineData] = self.__get_one_line_data_list(type)
            log_data[-1].data += data

    def log_enabled(self, type: str):
        log_list: List[OneLineData] = self.__get_one_line_data_list(type)
        if len(log_list) > 0:
            log_data: OneLineData = log_list[-1]
            return log_data.enabled
        return False

    def stop_line_log(self, type: str):
        log_data = ''
        data_list = self.__get_one_line_data_list(type)
        one_line_data: OneLineData = self.__get_one_line_data_list(type)[-1]
        if len(data_list) > 0:
            log_data = one_line_data.data
            one_line_data.enabled = False

        return log_data
    
    def delete_line_log(self, type: str):
        data_list = self.__get_one_line_data_list(type)
        if len(data_list) > 0:
            data_list.pop()
    
    def skip_logging(self,type: str, status: bool):
        self.__skip_logging[type] = status
        
    def logging_skiped(self, type: str):
        return self.__skip_logging[type]

__log_helper = LogHelper()

def __get(type: str):
    lvl = logging._nameToLevel[type]
    return _levelToInterface[lvl]

def setup(log_level = "INFO", verbose_enabled = False) -> None:

    global __verbose__ 
    level = logging._nameToLevel[log_level]
    logging.basicConfig(level=level, format='%(levelname)s: %(message)s')
    __verbose__ = verbose_enabled


def indentation_depth():
    depth = len(inspect.stack()) - 12
    indentation = ''
    for i in range(depth):
        indentation += __indendation_value__  # Vier Leerzeichen pro Einrückungsebene
    return indentation

def skip_logging(type: str, status: bool):
    global __log_helper
    __log_helper.skip_logging(type, status)

def log(type:str, msg:str, on_verbose = False):
    global __log_helper
    if on_verbose and not verbose():
        return

    if not __log_helper.log_enabled(type):
        if msg != '' and __log_helper.logging_skiped(type) == False:
            interface = __get(type)
            interface(msg)
        __log_helper.delete_line_log(type)
    else:
        __log_helper.log(type,msg)
        

def log_one_line(type: str, enabled: bool = True):
    global __log_helper

    if enabled:
        __log_helper.log_new_one_line(type)
    else: 
        log_data = __log_helper.stop_line_log(type)
        log(type,log_data)
      
def verbose():
    global __verbose__
    return __verbose__

def debug(msg: str, on_verbose=False):
    log("DEBUG",msg,on_verbose)
    

def info(msg:str, on_verbose = False):
    log("INFO",msg,on_verbose)

def warning(msg:str, on_verbose = False):
    log("WARNING",msg,on_verbose)

def error(msg:str, on_verbose = False):
    log("ERROR",msg,on_verbose)
