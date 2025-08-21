"""Domain objects and dataclass definitions.

Exports dataclasses and provides lazy accessors for richer wrapper types
(`Article`, `Seller`, `MainNumber`, `FleatMarket`).
"""

from .data_class_definition import *  # re-export generated dataclasses


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
