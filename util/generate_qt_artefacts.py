#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generate Qt Artefacts – wandelt Qt‑Designer‑Dateien in Python‑Module um
=====================================================================

* **UI‑Dateien** (`*.ui`) → `pyside6-uic` → `<name>_ui.py`
* **Ressourcen‑Dateien** (`*.qrc`) → `pyside6-rcc` → `<name>_rc.py`

Neu seit **22. Juni 2025**
-------------------------
* **--qrc-file / --qrc-input** – eigener Pfad zur einzulesenden `.qrc`‑Datei
* **--rc-output-name** – frei wählbarer Dateiname der generierten
  Ressourcen‑Python‑Datei
* Falls nicht angegeben, gelten die bisherigen Defaults
  (`src/resource/resources.qrc` & `resources_rc.py`).

Benötigte Pakete
----------------
``pip install pyside6 pyside6-tools``
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Iterable, List, Optional, Tuple

###############################################################################
# Globale Konfiguration                                                       #
###############################################################################
SCRIPT_DIR: Path = Path(__file__).resolve().parent
PROJECT_ROOT: Path = SCRIPT_DIR.parent  # Annahme: Skript liegt in util/

DEFAULT_UI_INPUT_DIR: Path = PROJECT_ROOT / "src" / "ui" / "design"
DEFAULT_UI_OUTPUT_DIR: Path = PROJECT_ROOT / "src" / "ui" / "generated"

RESOURCE_QRC_FILE_REL: Path = Path("src/resource") / "resources.qrc"
RESOURCE_QRC_FILE: Path = PROJECT_ROOT / RESOURCE_QRC_FILE_REL
RESOURCE_OUTPUT_FILENAME: str = "resources_rc.py"

###############################################################################
# Logging                                                                     #
###############################################################################
LOG_LEVEL_QUIET = 0
LOG_LEVEL_NORMAL = 1
LOG_LEVEL_VERBOSE = 2
CURRENT_LOG_LEVEL = LOG_LEVEL_NORMAL


def _log(level: int, msg: str, *, file=sys.stdout) -> None:  # noqa: D401
    """Einfacher Logger, abhängig von *CURRENT_LOG_LEVEL*."""
    if level <= CURRENT_LOG_LEVEL:
        print(msg, file=file)


def log_info(msg: str) -> None:  # noqa: D401
    _log(LOG_LEVEL_NORMAL, msg)


def log_verbose(msg: str) -> None:  # noqa: D401
    _log(LOG_LEVEL_VERBOSE, msg)


def log_warn(msg: str) -> None:  # noqa: D401
    _log(LOG_LEVEL_NORMAL, f"Warnung: {msg}")


def log_error(msg: str) -> None:  # noqa: D401
    _log(LOG_LEVEL_QUIET, f"Fehler: {msg}", file=sys.stderr)


###############################################################################
# Tool‑Verfügbarkeit                                                          #
###############################################################################
REQUIRED_TOOLS: dict[str, str] = {
    "uic": "pyside6-uic",
    "rcc": "pyside6-rcc",
}


def check_tools() -> bool:  # noqa: D401
    """Prüft, ob *pyside6-uic* und *pyside6-rcc* verfügbar sind."""
    ok = True
    for name, cmd in REQUIRED_TOOLS.items():
        if shutil.which(cmd) is None:
            log_error(
                f"Benötigtes Tool '{cmd}' ({name}) nicht im PATH gefunden.")
            ok = False
        else:
            log_verbose(f"Tool '{cmd}' gefunden.")
    return ok

###############################################################################
# Hilfsfunktionen                                                             #
###############################################################################


def _run(cmd: list[str], label: str) -> bool:  # noqa: D401
    """Führt *cmd* aus und schreibt stdout/stderr bei Bedarf."""
    log_verbose("Ausführen: " + " ".join(cmd))
    try:
        cp = subprocess.run(cmd, check=True, capture_output=True, text=True)
    except FileNotFoundError:
        log_error(f"Befehl '{cmd[0]}' nicht gefunden.")
        return False
    except subprocess.CalledProcessError as exc:
        log_error(f"{label} fehlgeschlagen (Code {exc.returncode}).")
        if exc.stdout:
            log_verbose("STDOUT:\n" + exc.stdout)
        if exc.stderr:
            log_verbose("STDERR:\n" + exc.stderr)
        return False

    log_info(label)
    if cp.stdout.strip():
        log_verbose("STDOUT:\n" + cp.stdout.strip())
    if cp.stderr.strip():
        log_verbose("STDERR:\n" + cp.stderr.strip())
    return True


def _needs_update(source: Path, target: Path, update_only: bool) -> bool:  # noqa: D401
    """True → (re)build erforderlich."""
    if not target.exists():
        return True
    if not update_only:
        return True
    return source.stat().st_mtime > target.stat().st_mtime

###############################################################################
# UI‑Konvertierung                                                            #
###############################################################################


def convert_ui_file(
    ui_file: Path,
    output_dir: Path,
    *,
    update_only: bool,
    mirror_structure: bool,
) -> bool:  # noqa: D401
    """Konvertiert eine einzelne *.ui* Datei mittels *pyside6-uic*."""
    if not ui_file.exists():
        log_error(f"UI‑Datei nicht gefunden: {ui_file}")
        return False

    # Zielpfad bestimmen
    if mirror_structure:
        try:
            rel = ui_file.relative_to(DEFAULT_UI_INPUT_DIR)
            out_dir = output_dir / rel.parent
        except ValueError:  # ui_file außerhalb des Input‑Verzeichnisses
            out_dir = output_dir
    else:
        out_dir = output_dir

    out_dir.mkdir(parents=True, exist_ok=True)
    target = out_dir / (ui_file.stem + "_ui.py")

    if not _needs_update(ui_file, target, update_only):
        log_verbose(f"Überspringe {ui_file} (aktuell).")
        return True

    cmd = [REQUIRED_TOOLS["uic"], str(ui_file), "-o", str(target)]
    label = f"{ui_file.relative_to(PROJECT_ROOT)} → {target.relative_to(PROJECT_ROOT)}"
    return _run(cmd, label)


def iter_ui_files(path: Path) -> Iterable[Path]:  # noqa: D401
    """Liefert rekursiv alle *.ui* Dateien."""
    return path.rglob("*.ui") if path.is_dir() else ([path] if path.suffix == ".ui" else [])


def convert_all_ui(
    input_dir: Path,
    output_dir: Path,
    *,
    update_only: bool,
    mirror_structure: bool,
) -> bool:  # noqa: D401
    """Konvertiert alle UI‑Dateien im Eingabe‑Verzeichnis."""
    if not input_dir.exists():
        log_error(f"Eingabe‑Verzeichnis nicht gefunden: {input_dir}")
        return False

    ui_files = list(iter_ui_files(input_dir))
    if not ui_files:
        log_warn("Keine .ui Dateien gefunden.")
        return True

    log_info(f"Konvertiere {len(ui_files)} UI‑Datei(en)…")
    success = True
    for ui in ui_files:
        success &= convert_ui_file(
            ui, output_dir, update_only=update_only, mirror_structure=mirror_structure)
    return success

###############################################################################
# RC‑Konvertierung                                                            #
###############################################################################


def convert_rc(
    qrc_path: Path,
    output_name: str,
    *,
    update_only: bool,
) -> bool:  # noqa: D401
    """Konvertiert eine *.qrc* Datei via *pyside6-rcc* in ein Python‑Modul."""
    if not qrc_path.exists():
        log_error(f"QRC‑Datei nicht gefunden: {qrc_path}")
        return False

    output_py = qrc_path.parent / output_name
    if not _needs_update(qrc_path, output_py, update_only):
        log_verbose(f"Überspringe {qrc_path} (aktuell).")
        return True
    cmd = [
        REQUIRED_TOOLS["rcc"],
        "-g", "python",
        "-o", str(output_py),
        str(qrc_path),
    ]
    # einfache, fehlerfreie Erzeugung relativer Pfade
    rel_qrc = os.path.relpath(qrc_path, PROJECT_ROOT)
    rel_out = os.path.relpath(output_py, PROJECT_ROOT)
    label = f"{rel_qrc} → {rel_out}"
    return _run(cmd, label)

###############################################################################
# Cleaning                                                                    #
###############################################################################


def clean(ui_output_dir: Path, qrc_path: Path, rc_output_name: str) -> None:  # noqa: D401
    """Entfernt generierte Dateien."""
    removed = 0

    # *_ui.py Dateien
    for py in ui_output_dir.rglob("*_ui.py"):
        py.unlink(missing_ok=True)
        removed += 1

    # resources_rc.py (oder alternativer Name)
    rc_py = qrc_path.parent / rc_output_name
    if rc_py.exists():
        rc_py.unlink()
        removed += 1

    log_info(f"Bereinigt – {removed} Datei(en) entfernt.")

###############################################################################
# Argument‑Parser                                                             #
###############################################################################


def build_parser() -> argparse.ArgumentParser:  # noqa: D401
    p = argparse.ArgumentParser(
        prog="generate_qt_artefacts.py",
        description="Konvertiert Qt‑Designer *.ui* und *.qrc* Dateien in Python‑Module.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    grp_action = p.add_mutually_exclusive_group(required=True)
    grp_action.add_argument("--all", action="store_true",
                            help="UI und RC generieren")
    grp_action.add_argument("--ui", action="store_true",
                            help="Nur UI Dateien generieren")
    grp_action.add_argument("--rc", action="store_true",
                            help="Nur RC Datei generieren")
    grp_action.add_argument("--ui-and-rc", action="store_true",
                            help="UI und RC generieren (alias von --all)")
    grp_action.add_argument("--clean", action="store_true",
                            help="Generierte Dateien entfernen")

    p.add_argument("--input-ui-dir", default=DEFAULT_UI_INPUT_DIR,
                   type=Path, help="Verzeichnis mit *.ui* Dateien")
    p.add_argument("--output-ui-dir", default=DEFAULT_UI_OUTPUT_DIR,
                   type=Path, help="Zielverzeichnis für generierte *_ui.py* Dateien")
    p.add_argument("--mirror-structure", action="store_true",
                   help="Ordnerstruktur der Eingabe im Output spiegeln")
    p.add_argument("--update-only", action="store_true",
                   help="Nur konvertieren, wenn Quelle neuer ist als Ziel")

    # Neue Parameter 2025‑06‑22
    p.add_argument("--qrc-file", "--qrc-input", dest="qrc_file",
                   default=RESOURCE_QRC_FILE, type=Path, help="Pfad zur *.qrc* Datei")
    p.add_argument("--rc-output-name", default=RESOURCE_OUTPUT_FILENAME,
                   help="Dateiname der erzeugten Ressourcen‑Python‑Datei")

    # Logging
    p.add_argument("-v", "--verbose", action="store_true",
                   help="Ausführliche Ausgabe")
    p.add_argument("-q", "--quiet", action="store_true",
                   help="Nur Fehlermeldungen ausgeben")

    return p

###############################################################################
# Main                                                                        #
###############################################################################


def main(argv: Optional[List[str]] = None) -> None:  # noqa: D401
    global CURRENT_LOG_LEVEL  # pylint: disable=global-statement

    args = build_parser().parse_args(argv)

    # Logging‑Level
    if args.quiet:
        CURRENT_LOG_LEVEL = LOG_LEVEL_QUIET
    elif args.verbose:
        CURRENT_LOG_LEVEL = LOG_LEVEL_VERBOSE
    else:
        CURRENT_LOG_LEVEL = LOG_LEVEL_NORMAL

    # Aktionen bestimmen
    do_ui = args.ui or args.all or args.ui_and_rc
    do_rc = args.rc or args.all or args.ui_and_rc

    # Clean‐Modus
    if args.clean:
        clean(args.output_ui_dir, args.qrc_file, args.rc_output_name)
        return

    # Vorher Tool‑Verfügbarkeit prüfen
    if (do_ui or do_rc) and not check_tools():
        sys.exit(1)

    success = True

    if do_ui:
        success &= convert_all_ui(
            args.input_ui_dir,
            args.output_ui_dir,
            update_only=args.update_only,
            mirror_structure=args.mirror_structure,
        )

    if do_rc:
        success &= convert_rc(
            args.qrc_file,
            args.rc_output_name,
            update_only=args.update_only,
        )

    if not success:
        sys.exit(1)


if __name__ == "__main__":
    main()
