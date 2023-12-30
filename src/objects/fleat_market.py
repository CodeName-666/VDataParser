from data import SellerDataClass
from data import MainNumberDataClass

from .seller import Seller
from .main_number import MainNumber
from typing import List



class FleatMarket:
    def __init__(self) -> None:
        self.__seller_list: List[Seller] = []
        self.__main_number_list: List[MainNumber] = []

    def set_seller_data(self, seller_data_list: SellerDataClass):
        self.__seller_list = [Seller(seller_data) for seller_data in seller_data_list]

    def set_main_number_data(self,main_number_data_list: List[MainNumberDataClass]):       
        self.__main_number_list = [MainNumber(main_number) for main_number in main_number_data_list]
               
    def get_seller_list(self):
        return self.__seller_list

    def get_main_number_data_list(self):
        return self.__main_number_list

    def get_seller_data(self, main_number: int):
        if main_number <= len(self.__seller_list) :
            return self.__seller_list[main_number]
        else: 
            return None