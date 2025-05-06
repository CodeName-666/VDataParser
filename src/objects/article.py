from __future__ import annotations

"""Refactored :class:`Article` implementation.

Highlights
----------
* **Lean, single‑responsibility** design: validation & simple logging only.
* Maintains legacy methods (``number()``, ``price()``, ``description()``) so
  external callers stay unaffected.
* Centralised helpers ``_log`` / ``_echo`` prevent repetitive code.
* Uses *properties* instead of ad‑hoc getter functions internally.
"""

from typing import Optional
import dataclasses

try:
    # Optional logger – available in production environment.
    from log import CustomLogger  # type: ignore
except ImportError:  # pragma: no cover – doctest / CI
    CustomLogger = None  # type: ignore

try:
    # Optional UI sink for human‑readable messages.
    from src.display import OutputInterfaceAbstraction  # type: ignore
except ImportError:  # pragma: no cover
    OutputInterfaceAbstraction = None  # type: ignore

from data import ArticleDataClass

__all__ = ["Article"]


class Article(ArticleDataClass):  # noqa: D101 – Detailed docs above
    # ------------------------------------------------------------------
    # Construction helpers
    # ------------------------------------------------------------------
    def __init__(
        self,
        info: Optional[ArticleDataClass] = None,
        *,
        logger: Optional[CustomLogger] = None,
        output_interface: Optional[OutputInterfaceAbstraction] = None,
    ) -> None:
        super().__init__()  # inherit all dataclass defaults
        self._logger = logger
        self._output = output_interface

        if info is not None:
            self.set_article_info(info)

    # ------------------------------------------------------------------
    # Internal utilities
    # ------------------------------------------------------------------
    def _log(self, level: str, msg: str) -> None:
        if not self._logger:
            return
        fn = getattr(self._logger, level, None)
        if callable(fn):
            fn(msg)
        else:
            self._logger.info(msg)

    def _echo(self, prefix: str, msg: str) -> None:
        if self._output:
            self._output.write_message(f"{prefix} {msg}")

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
        self._log("debug", f"Article {self.number or '?'} loaded.")

    # ------------------------------------------------------------------
    # Properties & legacy accessors
    # ------------------------------------------------------------------
    @property
    def number(self) -> Optional[str]:  # noqa: D401
        return getattr(self, "artikelnummer", None)

    @property
    def price(self) -> Optional[str]:  # noqa: D401
        return getattr(self, "preis", None)

    @property
    def description(self) -> Optional[str]:  # noqa: D401
        return getattr(self, "beschreibung", None)

    # Legacy aliases – keep public API stable --------------------------------
    def number(self):  # type: ignore[override]
        return self.number  # pragma: no cover – alias

    def price(self):  # type: ignore[override]
        return self.price   # pragma: no cover

    def description(self):  # type: ignore[override]
        return self.description  # pragma: no cover

    # ------------------------------------------------------------------
    # Validation helpers
    # ------------------------------------------------------------------
    def number_valid(self) -> bool:  # noqa: D401
        return bool(self.number and str(self.number).strip())

    def price_valid(self) -> bool:  # noqa: D401
        p = self.price
        return bool(p and str(p).strip() and str(p) != "None")

    def description_valid(self) -> bool:  # noqa: D401
        d = self.description
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
            self._log("debug", f"Artikel {self.number or '?'} ungültig: {', '.join(problems)}")
            self._echo("NOTICE:", f"Artikel {self.number or '?'} ist ungültig ({', '.join(problems)}).")
        return ok

    # ------------------------------------------------------------------
    # Representation helpers
    # ------------------------------------------------------------------
    def __repr__(self) -> str:  # noqa: D401
        return f"<Article {self.number or '?'} valid={self.is_valid()}>"
