
from data import ArticleDataClass
from log import logger

class Article(ArticleDataClass): 

    def __init__(self, article_info : ArticleDataClass = None):
        if article_info:
            self.set_article_info(article_info)
    
    def set_article_info(self, article_info : ArticleDataClass):
        ArticleDataClass.__init__(self,**article_info.__dict__)

    def is_valid(self):
        if self.descritpion_valid() and self.price_valid():
            logger.debug(f"Article: {self.description()} is valid",True)
            return True
        else:
            #logger.warning(f"Article: {self.description()} is not valid: ")
            return False
        
    def number(self):
        return self.artikelnummer
    
    
    def price(self):
        return self.preis
    
    def description(self):
        return self.beschreibung
    
    def number_valid(self):
        valid = (self.number() != "")
        logger.debug(f"Number Valid: {valid}", True)
        return valid
    
    def price_valid(self):
        is_none = (self.price() == None)
        is_none_str = (self.price() == "None")
        is_empty = (self.price() == "") 
        valid = (not is_empty and not is_none and not is_none_str)

        logger.log_one_line("DEBUG",True)
        logger.debug(f"Price is None: {is_none} | ",True)
        logger.debug(f"Price empty: {is_empty}\n", True)
        logger.debug(f"       ===>Price valid {valid}\n",True)
        logger.log_one_line("DEBUG",False)
        return valid 
    
    def descritpion_valid(self):
        valid = (self.description() != "")
        logger.debug(f"Description Valid: {valid}", True)
        return valid
    

    
    