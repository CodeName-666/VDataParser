#!/usr/bin/env python3
"""
raster2svg.py  –  Raster → SVG-Konverter
   * Skalierung (max-size / fixe Breite/Höhe)
   * Graustufen oder hartes Schwarz-Weiß
   * Nur-Linien-Modus: nicht-schwarze Pixel → transparent

Installieren:
    pip install pillow svgwrite numpy
"""

import argparse
import base64
import io
from pathlib import Path

import numpy as np
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
def apply_only_black_lines(img: Image.Image, threshold: int) -> Image.Image:
    """
    Belässt nur sehr dunkle Pixel schwarz, alles andere wird transparent.
    threshold: 0–255 – Pixel mit allen drei RGB-Kanälen < threshold bleiben.
    """
    arr = np.array(img.convert("RGBA"))
    rgb = arr[..., :3]
    dark = np.all(rgb < threshold, axis=2)

    # Alpha: dunkel → 255, sonst 0
    arr[..., 3] = np.where(dark, 255, 0).astype(np.uint8)
    # Farbe: dunkel → schwarz (0,0,0), Rest egal (alpha 0)
    arr[..., :3] = np.where(dark[..., None], 0, arr[..., :3])

    return Image.fromarray(arr)


# ------------------------------------------------------------
def process_folder(src: Path,
                   dst: Path,
                   grayscale: bool,
                   blackwhite: bool,
                   ink_only: bool,
                   threshold: int,
                   width: int | None,
                   height: int | None,
                   max_size: int | None) -> None:
    dst.mkdir(parents=True, exist_ok=True)
    exts = {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tiff"}
    for file in src.iterdir():
        if not (file.suffix.lower() in exts and file.is_file()):
            continue

        img = Image.open(file).convert("RGBA")

        # 1) Nur-Linien-Modus
        if ink_only:
            img = apply_only_black_lines(img, threshold)

        # 2) Hartes Schwarz-Weiß
        elif blackwhite:
            img = img.convert("L").convert("1").convert("RGBA")

        # 3) Graustufen
        elif grayscale:
            img = img.convert("L").convert("RGBA")

        out_svg = dst / f"{file.stem}.svg"
        raster_to_svg(img, out_svg, width, height, max_size)
        print(f"✔  {file.name:<30} → {out_svg.name}")


# ------------------------------------------------------------
def main() -> None:
    p = argparse.ArgumentParser(
        description="Konvertiert alle Rasterbilder eines Ordners in SVG "
                    "(inline-PNG, optional skaliert, Graustufe, 1-Bit oder "
                    "Nur-Linien-Modus).")
    p.add_argument("input_dir", type=Path)
    p.add_argument("output_dir", type=Path)

    size = p.add_mutually_exclusive_group()
    size.add_argument("--max-size", type=int, metavar="PX",
                      help="Max. Kantenlänge (proportional)")
    size.add_argument("--width", type=int, metavar="PX",
                      help="Feste Breite")
    p.add_argument("--height", type=int, metavar="PX",
                   help="Feste Höhe (nur in Kombi mit --width)")

    p.add_argument("--grayscale", action="store_true",
                   help="Graustufenausgabe")
    p.add_argument("--bw", "--blackwhite", dest="blackwhite",
                   action="store_true",
                   help="Hartes Schwarz-Weiß (1-Bit)")
    p.add_argument("--ink", "--only-black-lines", dest="ink_only",
                   action="store_true",
                   help="Nur dunkle Linien behalten, Rest transparent")
    p.add_argument("--threshold", type=int, default=60, metavar="T",
                   help="Schwellwert 0–255 für --ink (Default 60)")
    args = p.parse_args()

    if not args.input_dir.is_dir():
        p.error("input_dir ist kein gültiger Ordner.")

    process_folder(
        args.input_dir,
        args.output_dir,
        grayscale=args.grayscale,
        blackwhite=args.blackwhite,
        ink_only=args.ink_only,
        threshold=max(0, min(args.threshold, 255)),
        width=args.width,
        height=args.height,
        max_size=args.max_size,
    )


if __name__ == "__main__":
    main()
