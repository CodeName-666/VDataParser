"""Expose generator classes without eager imports."""

__all__ = [
    "DataGenerator",
    "PriceListGenerator",
    "SellerDataGenerator",
    "FileGenerator",
]

from importlib import import_module

_MODULE_MAP = {
    "DataGenerator": "data_generator",
    "PriceListGenerator": "price_list_generator",
    "SellerDataGenerator": "seller_data_generator",
    "FileGenerator": "file_generator",
}


def __getattr__(name: str):
    module_name = _MODULE_MAP.get(name)
    if module_name:
        module = import_module(f".{module_name}", __name__)
        return getattr(module, name)
    raise AttributeError(name)
