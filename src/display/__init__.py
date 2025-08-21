"""Display layer abstractions and implementations.

This package exposes console and (optionally) Qt-based output helpers:
- output interfaces (console/Qt)
- progress tracker abstraction + basic tracker
- progress bar abstraction + console/Qt implementations

Qt components are optional; when `PySide6` is not available the Qt exports
are set to ``None`` so consumers can handle the absence explicitly.
"""

from .output.output_interface_abstraction import OutputInterfaceAbstraction
from .output.console_output import ConsoleOutput

try:
    from .output.qt_output import QtOutput
except Exception:  # pragma: no cover - optional PySide6
    QtOutput = None  # type: ignore

from .tracker.progress_tracker_abstraction import ProgressTrackerAbstraction
from .tracker.basic_porgress_tracker import BasicProgressTracker

from .progress_bar.progress_bar_abstraction import ProgressBarAbstraction
from .progress_bar.console_progress_bar import ConsoleProgressBar
try:
    from .progress_bar.qt_progress_bar import QtProgressBar
except Exception:  # pragma: no cover - optional PySide6
    QtProgressBar = None  # type: ignore

__all__ = [
    "OutputInterfaceAbstraction",
    "ConsoleOutput",
    "QtOutput",
    "ProgressTrackerAbstraction",
    "BasicProgressTracker",
    "ProgressBarAbstraction",
    "ConsoleProgressBar",
    "QtProgressBar",
]

