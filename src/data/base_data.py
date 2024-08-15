from typing import Optional, Callable, Dict, List
from data import *
import time


class BaseData(JsonLoader, JSONData):

    def __init__(self, json_file_path: str, error_handler = None) -> None:
        JsonLoader.__init__(self,json_file_path, error_handler)
        
        try: 
            json_data =  self.get_data()
            _export_header = HeaderDataClass(**json_data[0])
            _base_info = BaseInfoDataClass(**json_data[1])
            _main_numbers = [MainNumberDataClass(**table) for table in json_data[2:-1]]
            _sellers = SellerListDataClass(**json_data[-1])
            JSONData.__init__(self,export_header= _export_header,base_info= _base_info,
                            main_numbers_list= _main_numbers,sellers= _sellers)
            
        except Exception as e:
            error_handler.error(f"Error occured during JSON loading: {str(e)}") if error_handler else None

    def __handle_error(self, type: str, msg: str): 
        fnc = self.error_handler().log(type,msg)

    def get_seller_list(self) -> List[SellerDataClass]:
        return self.sellers.data
    
    def get_main_number_list(self) -> List[MainNumberDataClass]:
        return self.main_numbers_list
    
    def verify_data(self):
        seller_quantity = len(self.get_seller_list())
        article_list_quatity = len(self.get_main_number_list())
        status = ">> Datenbank OK" if seller_quantity == article_list_quatity else ">> Datenbank Fehler"
            
        self.__handle_error("INFO", "Prüfe Datenbank:\n" + 
                            "========================\n" + 
                            f"    >> Anzahl Verkäufer: {seller_quantity}\n" +
                            f"    >> Anzahl Artikel Listen: {article_list_quatity}\n"+
                            f"    {status}\n"+ 
                             "========================\n")
        time.sleep(5)

