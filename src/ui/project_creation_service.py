from __future__ import annotations

"""Utility service for project creation dialogs and facade calls."""

from pathlib import Path
from typing import Any, Tuple

from PySide6.QtWidgets import QFileDialog, QMessageBox, QWidget

from data import MarketFacade
from ui.utils.file_checks import check_existing_files


class ProjectCreationService:
    """Service class handling project creation workflows.

    This class encapsulates user interactions required for creating new
    projects or projects from exports. It provides convenience methods to
    choose target directories, confirm overwriting of existing files and
    delegate the actual creation work to :class:`data.market_facade.MarketFacade`.
    """

    def __init__(self, parent: QWidget, facade: MarketFacade) -> None:
        """Initialise the service.

        Parameters
        ----------
        parent:
            Parent widget used for dialogs.
        facade:
            Facade instance used for project operations.
        """
        self._parent = parent
        self._facade = facade

    # ------------------------------------------------------------------
    # Helper dialogs
    # ------------------------------------------------------------------
    def _select_directory(self) -> str | None:
        """Ask the user to select a project directory."""
        return QFileDialog.getExistingDirectory(self._parent, "Projektordner wählen") or None

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def create_new_project(
        self,
        market,
        name: str,
        settings: Any | None = None,
        server_info: dict | None = None,
    ) -> bool:
        """Create a new local project after user confirmation.

        This method asks whether a local project should be created, lets the
        user choose a target directory and verifies whether important files
        already exist. If everything is accepted the facade's
        :func:`MarketFacade.create_new_project` method is invoked.

        Parameters
        ----------
        market:
            Target :class:`ui.market.Market` view.
        name:
            Desired project (and JSON) file name, without or with ``.json``.
        settings:
            Optional settings used for project initialisation.
        server_info:
            Optional server configuration to store in the project.

        Returns
        -------
        bool
            ``True`` if the project was created successfully, ``False`` otherwise.
        """
        reply = QMessageBox.question(
            self._parent,
            "Projekt anlegen",
            "Möchten Sie zusätzlich sofort ein lokales Projekt erstellen?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.Yes,
        )
        if reply != QMessageBox.Yes:
            return False

        chosen_dir = self._select_directory()
        if not chosen_dir:
            return False

        market_filename = name if name.lower().endswith(".json") else f"{name}.json"
        target_dir = Path(chosen_dir)
        _, proceed = check_existing_files(
            target_dir,
            [
                market_filename,
                "pdf_display_config.json",
                "project.project",
                "Abholung_Template.pdf",
            ],
            parent=self._parent,
            confirm=True,
        )
        if not proceed:
            return False

        return self._facade.create_new_project(
            market,
            chosen_dir,
            market_filename,
            settings=settings,
            server_info=server_info,
        )

    def create_project_from_export(
        self, market, export_path: str
    ) -> Tuple[bool, str | None]:
        """Create a project using an existing export file.

        The user is asked to select a target directory and confirm
        overwriting if the export file already exists in the chosen
        directory. On success the facade's
        :func:`MarketFacade.create_project_from_export` is used and the
        resulting project path is returned.

        Parameters
        ----------
        market:
            Target :class:`ui.market.Market` view.
        export_path:
            Path to the export JSON file.

        Returns
        -------
        tuple[bool, str | None]
            ``(True, path)`` on success where ``path`` points to the moved
            export file. ``(False, None)`` otherwise.
        """
        chosen_dir = self._select_directory()
        if not chosen_dir:
            return False, None

        export_file = Path(export_path)
        _, proceed = check_existing_files(
            chosen_dir,
            [export_file.name],
            parent=self._parent,
            confirm=True,
        )
        if not proceed:
            return False, None

        ok, target = self._facade.create_project_from_export(
            market, export_path, chosen_dir
        )
        if ok and target:
            return True, str(Path(target) / export_file.name)
        return False, None
