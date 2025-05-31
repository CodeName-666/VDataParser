import copy
from pathlib import Path
from typing import Any, Dict, TYPE_CHECKING, Union

from .json_handler import JsonHandler
from .base_data import BaseDataMeta

if TYPE_CHECKING:  # pragma: no cover
    from log import CustomLogger  # noqa: F401





#   A *singleton*‑style wrapper around a project‑configuration JSON.  The class
#   inherits JSON file/URL convenience from :class:`JsonHandler` and the
#   singleton behaviour from :class:`BaseDataMeta`.  It exposes **explicit** getter
#   & setter *methods* (\*no properties\*) for all top‑level sections that are
#   relevant for everyday use#
#   Usage example
#   -------------
#   ```python
#   from project_manager import ProjectManage#
#   pm = ProjectManager(json_path_or_data=my_json_dict#
#   # database section
#   print(pm.get_database())               # {"url": "", "port": ""}
#   pm.set_database(url="https://db", port="5432"#
#   # market section
#   print(pm.get_market())                 # {"market_path": "", "market_name": ""}
#   pm.set_market("/path", "EU_Market"#
#   # PDF defaults
#    print(pm.get_pdf_template_info())      # {"pdf_path": "...", "pdf_name": "..."}
#    print(pm.get_pdf_coordinates())
#
#    pm.save_to("config.json")
#


class ProjectManager(JsonHandler, metaclass=BaseDataMeta):
    """Manage one project‑configuration JSON and expose convenience helpers."""

    # --------------------------- defaults --------------------------- #
    _DEFAULT_STRUCTURE: Dict[str, Any] = {
        "database": {"url": "", "port": ""},
        "market": {"market_path": "", "market_name": ""},
        "default_pdf_generation_data": {
            "template_info": {
                "pdf_path": "Abholung_Template.pdf",
                "pdf_name": "Abholung_Template.pdf",
            },
            "coordinates": {"boxPairs": [], "singleBoxes": []},
        },
    }

    # ------------------------ construction ------------------------- #
    def __init__(
        self,
        json_path_or_data: Union[str, Path, Dict[str, Any]] = "",
        logger: "CustomLogger" | None = None,
    ) -> None:
        """Create or retrieve the *singleton* instance.

        * ``json_path_or_data`` may be a path/URL *or* a Python ``dict``.
          Empty/omitted argument starts with the default skeleton so you can
          build the config programmatically.
        * ``logger`` optional :class:`log.CustomLogger` instance.
        """
        super().__init__(json_path_or_data or copy.deepcopy(
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

    def set_market(self, market_path: str, market_name: str) -> None:
        """Set the *market* subsection."""
        self.set_key_value(["market", "market_path"], market_path)
        self.set_key_value(["market", "market_name"], market_name)

    # --------------- PDF‑generation default getters -------------- #
    def get_pdf_template_info(self) -> Dict[str, str]:
        """Return ``default_pdf_generation_data.template_info``."""
        return self.get_key_value(["default_pdf_generation_data", "template_info"]) or {}

    def get_pdf_coordinates(self) -> Dict[str, Any]:
        """Return ``default_pdf_generation_data.coordinates``."""
        return self.get_key_value(["default_pdf_generation_data", "coordinates"]) or {}

    # -------------------------- boxes ----------------------------- #
    def add_box_pair(
        self,
        *,
        box_id: int,
        usr_label: str,
        nr_label: str,
        usr_box: Dict[str, Union[int, float]],
        nr_box: Dict[str, Union[int, float]],
    ) -> None:
        """Append a *boxPairs* entry to the configuration."""
        pair = {
            "id": box_id,
            "box1": {"label": usr_label, **usr_box},
            "box2": {"label": nr_label, **nr_box},
        }
        pairs: list = self.get_key_value([
            "default_pdf_generation_data",
            "coordinates",
            "boxPairs",
        ]) or []
        pairs.append(pair)
        self.set_key_value([
            "default_pdf_generation_data",
            "coordinates",
            "boxPairs",
        ], pairs)

    # ------------------------- persistence ------------------------ #
    def save_to(self, destination: Union[str, Path]) -> None:
        """Persist current config to *destination*."""
        self.save(str(destination))

