from __future__ import annotations

"""Helpers to manipulate ``pdf_display_config.json`` using dataclasses."""

import copy
import os
from PySide6.QtCore import QObject, Signal
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from objects import CoordinatesConfig  # Typ für Koordinaten
        
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
        "boxPairs": [],
        "singleBoxes": [],
    }

    # ------------------------------------------------------------------
    # Konstruktor
    # ------------------------------------------------------------------
    def __init__(self, json_path_or_data: Optional[Union[str, Dict]] = None,logger=None) -> None:
        """Initialise and optionally load from ``json_path_or_data``."""

        QObject.__init__(self)
        JsonHandler.__init__(self,json_path_or_data, logger)
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

    def get_full_pdf_path(self) -> str:
        """Return the absolute PDF path composed of directory and file name."""
        path = self.get_pdf_path()
        return self.ensure_trailing_sep(path) + self.get_pdf_name()

    @staticmethod
    def ensure_trailing_sep(path: str) -> str:  # noqa: D401
        """Ensure *path* ends with the host‑OS separator (``os.sep``).

        * If the string is empty → returned unchanged.
        * If it already ends with *any* separator, the trailing component is
          normalised to ``os.sep`` so that callers always get a consistent
          result, independent of the separator style they passed in.

        Examples
        --------
        >>> ProjectManager.ensure_trailing_sep("/var/data")
        '/var/data/'  # on POSIX
        >>> ProjectManager.ensure_trailing_sep(r"C:\\logs")
        'C:\\logs\\'  # on Windows
        """
        if not path:
            return path

        # already ends with a separator – replace if necessary
        if path.endswith(("/", "\\")):
            if path.endswith(os.sep):
                return path
            return path[:-1] + os.sep  # swap the last char

        # append the host‑separator
        return path + os.sep

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
        """Convert JSON box information for ``box_id`` into ``CoordinatesConfig``."""

        # Verarbeitung der PairBox mit der übergebenen box_id
        pairboxes = self.get_box_pairs()
        pairbox = next((box for box in pairboxes if box.get("id") == box_id), {})
        first_point = pairbox.get("first", {})
        second_point = pairbox.get("second", {})
        x1 = float(first_point.get("x", 0.0))
        y1 = float(first_point.get("y", 0.0))
        x2 = float(second_point.get("x", 0.0))
        y2 = float(second_point.get("y", 0.0))
        
        # Verarbeitung der SingleBox mit der übergebenen box_id
        singleboxes = self.get_single_boxes()
        singlebox = next((box for box in singleboxes if box.get("id") == box_id), {})
        x3 = float(singlebox.get("x", 0.0))
        y3 = float(singlebox.get("y", 0.0))
        
        # Rückgabe des konfigurierten CoordinatesConfig-Objekts
        return CoordinatesConfig(
            x1=x1,
            y1=y1,
            x2=x2,
            y2=y2,
            x3=x3,
            y3=y3,
            font_size=12
        )           
        
    def is_empty(self):
        box_pairs_empty   = not self.get_box_pairs()      # True, wenn key fehlt oder Liste leer ist
        single_boxes_empty = not self.get_single_boxes()
        path_empty = not self.get_full_pdf_path()

        if box_pairs_empty and single_boxes_empty and path_empty:
            return True
        else:
            return False 
    

    