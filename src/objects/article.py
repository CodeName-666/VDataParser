from __future__ import annotations


from typing import Optional
import dataclasses
from data import Base
from log import CustomLogger  # type: ignore
from display import OutputInterfaceAbstraction  # type: ignore
from data import ArticleDataClass

__all__ = ["Article"]


class Article(ArticleDataClass, Base):  # noqa: D101 – Detailed docs above
    # ------------------------------------------------------------------
    # Construction helpers
    # ------------------------------------------------------------------
    def __init__(self, info: Optional[ArticleDataClass] = None,*,
        logger: Optional[CustomLogger] = None,
        output_interface: Optional[OutputInterfaceAbstraction] = None,):
        
        ArticleDataClass.__init__(self)  # inherit all dataclass defaults
        Base.__init__(logger, output_interface)  # inherit all base defaults
       

        if info is not None:
            self.set_article_info(info)

    # ------------------------------------------------------------------
    # Data loading
    # ------------------------------------------------------------------
    def set_article_info(self, info: ArticleDataClass) -> None:  # noqa: D401
        if not isinstance(info, ArticleDataClass):
            self._log("warning", f"Wrong type for set_article_info: {type(info).__name__}")
            self._echo("USER_WARNING:", "Ungültige Artikeldaten – ignoriert.")
            return

        for fld in dataclasses.fields(info):
            setattr(self, fld.name, getattr(info, fld.name))
        #self._log("debug", f"Article {self.number() or '?'} loaded.")
        

    def number(self) -> Optional[str]:  # noqa: D401
        return getattr(self, "artikelnummer", None)

  
    def price(self) -> Optional[str]:  # noqa: D401
        return getattr(self, "preis", None)

  
    def description(self) -> Optional[str]:  # noqa: D401
        return getattr(self, "beschreibung", None)

    # ------------------------------------------------------------------
    # Validation helpers
    # ------------------------------------------------------------------
    def number_valid(self) -> bool:  # noqa: D401
        return bool(self.number() and str(self.number()).strip())

    def price_valid(self) -> bool:  # noqa: D401
        p = self.price()
        return bool(p and str(p).strip() and str(p) != "None")

    def description_valid(self) -> bool:  # noqa: D401
        d = self.description()
        return bool(d and str(d).strip())

    def is_valid(self) -> bool:  # noqa: D401
        ok = self.number_valid() and self.price_valid() and self.description_valid()
        if not ok:
            problems: list[str] = []
            if not self.number_valid():
                problems.append("Nummer")
            if not self.price_valid():
                problems.append("Preis")
            if not self.description_valid():
                problems.append("Beschreibung")
            self._log("debug", f"Artikel {self.number() or '?'} ungültig: {', '.join(problems)}")
            #self._echo("NOTICE:", f"Artikel {self.number() or '?'} ist ungültig ({', '.join(problems)}).")
        return ok

    # ------------------------------------------------------------------
    # Representation helpers
    # ------------------------------------------------------------------
    #def __repr__(self) -> str:  # noqa: D401
    #    return f"<Article {self.number or '?'} valid={self.is_valid()}>"
