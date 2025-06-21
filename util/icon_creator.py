#!/usr/bin/env python3
"""
raster2svg.py  –  Bulk-Konverter Raster → SVG (mit Größenskali­erung & Graustufen)

Installation der Abhängigkeiten:
    pip install pillow svgwrite

Aufrufbeispiele
------------------------------------
# Alle Bilder in ./pics nach ./svgs, längste Kante max. 512 px
python raster2svg.py pics svgs --max-size 512

# Feste Zielgröße (Breite=200 px, Höhe=100 px) + Graustufen
python raster2svg.py pics svgs --width 200 --height 100 --grayscale
"""

import argparse
import base64
import io
import os
from pathlib import Path

from PIL import Image
import svgwrite


# ------------------------------------------------------------
def raster_to_svg(img: Image.Image,
                  out_path: Path,
                  width: int | None = None,
                  height: int | None = None,
                  max_size: int | None = None) -> None:
    """Erzeugt eine SVG-Datei mit dem (ggf. skalierten) Bild als inline-PNG."""
    # proportional skalieren, wenn max_size gesetzt ist
    if max_size:
        img.thumbnail((max_size, max_size), Image.LANCZOS)

    # feste Zielabmessungen setzen
    if width or height:
        new_w = width or img.width
        new_h = height or img.height
        img = img.resize((new_w, new_h), Image.LANCZOS)

    # Bild als PNG in-Memory codieren
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    b64_png = base64.b64encode(buf.getvalue()).decode("ascii")

    # SVG erstellen
    w, h = img.size
    dwg = svgwrite.Drawing(size=(f"{w}px", f"{h}px"))
    dwg.add(
        dwg.image(
            href=f"data:image/png;base64,{b64_png}",
            insert=(0, 0),
            size=(w, h),
        )
    )
    dwg.saveas(out_path)


# ------------------------------------------------------------
def process_folder(src: Path,
                   dst: Path,
                   grayscale: bool,
                   width: int | None,
                   height: int | None,
                   max_size: int | None) -> None:
    dst.mkdir(parents=True, exist_ok=True)
    supported = {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tiff"}
    for file in src.iterdir():
        if file.suffix.lower() not in supported or not file.is_file():
            continue
        img = Image.open(file).convert("RGBA")
        if grayscale:
            # in L konvertieren, danach wieder RGBA für Transparenz
            img = img.convert("L").convert("RGBA")
        out_name = file.stem + ".svg"
        raster_to_svg(
            img,
            dst / out_name,
            width=width,
            height=height,
            max_size=max_size,
        )
        print(f"✔  {file.name}  →  {out_name}")


# ------------------------------------------------------------
def main() -> None:
    parser = argparse.ArgumentParser(
        description="Konvertiert alle Rasterbilder in einem Ordner zu SVG (inline-PNG)."
    )
    parser.add_argument("input_dir", type=Path, help="Quellordner mit Bildern")
    parser.add_argument("output_dir", type=Path, help="Zielordner für SVGs")
    size = parser.add_mutually_exclusive_group()
    size.add_argument("--max-size", type=int, metavar="PX",
                      help="Längste Kante maximal PX Pixel (proportional)")
    size.add_argument("--width", type=int, metavar="PX",
                      help="Feste Breite in Pixeln")
    parser.add_argument("--height", type=int, metavar="PX",
                        help="Feste Höhe in Pixeln (mit --width kombinierbar)")
    parser.add_argument("--grayscale", action="store_true",
                        help="Bilder als Graustufen ausgeben")
    args = parser.parse_args()

    if not args.input_dir.is_dir():
        parser.error("input_dir muss ein existierender Ordner sein.")
    process_folder(
        args.input_dir,
        args.output_dir,
        grayscale=args.grayscale,
        width=args.width,
        height=args.height,
        max_size=args.max_size,
    )


if __name__ == "__main__":
    main()
