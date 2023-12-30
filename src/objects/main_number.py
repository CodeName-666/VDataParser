from data import MainNumberDataClass
from objects import Article
from typing import List
from log import logger


class MainNumber(MainNumberDataClass):

    def __init__(self, main_number_info: MainNumberDataClass = None) -> None:
        if main_number_info:
            self.set_main_number_info(main_number_info)

    def set_main_number_info(self, main_number_info: MainNumberDataClass):
        MainNumberDataClass.__init__(self,**main_number_info.__dict__)
        self.__article_list: List[Article] = [Article(article) for article in main_number_info.data] 

    def get_main_number(self) -> int : 
        return int(self.name.replace("stnr",""))
    
    def is_valid(self):
        if self.get_article_quantity() > 0 and self.get_article_total() > 0:
            logger.debug("Article List is valid", on_verbose= True)
            return True
        else:
            logger.warning("Article List is invalid", on_verbose= True)
            return False


    def get_article_quantity(self) -> int:
        valid_cnt = 0
        invalid_cnt = 0
        logger.log_one_line("DEBUG",True)
        logger.debug("Calculate Article Quantitiy: \n")
        

        for index, article in enumerate(self.__article_list):
            logger.debug(f"    ---> Article {index}: {article.description()} = ",on_verbose=True)
            logger.skip_logging("DEBUG",True)
            is_valid = article.is_valid()
            logger.skip_logging("DEBUG",False)
            if is_valid:
                valid_cnt += 1
                logger.debug("valid \n", on_verbose=True)
            else:
                invalid_cnt += 1
                logger.debug("invalid \n", on_verbose=True)
                
        logger.debug(f"       ==> Valid article: {valid_cnt}, Invalid: {invalid_cnt} \n")
        logger.log_one_line("DEBUG",False)
        return valid_cnt
    
    def get_article_total(self):
        total_count = 0.0
        for article in self.__article_list:
            if article.is_valid():
                total_count += float(article.preis)

        return round(total_count,2)
    
    @property
    def article_list(self):
        return self.__article_list