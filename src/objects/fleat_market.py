from __future__ import annotations

"""Refactored implementation of :class:`FleatMarket`.

Key improvements
----------------
* Clear, minimal public API (``load_sellers`` / ``load_main_numbers``).
* Centralised error handling & logging helpers.
* Properties expose immutable *views* – internal lists stay encapsulated.
* Optional dependencies (logger, output interface) remain truly optional.
"""

from typing import List, Optional, Sequence

try:
    # --- Optional Logger ---------------------------------------------------
    from log import CustomLogger  # type: ignore
except ImportError:  # pragma: no cover
    CustomLogger = None  # type: ignore

try:
    # --- Optional Output Interface ----------------------------------------
    from src.display import OutputInterfaceAbstraction  # type: ignore
except ImportError:  # pragma: no cover
    OutputInterfaceAbstraction = None  # type: ignore

from data import SellerDataClass, MainNumberDataClass
from .seller import Seller
from .main_number import MainNumber

__all__ = ["FleatMarket"]


class FleatMarket:  # noqa: D101 – Docstring below
    """Container object managing :class:`Seller` and :class:`MainNumber` sets."""

    # ------------------------------------------------------------------
    # Construction helpers
    # ------------------------------------------------------------------
    def __init__(
        self,
        *,
        logger: Optional[CustomLogger] = None,
        output_interface: Optional[OutputInterfaceAbstraction] = None,
    ) -> None:
        self._logger = logger
        self._output = output_interface

        self._sellers: List[Seller] = []
        self._main_numbers: List[MainNumber] = []

        self._log("info", "FleatMarket initialised.")

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _log(self, level: str, msg: str, *, exc: Exception | None = None) -> None:
        if not self._logger:
            return

        fn = getattr(self._logger, level, None)
        if callable(fn):
            try:
                fn(msg, exc_info=exc)  # type: ignore[arg-type]
            except TypeError:
                fn(msg)  # type: ignore[misc]
        else:
            self._logger.info(msg)

    def _echo(self, prefix: str, msg: str) -> None:
        if self._output:
            self._output.write_message(f"{prefix} {msg}")

    # ------------------------------------------------------------------
    # Public API – data loading
    # ------------------------------------------------------------------
    def load_sellers(self, data: Sequence[SellerDataClass]) -> None:  # noqa: D401
        """Replace internal seller list with *data*."""
        self._log("debug", f"Loading {len(data)} seller entries …")
        try:
            self._sellers = [
                Seller(s) for s in data
            ]
            self._log("info", f"{len(self._sellers)} sellers loaded.")
        except Exception as err:  # pragma: no cover – defensive
            self._log("error", "Failed to load sellers", exc=err)
            self._echo("USER_ERROR:", "Fehler beim Laden der Verkäuferdaten – siehe Log.")

    def load_main_numbers(self, data: Sequence[MainNumberDataClass]) -> None:  # noqa: D401
        """Replace internal main‑number list with *data*."""
        self._log("debug", f"Loading {len(data)} main‑number entries …")
        try:
            self._main_numbers = [
                MainNumber(m, logger=self._logger, output_interface=self._output) for m in data
            ]
            self._log("info", f"{len(self._main_numbers)} main numbers loaded.")
        except Exception as err:  # pragma: no cover
            self._log("error", "Failed to load main numbers", exc=err)
            self._echo("USER_ERROR:", "Fehler beim Laden der Hauptnummern – siehe Log.")

    # ------------------------------------------------------------------
    # Read‑only views
    # ------------------------------------------------------------------
    @property
    def sellers(self) -> tuple[Seller, ...]:
        """Immutable view of loaded sellers."""
        return tuple(self._sellers)

    @property
    def main_numbers(self) -> tuple[MainNumber, ...]:
        """Immutable view of loaded main numbers."""
        return tuple(self._main_numbers)

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
            self._log(
                "warning",
                f"Seller index {index} out of range (max {len(self._sellers) - 1}).",
            )
            return None

    # ------------------------------------------------------------------
    # Dunder helpers
    # ------------------------------------------------------------------
    def __repr__(self) -> str:  # noqa: D401
        return (
            f"<FleatMarket sellers={self.seller_count()} "
            f"main_numbers={self.main_number_count()}>"
        )
