"""Domain model: Seller.

Thin convenience wrapper around the `SellerDataClass` to simplify
initialisation and future extensions.
"""

from .data_class_definition import SellerDataClass


class Seller(SellerDataClass): 

    def __init__(self, seller_info: SellerDataClass = None):
        if seller_info:
            self.set_seller_info(seller_info)

    def set_seller_info(self, seller_info: SellerDataClass):
        SellerDataClass.__init__(self, **seller_info.__dict__)
        
    
        

    
