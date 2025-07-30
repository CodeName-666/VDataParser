from .data_class_definition import *


def __getattr__(name: str):
    if name == "Article":
        from .article import Article
        return Article
    if name == "Seller":
        from .seller import Seller
        return Seller
    if name == "MainNumber":
        from .main_number import MainNumber
        return MainNumber
    if name == "FleatMarket":
        from .fleat_market import FleatMarket
        return FleatMarket
    raise AttributeError(name)