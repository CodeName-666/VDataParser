from __future__ import annotations

from pathlib import Path
from typing import List, Optional, Sequence, Protocol
from log import CustomLogger  # type: ignore
from display import (
    ProgressTrackerAbstraction as _TrackerBase,  # type: ignore
    OutputInterfaceAbstraction,                  # type: ignore
)

from .data_generator import DataGenerator
from objects import FleatMarket  # type: ignore
from objects import MainNumber  # type: ignore



class PriceListGenerator(DataGenerator):  # noqa: D101 – detailed docs above
    FILE_SUFFIX = "dat"

    # ------------------------------------------------------------------
    def __init__(self, fleat_market_data: FleatMarket, *,path: str | Path = "", file_name: str = "preisliste",
                 logger: Optional[CustomLogger] = None, output_interface: Optional[OutputInterfaceAbstraction] = None) -> None:

        super().__init__(path, file_name, logger, output_interface)
        self._fleat_market = fleat_market_data

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    @staticmethod
    def _format_entry(main_number: str, article_number: str, price: str) -> str:  # noqa: D401
        try:
            num = int(article_number)
            article_format = f"{num:02d}" if 0 <= num < 100 else "XX"
        except ValueError:
            article_format = "XX"
        price_fmt = price.strip().replace(",", ".")
        return f"{main_number.strip()}{article_format},{price_fmt}\n"

    def _collect_lines(self) -> List[str]:  # noqa: D401
        lines: list[str] = []
        skipped = 0
        for main_number in self._fleat_market.main_numbers():
            if not (getattr(main_number, "is_valid", lambda: False)() and hasattr(main_number, "valid_articles")):
                skipped += 1
                continue
            main_number_int = str(main_number.number())
            #for art in getattr(mn, "valid_articles", []):
            for article in main_number.valid_articles():
                if not getattr(article, "is_valid", lambda: False)():
                    skipped += 1
                    continue
                try:
                    line = self._format_entry(main_number_int, str(article.number()), str(article.price()))
                    lines.append(line)
                except Exception:  # pragma: no cover – lenient parsing
                    skipped += 1
        self._log("debug", f"PriceList lines collected: {len(lines)}, skipped: {skipped}.")
        return lines

    def _write(self, lines: Sequence[str]) -> bool:  # noqa: D401
        if not lines:
            self._output_and_log("INFO", "Keine gültigen Einträge – Datei wird nicht erstellt.")
            return False
        path = self.get_full_path()
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("".join(lines), encoding="utf-8")
            self._output_and_log("INFO", f"Preisliste geschrieben: {path.relative_to(Path.cwd())}")
            return True
        except Exception as err:  # pragma: no cover
            self._output_and_log("ERROR", f"Fehler beim Schreiben der Preisliste: {err}")
            return False

    # ------------------------------------------------------------------
    # Public entry point
    # ------------------------------------------------------------------
    def generate(self, overall_tracker: Optional[_TrackerBase] = None) -> None:  # noqa: D401
        self._output_and_log("INFO", "Starte Preislisten‑Generierung …")
        lines = self._collect_lines()
        self._write(lines)
        if overall_tracker:
            overall_tracker.increment()  # type: ignore[attr-defined]
