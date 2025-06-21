#!/usr/bin/env python3
"""
raster2svg.py  –  Raster → SVG (inkl. Skalierung, Graustufen ODER hartes Schwarz-Weiß)

Install:
    pip install pillow svgwrite
"""

import argparse
import base64
import io
from pathlib import Path

from PIL import Image
import svgwrite


# ------------------------------------------------------------
def raster_to_svg(img: Image.Image,
                  out_path: Path,
                  width: int | None = None,
                  height: int | None = None,
                  max_size: int | None = None) -> None:
    """Speichert ein Pillow-Image als SVG mit inline-PNG."""
    if max_size:
        img.thumbnail((max_size, max_size), Image.LANCZOS)
    if width or height:
        img = img.resize((width or img.width, height or img.height),
                         Image.LANCZOS)

    buf = io.BytesIO()
    img.save(buf, "PNG")
    b64 = base64.b64encode(buf.getvalue()).decode()

    w, h = img.size
    dwg = svgwrite.Drawing(size=(f"{w}px", f"{h}px"))
    dwg.add(dwg.image(
        href=f"data:image/png;base64,{b64}",
        insert=(0, 0),
        size=(w, h)))
    dwg.saveas(out_path)


# ------------------------------------------------------------
def process_folder(src: Path,
                   dst: Path,
                   grayscale: bool,
                   blackwhite: bool,
                   width: int | None,
                   height: int | None,
                   max_size: int | None) -> None:
    dst.mkdir(parents=True, exist_ok=True)
    exts = {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tiff"}
    for file in src.iterdir():
        if file.suffix.lower() not in exts or not file.is_file():
            continue
        img = Image.open(file).convert("RGBA")

        if blackwhite:
            # 1-Bit: erst Graustufe, dann nach 1-Bit mit Default-Dithering
            img = img.convert("L").convert("1").convert("RGBA")
        elif grayscale:
            img = img.convert("L").convert("RGBA")

        out_svg = dst / (file.stem + ".svg")
        raster_to_svg(img, out_svg, width, height, max_size)
        print(f"✔  {file.name:<30} → {out_svg.name}")


# ------------------------------------------------------------
def main() -> None:
    p = argparse.ArgumentParser(
        description="Konvertiert Rasterbilder eines Ordners zu SVGs "
                    "(inline-PNG, optional skaliert & BW / Graustufe).")
    p.add_argument("input_dir", type=Path)
    p.add_argument("output_dir", type=Path)

    size = p.add_mutually_exclusive_group()
    size.add_argument("--max-size", type=int, metavar="PX",
                      help="Maximale Kantenlänge (proportional)")
    size.add_argument("--width", type=int, metavar="PX",
                      help="Feste Breite")
    p.add_argument("--height", type=int, metavar="PX",
                   help="Feste Höhe (mit --width kombinierbar)")

    p.add_argument("--grayscale", action="store_true",
                   help="Graustufenbild erzeugen")
    p.add_argument("--bw", "--blackwhite", dest="blackwhite",
                   action="store_true",
                   help="Hartes Schwarz-Weiß (1-Bit); überschreibt --grayscale")
    args = p.parse_args()

    if not args.input_dir.is_dir():
        p.error("input_dir ist kein gültiger Ordner.")

    process_folder(
        args.input_dir,
        args.output_dir,
        grayscale=args.grayscale,
        blackwhite=args.blackwhite,
        width=args.width,
        height=args.height,
        max_size=args.max_size,
    )


if __name__ == "__main__":
    main()
