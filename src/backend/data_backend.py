
from data import BaseData
from PySide6.QtCore import QObject


class DataInterface(QObject):

    def __init__(self, json_file_path: str) -> None:
        self.data: BaseData = BaseData(json_file_path)

    def get_seller_list(self): 
        return self.data.get_seller_list()

    def get_main_number_list(self):
        return self.data.get_main_number_list()
    
    