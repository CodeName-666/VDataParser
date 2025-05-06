from __future__ import annotations

"""Refactored :class:`StatisticDataGenerator`.

This version mirrors the coding style of the already‑refactored *Article*,
*MainNumber* and *FleatMarket* classes:

* **Tight cohesion** – one public method (``generate``) orchestrates the job.
* **Graceful degradation** – optional dependencies stay optional.
* **Clear user feedback** through the shared ``_output_and_log`` helper from
  the ``DataGenerator`` base class.
"""

from pathlib import Path
from typing import List, Optional, Sequence, Protocol

try:
    from log import CustomLogger  # type: ignore
except ImportError:  # pragma: no cover
    CustomLogger = None  # type: ignore

try:
    from src.display import ProgressTrackerAbstraction, OutputInterfaceAbstraction  # type: ignore
except ImportError:  # pragma: no cover
    ProgressTrackerAbstraction = OutputInterfaceAbstraction = None  # type: ignore

# ---------------------------------------------------------------------------
# FleatMarket interface (duck‑typed) – *real* class is injected at runtime
# ---------------------------------------------------------------------------
class _HasMainNumbers(Protocol):
    """Minimal subset of the *FleatMarket* API required here."""

    def get_main_number_list(self) -> Sequence[object]:  # noqa: D401
        ...


from .data_generator import DataGenerator

__all__ = ["StatisticDataGenerator"]


class StatisticDataGenerator(DataGenerator):  # noqa: D101 – Docstring above
    FILE_SUFFIX = "dat"

    # ------------------------------------------------------------------
    # Construction helpers
    # ------------------------------------------------------------------
    def __init__(
        self,
        fleat_market_data: _HasMainNumbers,
        *,
        path: str | Path = "",
        file_name: str = "versand",
        logger: Optional[CustomLogger] = None,
        output_interface: Optional[OutputInterfaceAbstraction] = None,
    ) -> None:
        super().__init__(path, file_name, logger, output_interface)
        self._fm = fleat_market_data

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    @staticmethod
    def _entry_for(number: int) -> str:  # noqa: D401
        """Return single line for *number* in CSV style."""
        return f"{number},\"-\"\n"

    # ------------------------------------------------------------------
    # Main worker
    # ------------------------------------------------------------------
    def generate(self, tracker: Optional[ProgressTrackerAbstraction] = None) -> None:  # noqa: D401
        """Collect valid *MainNumbers* and persist them to ``<file_name>.dat``."""
        self._output_and_log(
            "INFO",
            "Starte Generierung von Statistik‑Daten …"
        )

        try:
            main_numbers = self._fm.get_main_number_list()
        except Exception as err:  # pragma: no cover – defensive
            self._output_and_log("ERROR", f"Konnte Hauptnummern nicht laden: {err}")
            if tracker:
                tracker.set_error(err)  # type: ignore[attr-defined]
                tracker.increment()     # type: ignore[attr-defined]
            return

        valid_lines: list[str] = []
        skipped = 0

        for obj in main_numbers:
            if not all(hasattr(obj, m) for m in ("is_valid", "get_main_number")):
                skipped += 1
                continue

            try:
                if obj.is_valid():
                    num = int(obj.get_main_number())
                    valid_lines.append(self._entry_for(num))
                else:
                    skipped += 1
            except Exception:  # pragma: no cover – lenient: treat as invalid
                skipped += 1

        # Persist ----------------------------------------------------------------
        self._write(valid_lines)
        self._output_and_log(
            "INFO",
            f"Statistik erstellt: {len(valid_lines)} Einträge, {skipped} übersprungen."
        )

        if tracker:
            tracker.increment()  # type: ignore[attr-defined]
            self._log("debug", "Tracker inkrementiert.")

    # ------------------------------------------------------------------
    # I/O – delegates to DataGenerator for logging & error handling
    # ------------------------------------------------------------------
    def _write(self, lines: List[str]) -> None:  # noqa: D401
        if not lines:
            self._output_and_log("INFO", "Keine gültigen Daten zum Schreiben.")
            return

        path = self.get_full_path()
        path.parent.mkdir(parents=True, exist_ok=True)

        try:
            path.write_text("".join(lines), encoding="utf-8")
        except IOError as err:
            self._output_and_log(
                "ERROR", f"Fehler beim Schreiben nach {path}: {err}"
            )
        else:
            self._output_and_log(
                "INFO", f"Datei erfolgreich geschrieben: {path.relative_to(Path.cwd())}"
            )
