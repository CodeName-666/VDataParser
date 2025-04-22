#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Konvertiert Qt Designer UI-Dateien (.ui) und Ressourcen-Dateien (.qrc)
mithilfe von pyside6-uic und pyside6-rcc in Python-Dateien.

Bietet Optionen zum Aktualisieren nur bei Bedarf, Bereinigen,
kombinierter Konvertierung, Steuerung der Ausführlichkeit und
Spiegelung der Verzeichnisstruktur.

Standard-Ausgabeverzeichnis:
- Bei --all, --rc, --ui-and-rc, --clean: src/ui/generated (oder via -o)
- Bei -f: Verzeichnis der Eingabedatei (oder via -o)

Benötigt: PySide6 und pyside6-tools
Installation: pip install pyside6 pyside6-tools
"""

import argparse
import os
import subprocess
import sys
import shutil
import time
from typing import List, Optional, Tuple

# --- Globale Konfiguration ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, os.pardir)) # Annahme: Skript ist in Unterordner

DEFAULT_UI_INPUT_DIR = os.path.join(PROJECT_ROOT, "src", "ui", "design")
DEFAULT_UI_OUTPUT_DIR = os.path.join(PROJECT_ROOT, "src", "ui", "generated")
RESOURCE_QRC_FILE_REL = os.path.join("resource", "resources.qrc")
RESOURCE_QRC_FILE = os.path.join(PROJECT_ROOT, RESOURCE_QRC_FILE_REL)
RESOURCE_OUTPUT_FILENAME = "resources_rc.py"

# --- Verbosity Levels ---
LOG_LEVEL_QUIET = 0
LOG_LEVEL_NORMAL = 1
LOG_LEVEL_VERBOSE = 2
CURRENT_LOG_LEVEL = LOG_LEVEL_NORMAL

# --- Benötigte Tools ---
REQUIRED_TOOLS = {
    "uic": "pyside6-uic",
    "rcc": "pyside6-rcc"
}

# --- Logging-Funktionen --- (Unverändert)
def log_message(level: int, message: str, **kwargs):
    if CURRENT_LOG_LEVEL >= level:
        print(message, **kwargs)
def log_error(message: str, **kwargs):
    print(f"Fehler: {message}", file=sys.stderr, **kwargs)
def log_warning(message: str, **kwargs):
    if CURRENT_LOG_LEVEL > LOG_LEVEL_QUIET:
        print(f"Warnung: {message}", **kwargs)
def log_info(message: str, **kwargs):
    log_message(LOG_LEVEL_NORMAL, message, **kwargs)
def log_verbose(message: str, **kwargs):
    log_message(LOG_LEVEL_VERBOSE, message, **kwargs)

# --- Hilfsfunktionen --- (check_tools_availability, run_command, should_convert unverändert)
def check_tools_availability() -> bool:
    all_found = True
    log_verbose("Prüfe Verfügbarkeit der Tools...")
    for name, command in REQUIRED_TOOLS.items():
        if shutil.which(command):
            log_verbose(f"  - '{command}' gefunden.")
        else:
            log_error(f"Benötigtes Tool '{command}' ({name}) nicht im System-PATH gefunden.")
            all_found = False
    if not all_found:
        log_error("Stellen Sie sicher, dass PySide6 (insbesondere pyside6-tools) korrekt installiert ist.")
    return all_found

def run_command(command: List[str], success_msg: str, error_msg_prefix: str) -> bool:
    log_verbose(f"Führe Befehl aus: {' '.join(command)}")
    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True, encoding='utf-8')
        log_info(success_msg)
        if result.stdout: log_verbose(f"  STDOUT: {result.stdout.strip()}")
        if result.stderr: log_verbose(f"  STDERR: {result.stderr.strip()}")
        return True
    except FileNotFoundError:
        log_error(f"Befehl '{command[0]}' nicht gefunden.")
        return False
    except subprocess.CalledProcessError as e:
        log_error(f"{error_msg_prefix}")
        log_error(f"  Befehl: {' '.join(e.cmd)}")
        log_error(f"  Return Code: {e.returncode}")
        if e.stdout: log_error(f"  STDOUT: {e.stdout.strip()}")
        if e.stderr: log_error(f"  STDERR: {e.stderr.strip()}")
        return False
    except Exception as e:
        log_error(f"Unerwarteter Fehler bei Befehl '{' '.join(command)}': {e}")
        return False

def should_convert(source_path: str, target_path: str, update_only: bool) -> bool:
    if not update_only: return True
    if not os.path.exists(target_path):
        log_verbose(f"Zieldatei {target_path} existiert nicht, Konvertierung notwendig.")
        return True
    try:
        source_mtime = os.path.getmtime(source_path)
        target_mtime = os.path.getmtime(target_path)
        if source_mtime > target_mtime:
            log_verbose(f"Quelldatei {source_path} ist neuer als {target_path}, Konvertierung notwendig.")
            return True
        else:
            log_verbose(f"Zieldatei {target_path} ist aktuell, Konvertierung übersprungen.")
            return False
    except Exception as e:
        log_warning(f"Fehler beim Prüfen der Zeitstempel für {source_path} / {target_path}: {e}")
        return True # Im Zweifel konvertieren

# --- Kernfunktionen --- (find_ui_file_path, convert_ui, convert_all_ui, convert_rc, clean_generated_files unverändert)
def find_ui_file_path(ui_file_arg: str, input_dir: str) -> Optional[Tuple[str, Optional[str]]]:
    potential_paths_args = [ui_file_arg]
    if not ui_file_arg.lower().endswith(".ui"):
        potential_paths_args.append(ui_file_arg + ".ui")
    abs_input_dir = os.path.abspath(input_dir)
    for path_candidate_arg in potential_paths_args:
        if os.path.isabs(path_candidate_arg):
            abs_path = os.path.normpath(path_candidate_arg)
            if os.path.isfile(abs_path):
                log_verbose(f"Interpretiere '{ui_file_arg}' als absoluten Pfad.")
                relative_path = None
                try:
                    relative_path = os.path.relpath(abs_path, abs_input_dir)
                    if relative_path.startswith(".."): relative_path = None
                except ValueError: relative_path = None
                return abs_path, relative_path
            continue
        path_rel_cwd = os.path.abspath(path_candidate_arg)
        path_rel_cwd = os.path.normpath(path_rel_cwd)
        if os.path.isfile(path_rel_cwd):
             path_rel_input_dir = None
             try:
                 path_rel_input_dir = os.path.relpath(path_rel_cwd, abs_input_dir)
                 if path_rel_input_dir.startswith(".."): path_rel_input_dir = None
             except ValueError: path_rel_input_dir = None
             if path_rel_input_dir is None:
                 log_verbose(f"Interpretiere '{ui_file_arg}' als Pfad relativ zum aktuellen Verzeichnis ({os.getcwd()}).")
                 return path_rel_cwd, None
        path_rel_input = os.path.join(abs_input_dir, path_candidate_arg)
        path_rel_input = os.path.normpath(path_rel_input)
        if os.path.isfile(path_rel_input):
            log_verbose(f"Interpretiere '{ui_file_arg}' als Pfad relativ zum Input-Verzeichnis ({input_dir}).")
            relative_path = os.path.relpath(path_rel_input, abs_input_dir)
            return path_rel_input, relative_path
    return None

def convert_ui(ui_file_arg: str, input_dir: str, output_dir: str, update_only: bool, mirror_structure: bool) -> bool:
    found_path_info = find_ui_file_path(ui_file_arg, input_dir)
    if found_path_info is None:
        log_error(f"UI-Datei '{ui_file_arg}' konnte nicht gefunden werden (geprüft: absolut, relativ CWD, relativ zu {input_dir}, auch mit .ui).")
        return False
    input_path, relative_to_input = found_path_info
    base_name = os.path.basename(input_path)
    output_filename = os.path.splitext(base_name)[0] + "_ui.py"
    final_output_dir = output_dir
    if mirror_structure and relative_to_input is not None and os.path.dirname(relative_to_input):
        relative_dir = os.path.dirname(relative_to_input)
        final_output_dir = os.path.join(output_dir, relative_dir)
        log_verbose(f"Spiegelung aktiv: Zielordner wird {final_output_dir}")
    elif mirror_structure and relative_to_input is None:
        log_verbose(f"Spiegelung aktiv, aber Datei {input_path} liegt außerhalb von {input_dir}. Wird in {output_dir} abgelegt.")
    output_path = os.path.join(final_output_dir, output_filename)
    if not should_convert(input_path, output_path, update_only):
        return True # Überspringen ist auch ein Erfolg
    try:
        os.makedirs(final_output_dir, exist_ok=True)
    except OSError as e:
        log_error(f"Konnte Ausgabe-Verzeichnis nicht erstellen: {final_output_dir}\n{e}")
        return False
    command = [REQUIRED_TOOLS["uic"], input_path, "-o", output_path]
    # Verwende relpath vom Projekt-Root für übersichtlichere Logs
    try:
        rel_input = os.path.relpath(input_path, PROJECT_ROOT)
        rel_output = os.path.relpath(output_path, PROJECT_ROOT)
    except ValueError: # Falls außerhalb des Projekt-Roots
        rel_input = input_path
        rel_output = output_path
    success_msg = f"Konvertiert: {rel_input} -> {rel_output}"
    error_msg = f"Fehler beim Konvertieren von {input_path} nach {output_path}"
    return run_command(command, success_msg, error_msg)

def convert_all_ui(input_dir: str, output_dir: str, update_only: bool, mirror_structure: bool) -> bool:
    if not os.path.isdir(input_dir):
        log_error(f"Eingabe-Verzeichnis nicht gefunden: {input_dir}")
        return False
    log_info(f"Suche nach .ui Dateien in '{input_dir}'...")
    found_files = False
    all_successful = True
    for root, _, files in os.walk(input_dir):
        for filename in files:
            if filename.lower().endswith(".ui"):
                found_files = True
                absolute_ui_path = os.path.join(root, filename)
                if not convert_ui(absolute_ui_path, input_dir, output_dir, update_only, mirror_structure):
                    all_successful = False # Merken, wenn ein Fehler auftritt
    if not found_files:
        log_info(f"Keine .ui Dateien in '{input_dir}' gefunden.")
    return all_successful

def convert_rc(qrc_file_path: str, output_dir: str, output_filename: str, update_only: bool) -> bool:
    if not os.path.isfile(qrc_file_path):
        log_error(f"Ressourcen-Datei (.qrc) nicht gefunden: {qrc_file_path}")
        return False
    output_path = os.path.join(output_dir, output_filename)
    if not should_convert(qrc_file_path, output_path, update_only):
        return True # Überspringen ist auch ein Erfolg
    try:
        os.makedirs(output_dir, exist_ok=True)
    except OSError as e:
        log_error(f"Konnte Ausgabe-Verzeichnis nicht erstellen: {output_dir}\n{e}")
        return False
    command = [REQUIRED_TOOLS["rcc"], qrc_file_path, "-o", output_path]
    try:
        rel_input = os.path.relpath(qrc_file_path, PROJECT_ROOT)
        rel_output = os.path.relpath(output_path, PROJECT_ROOT)
    except ValueError:
        rel_input = qrc_file_path
        rel_output = output_path
    success_msg = f"Konvertiert: {rel_input} -> {rel_output}"
    error_msg = f"Fehler beim Konvertieren von {qrc_file_path} nach {output_path}"
    return run_command(command, success_msg, error_msg)

def clean_generated_files(output_dir: str, resource_filename: str):
    log_info(f"Suche nach generierten Dateien in '{output_dir}' zum Löschen...")
    if not os.path.isdir(output_dir):
        log_warning(f"Ausgabe-Verzeichnis '{output_dir}' existiert nicht, nichts zu löschen.")
        return
    cleaned_count = 0
    resource_path = os.path.join(output_dir, resource_filename)
    if os.path.isfile(resource_path):
        try:
            os.remove(resource_path)
            log_info(f"Gelöscht: {resource_path}")
            cleaned_count += 1
        except OSError as e:
            log_error(f"Konnte Ressourcendatei nicht löschen: {resource_path}\n{e}")
    for root, _, files in os.walk(output_dir):
        for filename in files:
            if filename.lower().endswith("_ui.py"):
                ui_path = os.path.join(root, filename)
                try:
                    os.remove(ui_path)
                    log_info(f"Gelöscht: {ui_path}")
                    cleaned_count += 1
                except OSError as e:
                    log_error(f"Konnte UI-Datei nicht löschen: {ui_path}\n{e}")
    deleted_dirs = 0
    for root, dirs, _ in os.walk(output_dir, topdown=False):
        for dir_name in dirs:
            dir_path = os.path.join(root, dir_name)
            try:
                if not os.listdir(dir_path):
                    os.rmdir(dir_path)
                    log_verbose(f"Leeres Verzeichnis gelöscht: {dir_path}")
                    deleted_dirs += 1
            except OSError as e:
                log_warning(f"Konnte leeres Verzeichnis nicht löschen: {dir_path}\n{e}")
    if cleaned_count == 0 and deleted_dirs == 0:
         log_info("Keine generierten Dateien zum Löschen gefunden.")
    else:
         log_info(f"Bereinigung abgeschlossen. {cleaned_count} Datei(en) und {deleted_dirs} leere(s) Verzeichnis(se) gelöscht.")


# --- Argument Parser und Main ---

def arguments() -> argparse.Namespace:
    """Verarbeitet die Kommandozeilenargumente."""
    parser = argparse.ArgumentParser(
        description="Konvertiert Qt Designer UI (.ui) und Ressourcen (.qrc) Dateien nach Python.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    action_group = parser.add_mutually_exclusive_group(required=True)
    action_group.add_argument("-f", "--file", help="Einzelne UI-Datei konvertieren...", metavar="UI_FILE_OR_PATH")
    action_group.add_argument("--all", action="store_true", help="Alle .ui-Dateien im --input-dir (rekursiv) konvertieren.")
    action_group.add_argument("--rc", action="store_true", help=f"Nur die Standard-Ressourcen-Datei konvertieren:\n'{RESOURCE_QRC_FILE}'")
    action_group.add_argument("--ui-and-rc", action="store_true", help="Alle UI-Dateien UND die Standard-Ressourcen-Datei konvertieren.")
    action_group.add_argument("--clean", action="store_true", help="Generierte Dateien im Ausgabeverzeichnis löschen.")

    ui_group = parser.add_argument_group('UI Konvertierungsoptionen')
    ui_group.add_argument("-i", "--input-dir", default=DEFAULT_UI_INPUT_DIR, help=f"Basisverzeichnis für UI-Dateien (--all) und Fallback für relative Pfade (-f).\nStandard: '{DEFAULT_UI_INPUT_DIR}'", metavar="DIR")
    ui_group.add_argument("--mirror-structure", action="store_true", help="Verzeichnisstruktur von --input-dir im --output-dir nachbilden.")

    common_group = parser.add_argument_group('Allgemeine Optionen')
    common_group.add_argument(
        "-o", "--output-dir",
        default=None, # <-- WICHTIG: Default ist None, wird in main() behandelt
        help="Stammverzeichnis für generierte Python-Dateien.\n"
             f"Standard (--all, --rc, --ui-and-rc, --clean): '{DEFAULT_UI_OUTPUT_DIR}'\n"
             "Standard (-f): Verzeichnis der Eingabedatei.",
        metavar="DIR"
    )
    common_group.add_argument("-u", "--update-only", action="store_true", help="Nur konvertieren, wenn Quelldatei neuer als Zieldatei ist.")

    verbosity_group = parser.add_mutually_exclusive_group()
    verbosity_group.add_argument("-v", "--verbose", action="store_const", const=LOG_LEVEL_VERBOSE, dest="verbosity", help="Ausführliche Ausgabe.")
    verbosity_group.add_argument("-q", "--quiet", action="store_const", const=LOG_LEVEL_QUIET, dest="verbosity", help="Minimale Ausgabe (nur Fehler).")
    parser.set_defaults(verbosity=LOG_LEVEL_NORMAL)

    return parser.parse_args()

def main() -> None:
    """Hauptfunktion: Verarbeitet Argumente und startet die Aktionen."""
    global CURRENT_LOG_LEVEL
    args = arguments()
    CURRENT_LOG_LEVEL = args.verbosity

    # --- Tool-Prüfung ---
    # Bei --clean nicht notwendig
    if not args.clean and not check_tools_availability():
         sys.exit(1)

    # --- Pfade vorbereiten ---
    # Eingabepfade (immer normalisieren)
    input_dir = os.path.abspath(os.path.normpath(args.input_dir))
    qrc_file = os.path.abspath(os.path.normpath(RESOURCE_QRC_FILE))

    # --- Ausgabepfad bestimmen ---
    final_output_dir_str: Optional[str] = None # Temporäre Variable

    if args.file:
        # Bei -f: Erst Input finden, dann Output bestimmen
        found_path_info = find_ui_file_path(args.file, input_dir)
        if found_path_info is None:
            # Fehler wird später in convert_ui behandelt, aber wir brauchen einen Fallback für output_dir
            log_error(f"Konnte Eingabedatei für -f '{args.file}' nicht finden. Abbruch.")
            sys.exit(1)

        input_path, _ = found_path_info

        if args.output_dir is None:
            # Kein -o angegeben bei -f -> Nimm Verzeichnis der Input-Datei
            final_output_dir_str = os.path.dirname(input_path)
            log_verbose(f"Kein -o bei -f angegeben. Verwende Verzeichnis der Eingabedatei: {final_output_dir_str}")
        else:
            # -o wurde angegeben
            final_output_dir_str = args.output_dir
            log_verbose(f"-o angegeben: {final_output_dir_str}")

    # Für alle anderen Aktionen oder wenn -o bei -f angegeben wurde:
    if final_output_dir_str is None: # Nur setzen, wenn nicht schon durch -f ohne -o gesetzt
        if args.output_dir is None:
            # Kein -o angegeben -> Nimm den Standard-Output-Dir
            final_output_dir_str = DEFAULT_UI_OUTPUT_DIR
            log_verbose(f"Kein -o angegeben. Verwende Standard-Ausgabeverzeichnis: {final_output_dir_str}")
        else:
            # -o wurde angegeben
            final_output_dir_str = args.output_dir
            log_verbose(f"-o angegeben: {final_output_dir_str}")

    # Finalen Output-Pfad normalisieren
    output_dir = os.path.abspath(os.path.normpath(final_output_dir_str))
    log_verbose(f"Finales Ausgabeverzeichnis: {output_dir}")


    # --- Aktionen ausführen ---
    start_time = time.time()
    overall_success = True # Um Exit-Code zu setzen

    if args.clean:
        log_info(f"--- Starte Bereinigung in '{output_dir}' ---")
        clean_generated_files(output_dir, RESOURCE_OUTPUT_FILENAME)
        # Clean gilt immer als erfolgreich, wenn es durchläuft

    elif args.all:
        log_info(f"--- Konvertiere alle UI-Dateien (Input: '{input_dir}', Output: '{output_dir}') ---")
        overall_success = convert_all_ui(input_dir, output_dir, args.update_only, args.mirror_structure)

    elif args.file:
        log_info(f"--- Konvertiere einzelne UI-Datei (Input: '{args.file}', Output-Basis: '{output_dir}') ---")
        # Input_path wurde oben schon bestimmt
        overall_success = convert_ui(args.file, input_dir, output_dir, args.update_only, args.mirror_structure)

    elif args.rc:
        log_info(f"--- Konvertiere Ressourcen-Datei (Input: '{qrc_file}', Output: '{output_dir}') ---")
        overall_success = convert_rc(qrc_file, output_dir, RESOURCE_OUTPUT_FILENAME, args.update_only)

    elif args.ui_and_rc:
        log_info(f"--- Konvertiere alle UI-Dateien UND Ressourcen-Datei (Output: '{output_dir}') ---")
        # Führe beides aus, Erfolg ist nur gegeben, wenn beides klappt
        ui_success = convert_all_ui(input_dir, output_dir, args.update_only, args.mirror_structure)
        rc_success = convert_rc(qrc_file, output_dir, RESOURCE_OUTPUT_FILENAME, args.update_only)
        overall_success = ui_success and rc_success

    end_time = time.time()
    duration = end_time - start_time
    if overall_success:
        log_info(f"--- Vorgang erfolgreich abgeschlossen in {duration:.2f} Sekunden ---")
        sys.exit(0)
    else:
        log_error(f"--- Vorgang mit Fehlern abgeschlossen nach {duration:.2f} Sekunden ---")
        sys.exit(1)


if __name__ == "__main__":
    main()