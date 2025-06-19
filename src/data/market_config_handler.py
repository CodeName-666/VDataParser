import copy
import os
from PySide6.QtCore import QObject, Signal

from pathlib import Path
from typing import Any, Dict, TYPE_CHECKING, Union

from .json_handler import JsonHandler
from .data_manager import DataManager
from log import CustomLogger  # noqa: F401
from objects import SettingsContentDataClass

class MarketConfigHandler(QObject, JsonHandler):
    """Manage one project‑configuration JSON and expose convenience helpers."""
    default_signal_loaded = Signal(object)  # Signal to notify when the default configuration is loaded
    # --------------------------- defaults --------------------------- #
    _DEFAULT_STRUCTURE: Dict[str, Any] = {
        "database": {"url": "", "port": ""},
        "market": {"market_path": "", "market_name": ""},
        "default_pdf_generation_data": {
            "template_info": {
                "pdf_path": "",
                "pdf_name": "Abholung_Template.pdf",
            },
            "coordinates": {"boxPairs": [], "singleBoxes": []},
        },
    }

    # ------------------------ construction ------------------------- #
    def __init__(self, json_path_or_data: Union[str, Path, Dict[str, Any]] = "", logger: CustomLogger or None = None) -> None:
        """Create or retrieve the *singleton* instance.

        * ``json_path_or_data`` may be a path/URL *or* a Python ``dict``.
          Empty/omitted argument starts with the default skeleton so you can
          build the config programmatically.
        * ``logger`` optional :class:`log.CustomLogger` instance.
        """
        QObject.__init__(self)
        JsonHandler.__init__(self, json_path_or_data or copy.deepcopy(
            self._DEFAULT_STRUCTURE), logger=logger)
        self._merge_defaults()
       

    # BaseDataMeta hook ----------------------------------------------------
    def reload_data(self, json_path_or_data: Union[str, Path]) -> None:  # noqa: D401
        """Reload and re‑apply defaults."""
        self.load(str(json_path_or_data))
        self._merge_defaults()

    # ------------------------- internals -------------------------- #
    def _merge_defaults(self) -> None:
        """Ensure that all mandatory keys exist in :pyattr:`json_data`."""
        if self.json_data is None:
            self.json_data = copy.deepcopy(self._DEFAULT_STRUCTURE)
            return

        def _merge(dst: Dict[str, Any], src: Dict[str, Any]) -> None:
            for key, value in src.items():
                if key not in dst:
                    dst[key] = copy.deepcopy(value)
                elif isinstance(value, dict) and isinstance(dst[key], dict):
                    _merge(dst[key], value)

        _merge(self.json_data, self._DEFAULT_STRUCTURE)

    # -------------------- database accessors ---------------------- #
    def get_database(self) -> Dict[str, str]:
        """Return the *database* section as a shallow dict."""
        return self.get_key_value(["database"]) or {}

    def set_database(self, url: str, port: str) -> None:
        """Set both ``database.url`` and ``database.port``."""
        self.set_key_value(["database", "url"], url)
        self.set_key_value(["database", "port"], port)

    # --------------------- market accessors ----------------------- #
    def get_market(self) -> Dict[str, str]:
        """Return the *market* section as a shallow dict."""
        return self.get_key_value(["market"]) or {}
    
    def get_market_path(self):
        return self.get_market()["market_path"]

    def get_market_name(self):
        return self.get_market()["market_name"]

    def get_full_market_path(self):
        path = self.get_market_path()
        return self.ensure_trailing_sep(path) + self.get_market_name()
    
    def get_pdf_generation_data(self) -> Dict[str, Any]:
        """Return the *default_pdf_generation_data* section as a shallow dict."""
        return self.get_key_value(["default_pdf_generation_data"]) or {}

    def set_market(self, market_path: str, market_name: str) -> None:
        """Set the *market* subsection."""
        self.set_key_value(["market", "market_path"], market_path)
        self.set_key_value(["market", "market_name"], market_name)

    def set_market_path(self, market_path: str) -> None:
        """Set only the market_path key in the market section."""
        self.set_key_value(["market", "market_path"], market_path)
    
    def set_market_name(self, market_name: str) -> None:
        """Set only the market_name key in the market section."""
        self.set_key_value(["market", "market_name"], market_name)
    
    def set_full_market_path(self, full_path: str) -> None:
        """
        Set the market section by parsing the provided full market path.

        The method splits the full path into a directory part (market_path)
        and a market name (market_name) using the host's OS conventions.
        """
        market_path = os.path.dirname(full_path)
        market_path = self.ensure_trailing_sep(market_path)
        market_name = os.path.basename(full_path)
        self.set_market(market_path, market_name)

    # -------------------- pdf display configuration accessors ---------------------- #
    def get_pdf_coordinates_config(self) -> Dict[str, str]:
        """Return the *pfd_coordiantes_config* section as a shallow dict."""
        return self.get_key_value(["pfd_coordiantes_config"]) or {}

    def get_pdf_coordinates_config_path(self) -> str:
        """Return the coordinates_config_path from the pfd_coordiantes_config section."""
        return self.get_pdf_coordinates_config().get("coordinates_config_path", "")

    def get_pdf_coordinates_config_name(self) -> str:
        """Return the coordinates_config_name from the pfd_coordiantes_config section."""
        return self.get_pdf_coordinates_config().get("coordinates_config_name", "")

    def get_full_pdf_coordinates_config_path(self) -> str:
        """
        Compute the full pdf coordinates configuration path by joining
        the coordinates_config_path and coordinates_config_name.
        """
        path = self.get_pdf_coordinates_config_path()
        name = self.get_pdf_coordinates_config_name()
        return self.ensure_trailing_sep(path) + name

    def set_pdf_coordinates_config(self, coordinates_config_path: str, coordinates_config_name: str) -> None:
        """Set the entire pfd_coordiantes_config section."""
        self.set_key_value(["pfd_coordiantes_config", "coordinates_config_path"], coordinates_config_path)
        self.set_key_value(["pfd_coordiantes_config", "coordinates_config_name"], coordinates_config_name)

    def set_pdf_coordinates_config_path(self, coordinates_config_path: str) -> None:
        """Set only the coordinates_config_path key in the pfd_coordiantes_config section."""
        self.set_key_value(["pfd_coordiantes_config", "coordinates_config_path"], coordinates_config_path)

    def set_pdf_coordinates_config_name(self, coordinates_config_name: str) -> None:
        """Set only the coordinates_config_name key in the pfd_coordiantes_config section."""
        self.set_key_value(["pfd_coordiantes_config", "coordinates_config_name"], coordinates_config_name)

    def set_full_pdf_coordinates_config_path(self, full_path: str) -> None:
        """
        Set the pfd_coordiantes_config section by parsing the provided full
        configuration path. Splits the full path into a directory part
        (coordinates_config_path) and a file name (coordinates_config_name)
        using the host's OS conventions.
        """
        import os
        config_path = os.path.dirname(full_path)
        config_path = self.ensure_trailing_sep(config_path)
        config_name = os.path.basename(full_path)
        self.set_pdf_coordinates_config(config_path, config_name)

    def get_default_settings(self) -> SettingsContentDataClass:
        """Return the *default_pdf_generation_data* section as a shallow dict."""
        dict_settings = self.get_key_value(["dafault_settings"]) or {}
        return SettingsContentDataClass(**dict_settings) if dict_settings else SettingsContentDataClass()

    # ------------------------- persistence ------------------------ #
    def save_to(self, destination: Union[str, Path]) -> None:
        """Persist current config to *destination*."""
        self.save(str(destination))
    
    @staticmethod
    def ensure_trailing_sep(path: str) -> str:  # noqa: D401
        """Ensure *path* ends with the host‑OS separator (``os.sep``).

        * If the string is empty → returned unchanged.
        * If it already ends with *any* separator, the trailing component is
          normalised to ``os.sep`` so that callers always get a consistent
          result, independent of the separator style they passed in.

        Examples
        --------
        >>> ProjectManager.ensure_trailing_sep("/var/data")
        '/var/data/'  # on POSIX
        >>> ProjectManager.ensure_trailing_sep(r"C:\\logs")
        'C:\\logs\\'  # on Windows
        """
        if not path:
            return path

        # already ends with a separator – replace if necessary
        if path.endswith(("/", "\\")):
            if path.endswith(os.sep):
                return path
            return path[:-1] + os.sep  # swap the last char

        # append the host‑separator
        return path + os.sep
    
    def load_project(self, json_path: Union[str, Path]) -> None:
        """Load project configuration from a JSON file."""
        self.reload_data(json_path)


    def load(self, path_or_url):
        ret = super().load(path_or_url)
        if ret:
            self.default_signal_loaded.emit(self.get_default_settings())
