"""Utilities for file existence checks with optional user confirmation."""

from __future__ import annotations

from pathlib import Path
from typing import Sequence, Tuple, TYPE_CHECKING

from PySide6.QtWidgets import QMessageBox

if TYPE_CHECKING:  # pragma: no cover - imported for type hints only
    from PySide6.QtWidgets import QWidget


def check_existing_files(
    target_dir: str | Path,
    expected_files: Sequence[str | Path],
    *,
    parent: "QWidget" | None = None,
    confirm: bool = False,
) -> Tuple[list[str], bool]:
    """Check whether expected files exist in *target_dir*.

    Parameters
    ----------
    target_dir:
        Directory in which to check for files.
    expected_files:
        Sequence of file names or paths to validate. Relative paths are
        resolved against ``target_dir``. Only the file names are returned.
    parent:
        Optional parent widget used for confirmation dialogs.
    confirm:
        If ``True`` and any file exists, a confirmation dialog asking
        whether to overwrite is shown.

    Returns
    -------
    tuple[list[str], bool]
        ``(existing, proceed)`` where ``existing`` contains the names of
        files already present in ``target_dir`` and ``proceed`` indicates
        whether the caller may continue (``False`` when confirmation was
        denied).
    """
    dir_path = Path(target_dir)
    existing: list[str] = []
    for f in expected_files:
        path = Path(f)
        path = dir_path / path.name if not path.is_absolute() else path
        if path.exists():
            existing.append(path.name)

    proceed = True
    if confirm and existing:
        msg = (
            "Im Zielordner existieren bereits folgende Dateien:\n\n"
            + "\n".join(f"- {name}" for name in existing)
            + "\n\nÜberschreiben?"
        )
        reply = QMessageBox.warning(
            parent,
            "Dateien überschreiben?",
            msg,
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        proceed = reply == QMessageBox.Yes

    return existing, proceed
