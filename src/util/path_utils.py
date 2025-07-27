"""Utility helpers for path manipulation."""

from __future__ import annotations

import os


def ensure_trailing_sep(path: str) -> str:
    """Return ``path`` with a single trailing ``os.sep``.

    The separator is normalised to the host operating system. If a separator is
    already present it will be replaced with ``os.sep``. Empty strings are
    returned unchanged.

    Args:
        path (str): The input path string.

    Returns:
        str: The path guaranteed to end with ``os.sep``.
    """
    result = path
    if path:
        if path.endswith(("/", "\\")):
            if not path.endswith(os.sep):
                result = path[:-1] + os.sep
        else:
            result = path + os.sep
    return result
