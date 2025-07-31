from __future__ import annotations

"""Helpers to manipulate ``pdf_display_config.json`` using dataclasses."""

import copy
import os
from PySide6.QtCore import QObject, Signal
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from src.objects import CoordinatesConfig  # Typ für Koordinaten

from src.util.path_utils import ensure_trailing_sep

from .json_handler import JsonHandler  # Basisklasse mit get_key_value / set_key_value

__all__ = ["Box", "BoxPair", "PdfDisplayConfig"]


# -----------------------------------------------------------------------------
# Typsichere Datenklassen (optional)
# -----------------------------------------------------------------------------
@dataclass
class Box:
    label: str
    x: float
    y: float
    width: float
    height: float
    id: Optional[int] | None = None  # nur für SingleBox relevant

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Box":
        return cls(**data)  # type: ignore[arg-type]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class BoxPair:
    id: int
    box1: Box
    box2: Box

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BoxPair":
        return cls(
            id=data["id"],
            box1=Box.from_dict(data["box1"]),
            box2=Box.from_dict(data["box2"]),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {"id": self.id, "box1": self.box1.to_dict(), "box2": self.box2.to_dict()}


# -----------------------------------------------------------------------------
# Spezial‑Handler
# -----------------------------------------------------------------------------
class PdfDisplayConfig(QObject, JsonHandler):
    """Convenient access wrapper around ``pdf_display_config.json``."""

    data_loaded = Signal(object)  # Signal to notify when data is loaded

    _TEMPLATE: Dict[str, Any] = {
        "pdf_path": "",
        "pdf_name": "",
        "output_path": "",
        "output_name": "",
        "dpi": 150,
        "placeholder_font_family": "Helvetica",
        "placeholder_font_size": 12,
        "pickup_date": "",
        "pickup_time": "",
        "boxPairs": [],
        "singleBoxes": [],
    }

    # ------------------------------------------------------------------
    # Konstruktor
    # ------------------------------------------------------------------
    def __init__(
        self, json_path_or_data: Optional[Union[str, Dict]] = None, logger=None
    ) -> None:
        """Initialise and optionally load from ``json_path_or_data``."""

        QObject.__init__(self)
        JsonHandler.__init__(self, json_path_or_data, logger)
        # Create default template when constructed empty
        if self.json_data is None:
            self.json_data = self._clone_template()

    # ------------------------------------------------------------------
    # Metadaten (pdf_path / pdf_name)
    # ------------------------------------------------------------------
    def get_pdf_path(self) -> str:
        """Return the configured PDF directory path."""
        return str(self.get_key_value(["pdf_path"]) or "")

    def set_full_pdf_path(self, value: str) -> None:
        """Set the PDF directory path and update ``pdf_name`` if empty."""
        file = Path(value)
        self.set_key_value(["pdf_path"], str(file.parent))
        if value and not self.get_key_value(["pdf_name"]):
            self.set_key_value(["pdf_name"], file.name)

    def set_pdf_path(self, value: str) -> None:
        self.set_key_value(["pdf_path"], str(value))

    def get_pdf_name(self) -> str:
        """Return the configured PDF file name."""
        return str(self.get_key_value(["pdf_name"]) or "")

    def set_pdf_name(self, value: str) -> None:
        """Set the PDF file name."""
        self.set_key_value(["pdf_name"], str(value))

    # ------------------------------------------------------------------
    # Output path / output name
    # ------------------------------------------------------------------
    def get_output_path(self) -> str:
        """Return the configured output directory path."""
        return str(self.get_key_value(["output_path"]) or "")

    def set_output_path(self, value: str) -> None:
        self.set_key_value(["output_path"], str(value))

    def get_output_name(self) -> str:
        """Return the configured output file name."""
        return str(self.get_key_value(["output_name"]) or "")

    def set_output_name(self, value: str) -> None:
        self.set_key_value(["output_name"], str(value))

    def get_full_output_path(self) -> str:
        """Return the absolute output path composed of directory and file name."""
        path = self.get_output_path()
        return ensure_trailing_sep(path) + self.get_output_name()

    def set_full_output_path(self, value: str) -> None:
        file = Path(value)
        self.set_key_value(["output_path"], str(file.parent))
        self.set_key_value(["output_name"], file.name)

    # ------------------------------------------------------------------
    # DPI handling
    # ------------------------------------------------------------------
    def get_dpi(self) -> int:
        """Return the DPI used when capturing coordinates."""
        return int(self.get_key_value(["dpi"]) or 150)

    def set_dpi(self, value: int) -> None:
        self.set_key_value(["dpi"], int(value))

    # ------------------------------------------------------------------
    # Placeholder font handling
    # ------------------------------------------------------------------
    def get_placeholder_font_family(self) -> str:
        """Return the font family used for placeholders and PDF text."""
        return str(self.get_key_value(["placeholder_font_family"]) or "Helvetica")

    def set_placeholder_font_family(self, value: str) -> None:
        self.set_key_value(["placeholder_font_family"], str(value))

    def get_placeholder_font_size(self) -> int:
        """Return the font size for placeholders and PDF text."""
        return int(self.get_key_value(["placeholder_font_size"]) or 12)

    def set_placeholder_font_size(self, value: int) -> None:
        self.set_key_value(["placeholder_font_size"], int(value))

    # ------------------------------------------------------------------
    # Pickup date handling
    # ------------------------------------------------------------------
    def get_pickup_date(self) -> str:
        """Return the configured pickup date string."""
        return str(self.get_key_value(["pickup_date"]) or "")

    def set_pickup_date(self, value: str) -> None:
        self.set_key_value(["pickup_date"], str(value))

    def get_pickup_time(self) -> str:
        """Return the configured pickup time string."""
        return str(self.get_key_value(["pickup_time"]) or "")

    def set_pickup_time(self, value: str) -> None:
        self.set_key_value(["pickup_time"], str(value))

    def get_full_pdf_path(self) -> str:
        """Return the absolute PDF path composed of directory and file name."""
        path = self.get_pdf_path()
        return ensure_trailing_sep(path) + self.get_pdf_name()


    # ------------------------------------------------------------------
    # BoxPairs ---------------------------------------------------------
    # ------------------------------------------------------------------
    def get_box_pairs(self) -> List[BoxPair]:
        raw = self.get_key_value(["boxPairs"]) or []
        return [BoxPair.from_dict(p) for p in raw]

    def add_box_pair(self, pair: BoxPair) -> None:
        pairs: List[Dict[str, Any]] = self.get_key_value(["boxPairs"]) or []
        pairs.append(pair.to_dict())
        self.set_key_value(["boxPairs"], pairs)

    def remove_box_pair(self, pair_id: int) -> bool:
        pairs: List[Dict[str, Any]] = self.get_key_value(["boxPairs"]) or []
        new_pairs = [p for p in pairs if p.get("id") != pair_id]
        if len(new_pairs) == len(pairs):
            return False
        self.set_key_value(["boxPairs"], new_pairs)
        return True

    # ------------------------------------------------------------------
    # SingleBoxes ------------------------------------------------------
    # ------------------------------------------------------------------
    def get_single_boxes(self) -> List[Box]:
        raw = self.get_key_value(["singleBoxes"]) or []
        return [Box.from_dict(b) for b in raw]

    def add_single_box(self, box: Box) -> None:
        singles: List[Dict[str, Any]] = self.get_key_value(["singleBoxes"]) or []
        singles.append(box.to_dict())
        self.set_key_value(["singleBoxes"], singles)

    def remove_single_box(self, box_id: int) -> bool:
        singles: List[Dict[str, Any]] = self.get_key_value(["singleBoxes"]) or []
        new_singles = [b for b in singles if b.get("id") != box_id]
        if len(new_singles) == len(singles):
            return False
        self.set_key_value(["singleBoxes"], new_singles)
        return True

    # ------------------------------------------------------------------
    # Export / Utilities
    # ------------------------------------------------------------------
    def to_dict(self) -> Dict[str, Any]:
        return copy.deepcopy(self.json_data)

    @classmethod
    def _clone_template(cls) -> Dict[str, Any]:
        return copy.deepcopy(cls._TEMPLATE)

    def load(self, path_or_url: str) -> bool:
        """
        Load JSON data from a file or URL and parse it into data classes.

        Args:
            path_or_url (str): Path to the JSON file or URL.
        """
        ret = super().load(path_or_url)
        if ret:
            self.data_loaded.emit(self)
        return ret

    def convert_json_to_coordinates(self, box_id: int) -> CoordinatesConfig:
        """Return ``CoordinatesConfig`` for the given ``box_id``.

        The coordinates represent the centre points of the boxes. When
        drawing text with the configured ``font_size`` of ``12`` points the
        baseline will be vertically centred within the box.  Horizontal
        centring must be performed by the caller, typically by subtracting
        half of the string width from the ``x`` values returned here.

        If either a ``BoxPair`` or ``SingleBox`` is missing for ``box_id`` the
        corresponding coordinates will be ``0``.
        """

        pairboxes = {pair.id: pair for pair in self.get_box_pairs()}
        singleboxes = {
            box.id: box for box in self.get_single_boxes() if box.id is not None
        }

        pair = pairboxes.get(box_id)
        single = singleboxes.get(box_id)

        font_size = self.get_placeholder_font_size()

        x1 = (pair.box1.x + pair.box1.width / 2) if pair else 0.0
        y1 = (pair.box1.y + pair.box1.height / 2 + font_size / 2) if pair else 0.0
        x2 = (pair.box2.x + pair.box2.width / 2) if pair else 0.0
        y2 = (pair.box2.y + pair.box2.height / 2 + font_size / 2) if pair else 0.0

        x3 = (single.x + single.width / 2) if single else 0.0
        y3 = (single.y + single.height / 2 + font_size / 2) if single else 0.0

        return CoordinatesConfig(
            x1=x1,
            y1=y1,
            x2=x2,
            y2=y2,
            x3=x3,
            y3=y3,
            font_size=font_size,
        )
    
    def convert_json_to_coordinate_list(self) -> List[CoordinatesConfig]:
        """Return list of ``CoordinatesConfig`` objects derived from the config.

        The list is ordered by the ``id`` values appearing in ``boxPairs`` or
        ``singleBoxes``.  Missing coordinate values for a pair or single box are
        returned as ``0``.
        """

        pair_ids = {pair.id for pair in self.get_box_pairs()}
        single_ids = {box.id for box in self.get_single_boxes() if box.id is not None}

        all_ids = sorted(pair_ids | single_ids)

        return [self.convert_json_to_coordinates(i) for i in all_ids]

    def is_empty(self):
        box_pairs_empty = (
            not self.get_box_pairs()
        )  # True, wenn key fehlt oder Liste leer ist
        single_boxes_empty = not self.get_single_boxes()
        path_empty = not self.get_full_pdf_path()

        if box_pairs_empty and single_boxes_empty and path_empty:
            return True
        else:
            return False
