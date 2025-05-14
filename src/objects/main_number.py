from __future__ import annotations

from typing import List, Optional
import dataclasses
from log import CustomLogger  # type: ignore
from display import OutputInterfaceAbstraction  # type: ignore
from data import MainNumberDataClass, ArticleDataClass
from objects import Article

__all__ = ["MainNumber"]


class MainNumber(MainNumberDataClass):
    """Business‑logic wrapper around :class:`MainNumberDataClass`.

    A *main number* groups multiple :class:`Article` objects.  This subclass adds
    validation logic, aggregation helpers, and optional hooks for logging and
    rich user output while keeping the original data attributes (``name``,
    ``data`` …) inherited from :class:`MainNumberDataClass`.
    """

    # ---------------------------------------------------------------------
    # Construction helpers
    # ---------------------------------------------------------------------
    def __init__(
        self,
        main_number_info: Optional[MainNumberDataClass] = None,
        *,
        logger: Optional[CustomLogger] = None,
        output_interface: Optional[OutputInterfaceAbstraction] = None,
    ) -> None:
        # 1. Initialise inherited dataclass fields with their defaults.
        super().__init__()

        # 2. Optional collaborators --------------------------------------------------
        self._logger = logger
        self._output = output_interface

        # 3. Runtime‑only state ------------------------------------------------------
        self._articles: List[Article] = []

        # 4. Load initial data (if provided) -----------------------------------------
        if main_number_info is not None:
            self.set_main_number_info(main_number_info)

    # ---------------------------------------------------------------------
    # Logging utilities (internal only)
    # ---------------------------------------------------------------------
    def _log(
        self,
        level: str,
        msg: str,
        *,
        verbose: bool = False,
        exc_info: bool | Exception | None = False,
    ) -> None:
        """Dispatch *msg* to the external logger (if configured)."""
        if not self._logger:
            return  # Logging disabled

        log_fn = getattr(self._logger, level, None)
        if callable(log_fn):
            # Most common logger signatures are ``(msg)`` or ``(msg, exc_info=…)``.
            try:
                log_fn(msg, exc_info=exc_info)  # type: ignore[arg-type]
            except TypeError:
                # Fallback: silently ignore unsupported keyword args.
                log_fn(msg)  # type: ignore[misc]
        else:
            # Unknown *level* → fallback to *info*.
            self._logger.info(msg)

    def _echo(self, prefix: str, msg: str) -> None:
        """Write *msg* to the optional *output_interface*."""
        if self._output:
            self._output.write_message(f"{prefix} {msg}")

    # ---------------------------------------------------------------------
    # Public API
    # ---------------------------------------------------------------------
    def set_main_number_info(self, info: MainNumberDataClass) -> None:  # noqa: D401
        """Load *info* and (re‑)initialise :pyattr:`_articles`."""
        if not isinstance(info, MainNumberDataClass):
            self._log("error", f"Expected MainNumberDataClass, got {type(info).__name__}")
            self._echo("USER_ERROR:", "Ungültige Datenstruktur übergeben.")
            return

        # Copy dataclass fields efficiently (works even if *info* is a plain obj).
        for fld in dataclasses.fields(info):
            setattr(self, fld.name, getattr(info, fld.name))

        # Convert raw *ArticleDataClass* entries into rich *Article* objects.
        raw_articles = getattr(info, "data", []) or []
        self._articles = [
            Article(a, logger=self._logger, output_interface=self._output)
            for a in raw_articles
        ]
        self._log("debug", f"Loaded {len(self._articles)} article(s) for '{self.name}'.")

    # ------------------------------------------------------------------
    # Convenience helpers / computed attributes
    # ------------------------------------------------------------------
    def number(self) -> Optional[int]:
        """Return the numeric identifier extracted from ``self.name`` (``stnr123`` → ``123``)."""
        if isinstance(self.name, str) and self.name.lower().startswith("stnr"):
            try:
                return int(self.name[4:])
            except ValueError:
                pass  # fallthrough → None
        return None

    # ------------------------------------------------------------------
    # Aggregations
    # ------------------------------------------------------------------
    def valid_articles(self) -> List[Article]:
        """List of *valid* :class:`Article` instances."""
        return [a for a in self._articles if a.is_valid()]

    def article_quantity(self) -> int:
        """Number of valid articles."""
        qty = len(self.valid_articles())
        self._log("debug", f"'{self.name}': {qty} gültige Artikel gezählt (gesamt {len(self._articles)}).")
        return qty

    def article_total(self) -> float:
        """Total price of valid articles (rounded to 2 decimals)."""
        total = round(sum(float(a.price()) for a in self.valid_articles()), 2)
        self._log("debug", f"'{self.name}': Gesamtwert der Artikel = {total:.2f} €.")
        return total

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------
    def is_valid(self) -> bool:  # noqa: D401
        """A *main number* is considered *valid* if it has at least one valid article."""
        flag = bool(self.article_quantity())
        if flag:
            self._log("info", f"MainNumber '{self.name}' ist *gültig*.")
        else:
            self._log("warning", f"MainNumber '{self.name}' ist *ungültig* (keine gültigen Artikel).")
            self._echo("NOTICE:", "Keine gültigen Artikel gefunden – bitte prüfen.")
        return flag

    # ------------------------------------------------------------------
    # Human‑readable helpers
    # ------------------------------------------------------------------
    def __repr__(self) -> str:  # noqa: D401
        return (
            f"<MainNumber name='{self.name}' #articles={len(self._articles)} "
            f"valid={self.article_quantity()} total={self.article_total():.2f}>"
        )

