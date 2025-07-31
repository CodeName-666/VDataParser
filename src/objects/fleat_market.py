from __future__ import annotations
from typing import List, Optional, Sequence
from src.log import CustomLogger  # type: ignore
from src.display import OutputInterfaceAbstraction  # type: ignore
from src.data import Base
from .data_class_definition import SellerDataClass, MainNumberDataClass
from .seller import Seller
from .main_number import MainNumber



class FleatMarket(Base):  # noqa: D101 – Docstring below
    """Container object managing :class:`Seller` and :class:`MainNumber` sets."""

    # ------------------------------------------------------------------
    # Construction helpers
    # ------------------------------------------------------------------
    def __init__(self, *,logger: Optional[CustomLogger] = None, output_interface: Optional[OutputInterfaceAbstraction] = None,):
        
        Base.__init__(logger, output_interface)

        self._sellers: List[Seller] = []
        self._main_numbers: List[MainNumber] = []

        self._log("info", "FleatMarket initialised.")
   
    def load_sellers(self, data: Sequence[SellerDataClass]) -> None:  # noqa: D401
        """Replace internal seller list with *data*."""
        self._log("debug", f"Loading {len(data)} seller entries …")
        try:
            self._sellers = [ Seller(s) for s in data ]

            self._log("info", f"{len(self._sellers)} sellers loaded.")
        except Exception as err:  # pragma: no cover – defensive
            self._log("error", "Failed to load sellers", exc=err)
            self._echo("USER_ERROR:", "Fehler beim Laden der Verkäuferdaten – siehe Log.")

    def load_main_numbers(self, data: Sequence[MainNumberDataClass]) -> None:  # noqa: D401
        """Replace internal main‑number list with *data*."""
        self._log("debug", f"Loading {len(data)} main‑number entries …")
        try:
            self._main_numbers = [ MainNumber(m) for m in data]
            self._log("info", f"{len(self._main_numbers)} main numbers loaded.")
        except Exception as err:  # pragma: no cover
            self._log("error", "Failed to load main numbers", exc=err)
            self._echo("USER_ERROR:", "Fehler beim Laden der Hauptnummern – siehe Log.")

    def sellers(self) ->  List[Seller]:
        """Immutable view of loaded sellers."""
        return self._sellers

    def main_numbers(self) -> List[MainNumber]:
        """Immutable view of loaded main numbers."""
        return self._main_numbers

    # Convenience helpers -------------------------------------------------
    def seller_count(self) -> int:  # noqa: D401
        return len(self._sellers)

    def main_number_count(self) -> int:  # noqa: D401
        return len(self._main_numbers)

    def seller_at(self, index: int) -> Optional[Seller]:  # noqa: D401
        """Return seller *index* or ``None`` if out of range."""
        try:
            return self._sellers[index]
        except IndexError:
            self._log("warning",f"Seller index {index} out of range (max {len(self._sellers) - 1}).")
            return None