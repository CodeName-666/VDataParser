"""Helpers for font lookup and registration."""

from __future__ import annotations

import os
from pathlib import Path
import platform
import subprocess

try:
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
except Exception:  # pragma: no cover - optional dependency
    pdfmetrics = None  # type: ignore
    TTFont = None  # type: ignore

try:
    from fontTools.ttLib import TTFont as TTFontParser
except Exception:  # pragma: no cover - optional dependency
    TTFontParser = None  # type: ignore

__all__ = ["register_font"]


def register_font(name: str) -> None:
    """Register ``name`` with ReportLab if available."""
    if pdfmetrics is None or TTFont is None:
        return
    if name in pdfmetrics.getRegisteredFontNames():
        return

    path = ""
    if platform.system() != "Windows":
        try:
            path = subprocess.check_output(
                ["fc-match", "-f", "%{file}", name],
                text=True,
                stderr=subprocess.DEVNULL,
            ).strip()
        except Exception:
            path = ""

    if not path and platform.system() == "Windows":
        font_dir = Path(os.environ.get("WINDIR", "C:\\Windows")) / "Fonts"
        if font_dir.is_dir():
            sanitized = name.lower().replace(" ", "")
            for ext in (".ttf", ".ttc", ".otf"):
                for file in font_dir.glob(f"*{ext}"):
                    stem = file.stem.lower().replace(" ", "")
                    title_match = False
                    if TTFontParser is not None:
                        try:
                            f = TTFontParser(str(file))
                            for rec in f["name"].names:
                                if rec.nameID in (1, 4):
                                    val = rec.toStr().lower().replace(" ", "")
                                    if sanitized in val:
                                        title_match = True
                                        break
                            f.close()
                        except Exception:
                            pass
                    if sanitized in stem or title_match:
                        path = str(file)
                        break
                if path:
                    break

    if path:
        try:
            pdfmetrics.registerFont(TTFont(name, path))
        except Exception:
            pass
