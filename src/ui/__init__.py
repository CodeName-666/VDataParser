"""Qt UI entry points for the application.

This package contains high-level widgets and dialogs that compose the GUI.
Generated code from Qt Designer lives in `src/ui/generated` and should not be
edited manually.
"""

__all__ = [
    "MainMenu",
    "MainWindow",
    "MarketLoaderDialog",
    "NewMarketDialog",
    "DatabaseSelectionDialog",
]


def __getattr__(name: str):  # pragma: no cover - simple delegation
    if name == "MainMenu":
        from .main_menu import MainMenu
        return MainMenu
    if name == "MainWindow":
        from .main_window import MainWindow
        return MainWindow
    if name == "MarketLoaderDialog":
        from .market_loader_dialog import MarketLoaderDialog
        return MarketLoaderDialog
    if name == "NewMarketDialog":
        from .new_market_dialog import NewMarketDialog
        return NewMarketDialog
    if name == "DatabaseSelectionDialog":
        from .database_selection_dialog import DatabaseSelectionDialog
        return DatabaseSelectionDialog
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
