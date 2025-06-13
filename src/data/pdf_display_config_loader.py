from __future__ import annotations

"""PdfDisplayConfigHandler – Refactor

Diese Version verwendet **ausschließlich** die von ``JsonHandler`` bereit‑
­gestellten Hilfsfunktionen

* ``get_key_value(key_path: list[str])``
* ``set_key_value(key_path: list[str], value)``

für **sämtliche** Lese‑ und Schreibzugriffe – keinerlei direkte
Dictionary‑Manipulation mehr.
"""

from __future__ import annotations

import copy
from PySide6.QtCore import QObject
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
        
from json_handler import JsonHandler  # Basisklasse mit get_key_value / set_key_value

__all__ = ["Box", "BoxPair", "PdfDisplayConfigLoader"]


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
class PdfDisplayConfigLoader(QObject, JsonHandler):
    """Komfortabler Zugriff auf *pdf_display_config.json* via JsonHandler‑API."""

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
        
        QObject.__init__(self)
        JsonHandler().__init__(self,json_path_or_data, logger)
        # Bei leerem Handler Grundgerüst erzeugen
        if self.json_data is None:
            self.json_data = self._clone_template()

    # ------------------------------------------------------------------
    # Metadaten (pdf_path / pdf_name)
    # ------------------------------------------------------------------
    @property
    def pdf_path(self) -> str:
        return str(self.get_key_value(["pdf_path"]) or "")

    @pdf_path.setter
    def pdf_path(self, value: str) -> None:
        self.set_key_value(["pdf_path"], str(value))
        if value and not self.get_key_value(["pdf_name"]):
            self.set_key_value(["pdf_name"], Path(value).name)

    @property
    def pdf_name(self) -> str:
        return str(self.get_key_value(["pdf_name"]) or "")

    @pdf_name.setter
    def pdf_name(self, value: str) -> None:
        self.set_key_value(["pdf_name"], str(value))

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
