"""Observer handling market data, settings, and generation utilities."""

from pathlib import Path
import shutil

from PySide6.QtCore import QObject, Slot, Signal
from PySide6.QtWidgets import QMessageBox

from display import BasicProgressTracker
from generator.file_generator import FileGenerator
from objects import FleatMarket

from .data_manager import DataManager
from .market_config_handler import MarketConfigHandler
from .pdf_display_config import PdfDisplayConfig
from utils.file_checks_utils import check_existing_files

class MarketObserver(QObject):

    status_info = Signal(str, str)
    data_manager_loaded = Signal(object)
    pdf_display_config_loaded = Signal(object)

    def __init__(self, market=None, json_path: str = ""):
        """

        Initialize the MarketObserver with a JSON path.
        :param json_path: Path to the JSON file.
        """
        QObject.__init__(self)
        self.market_config_handler: MarketConfigHandler = MarketConfigHandler()
        self.data_manager: DataManager = DataManager()
        self.pdf_display_config_loader: PdfDisplayConfig = PdfDisplayConfig()
        self.file_generator: FileGenerator = None
        self.fm: FleatMarket = None
        self._data_ready = False
        self._project_exists = False
        self._market = market
        self._project_dir = ""

    def apply_settings(self) -> None:
        """Set ``default_settings`` and inform the user."""
        if not self.data_manager.settings_available():
            default_settings = self.market_config_handler.get_default_settings()
            self.data_manager.set_new_settings(default_settings)
            self.status_info.emit(
                "WARNING",
                "Keine Settings gefunden. Default Einstellungen wurden geladen.",
            )

    def set_data_ready_satus(self, status: bool) -> None:
        """
        Set the data ready status.
        :param status: Boolean indicating if the data is ready.
        """
        self._data_ready = status

    def is_data_ready(self) -> bool:
        """
        Check if the data is ready.
        :return: True if the data is ready, False otherwise.
        """
        return self._data_ready

    def project_exists(self) -> bool:
        """
        Check if a project already exists.
        :return: True if a project exists, False otherwise.
        """
        return self._project_exists

    def set_project_exists(self, status: bool) -> None:
        """
        Set the project exists status.
        :param status: Boolean indicating if a project exists.
        """
        self._project_exists = status

    def set_project_dir(self, path: str | Path) -> None:
        """Remember the directory where the project is stored."""
        self._project_dir = str(path)

    def get_project_dir(self) -> str:
        """Return the directory of the current project."""
        return self._project_dir

    def init_project(self, export_path: str) -> None:
        """Initialise a new project based on an exported market file."""

        # reset the config handler to its defaults and point it to the export
        self.market_config_handler = MarketConfigHandler()
        self.market_config_handler.set_full_market_path(export_path)
        self._project_exists = True

    def load_local_market_project(self, json_path: str) -> bool:
        """
        Load a local market project from a JSON file.

        :param json_path: Path to the local JSON file.
        """
        ret = False
        if json_path:
            # Load the market configuration from the provided JSON path
            ret = self.market_config_handler.load(json_path)
            if ret:
                self._project_exists = True
                self._project_dir = str(Path(json_path).parent)
                market_json_path = self.market_config_handler.get_full_market_path()
                pdf_display_config = (
                    self.market_config_handler.get_full_pdf_coordinates_config_path()
                )
                # Initialize the DataManager with the market JSON path
                ret = self.data_manager.load(market_json_path)
                if ret:
                    self._on_loaded_success(f"Projekt geladen: {json_path}")
                else:
                    self.status_info.emit("ERROR", "Daten konnten nicht geladen werden")
                # Load the PDF display configuration
                pdf_ret = self.pdf_display_config_loader.load(pdf_display_config)
                if pdf_ret:
                    self.pdf_display_config_loaded.emit(self.pdf_display_config_loader)
                else:
                    if self._ask_for_default_pdf_config():
                        self._load_default_pdf_config(json_path)
                    else:
                        self.status_info.emit(
                            "ERROR", "Default pdf display config is not available now."
                        )

            else:
                self.status_info.emit(
                    "ERROR", "Projektkonfiguration konnte nicht geladen werden"
                )

        return ret

    def load_local_market_export(self, json_path: str) -> bool:
        """
        Load local JSON data.

        :param json_path: Path to the local JSON file.
        """
        ret = False
        if json_path:
            ret = self.data_manager.load(json_path)
            if ret:
                # send empty config, then finalise
                self.pdf_display_config_loaded.emit(self.pdf_display_config_loader)
                self._on_loaded_success(f"Export geladen: {json_path}")
            else:
                self.status_info.emit("ERROR", "Export konnte nicht geladen werden")

            self.market_config_handler.set_full_market_path(json_path)
            self._project_exists = True

            # self.file_generator = FileGenerator(self.data_manager)
        return ret

    @Slot()
    def setup_data_generation(self) -> None:

        self._data_ready = True
        self.fm: FleatMarket = FleatMarket()
        self.fm.load_sellers(self.data_manager.get_seller_as_list())
        self.fm.load_main_numbers(self.data_manager.get_main_number_as_list())
        self.file_generator = FileGenerator(self.fm)

    # Small helper to consolidate repeated success handling
    def _on_loaded_success(self, info_text: str) -> None:
        self.apply_settings()
        self.data_manager_loaded.emit(self.data_manager)
        self.setup_data_generation()
        self.status_info.emit("INFO", info_text)

    @Slot(str)
    def storage_path_changed(self, path: str) -> None:
        """Persist project when the PDF storage path changes."""

        self.market_config_handler.set_full_pdf_coordinates_config_path(path)
        if not self._project_dir:
            self._project_dir = str(Path(path).parent)
        from .market_facade import MarketFacade  # local import to avoid cycle
        MarketFacade().save_project(self._market, self._project_dir)

    def _ask_for_default_pdf_config(self) -> bool:
        """Prompt the user whether default PDF layout data should be loaded."""

        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Question)
        msg_box.setWindowTitle("PDF Konfiguration")
        msg_box.setText("Keine PDF Konfiguration gefunden. Default laden?")
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg_box.setDefaultButton(QMessageBox.Yes)
        return msg_box.exec() == QMessageBox.Yes

    def _load_default_pdf_config(self, project_path: str) -> None:
        """Copy default PDF layout files into the project directory."""

        project_dir = Path(project_path).parent
        default_dir = Path(__file__).resolve().parents[1] / "resource" / "default_data"

        cfg_src = default_dir / "pdf_display_config.json"
        pdf_src = default_dir / "Abholung_Template.pdf"

        cfg_dst = project_dir / "pdf_display_config.json"
        pdf_dst = project_dir / "Abholung_Template.pdf"

        _, proceed = check_existing_files(
            project_dir,
            [cfg_dst.name, pdf_dst.name],
            confirm=True,
        )
        if not proceed:
            return

        shutil.copy(cfg_src, cfg_dst)
        shutil.copy(pdf_src, pdf_dst)

        # update project configuration
        self.market_config_handler.set_full_pdf_coordinates_config_path(str(cfg_dst))
        self.market_config_handler.save_to(project_path)

        # update display config
        self.pdf_display_config_loader.load(str(cfg_dst))
        self.pdf_display_config_loader.set_full_pdf_path(str(pdf_dst))
        self.pdf_display_config_loader.set_output_path(str(project_dir))
        self.pdf_display_config_loader.set_output_name("Abholbestätigung.pdf")
        self.pdf_display_config_loader.save(str(cfg_dst))

        self.pdf_display_config_loaded.emit(self.pdf_display_config_loader)

    def get_data(self):
        return self.data_manager

    def connect_signals(self, market) -> None:
        self._market = market
        self.data_manager_loaded.connect(market.set_market_data)
        self.pdf_display_config_loaded.connect(market.set_pdf_config)

        market.pdf_display_storage_path_changed.connect(self.storage_path_changed)

    def prepare_pdf_generator(
        self, window
    ) -> tuple[FileGenerator | None, BasicProgressTracker | None]:
        """Return a configured ``FileGenerator`` for PDF generation."""
        if not self._data_ready:
            return None, None

        tracker = self._make_tracker(window)

        (
            template_path,
            outputpath,
            outputname,
            coordinates,
            dpi,
            pickup,
            font_family,
            font_size,
        ) = self._pdf_params()

        self.file_generator = FileGenerator(
            self.fm,
            output_interface=window,
            progress_tracker=tracker,
            output_path=outputpath,
            pdf_template_path_input=template_path,
            pdf_output_file_name=outputname,
            pdf_coordinates=coordinates,
            pdf_display_dpi=dpi,
            pickup_date=pickup,
            placeholder_font_family=font_family,
            placeholder_font_size=font_size,
        )
        return self.file_generator, tracker

    def prepare_seller_generator(
        self, window
    ) -> tuple[FileGenerator | None, BasicProgressTracker | None]:
        """Return a configured ``FileGenerator`` for seller data generation."""
        if not self._data_ready:
            return None, None

        tracker = self._make_tracker(window)

        output_path = self.pdf_display_config_loader.get_output_path()

        self.file_generator = FileGenerator(
            self.fm,
            output_interface=window,
            progress_tracker=tracker,
            output_path=output_path,
        )
        return self.file_generator, tracker

    def prepare_all_generator(
        self, window
    ) -> tuple[FileGenerator | None, BasicProgressTracker | None]:
        """Return a configured ``FileGenerator`` for full generation."""
        if not self._data_ready:
            return None, None

        tracker = self._make_tracker(window)

        (
            template_path,
            output_path,
            output_name,
            coordinates,
            dpi,
            pickup,
            font_family,
            font_size,
        ) = self._pdf_params()

        self.file_generator = FileGenerator(
            self.fm,
            output_interface=window,
            progress_tracker=tracker,
            output_path=output_path,
            pdf_template_path_input=template_path,
            pdf_output_file_name=output_name,
            pdf_coordinates=coordinates,
            pdf_display_dpi=dpi,
            pickup_date=pickup,
            placeholder_font_family=font_family,
            placeholder_font_size=font_size,
        )
        return self.file_generator, tracker

    # -------------------------- helpers --------------------------- #
    def _make_tracker(self, window) -> BasicProgressTracker:
        tracker = BasicProgressTracker()
        try:
            window.set_primary_tracker(tracker)
        except AttributeError:
            pass
        return tracker

    def _pdf_params(self):
        template_path = self.pdf_display_config_loader.get_full_pdf_path()
        output_path = self.pdf_display_config_loader.get_output_path()
        output_name = self.pdf_display_config_loader.get_output_name()
        coordinates = self.pdf_display_config_loader.convert_json_to_coordinate_list()
        dpi = self.pdf_display_config_loader.get_dpi()
        pickup_date = self.pdf_display_config_loader.get_pickup_date()
        pickup_time = self.pdf_display_config_loader.get_pickup_time()
        pickup = f"{pickup_date} {pickup_time}".strip()
        font_family = self.pdf_display_config_loader.get_placeholder_font_family()
        font_size = self.pdf_display_config_loader.get_placeholder_font_size()
        return (
            template_path,
            output_path,
            output_name,
            coordinates,
            dpi,
            pickup,
            font_family,
            font_size,
        )

    def generate_pdf_data(self, window) -> bool:
        """Generate PDF data using ``window`` for output and progress."""
        generator, tracker = self.prepare_pdf_generator(window)
        if generator is None or tracker is None:
            return False

        generator.create_pdf_data()
        self.status_info.emit(
            "ERROR" if tracker.has_error else "INFO",
            "PDF Daten generiert" if not tracker.has_error else "PDF Fehler",
        )
        return not tracker.has_error

    def generate_seller_data(self, window) -> bool:
        """Generate seller related data files using ``window`` for output."""
        generator, tracker = self.prepare_seller_generator(window)
        if generator is None or tracker is None:
            return False

        generator.create_seller_data()
        self.status_info.emit(
            "ERROR" if tracker.has_error else "INFO",
            (
                "Verkäuferdaten generiert"
                if not tracker.has_error
                else "Fehler bei Verkäuferdaten"
            ),
        )
        return not tracker.has_error

    def generate_all(self, window) -> bool:
        """Generate all data and PDF using ``window`` for output."""
        generator, tracker = self.prepare_all_generator(window)
        if generator is None or tracker is None:
            return False

        generator.create_all()
        self.status_info.emit(
            "ERROR" if tracker.has_error else "INFO",
            "Alle Daten erstellt" if not tracker.has_error else "Fehler bei Erstellung",
        )
        return not tracker.has_error

    def save_project(self, dir_path: str) -> bool:
        """Save the current project to ``dir_path``.

        The method writes the market data, PDF layout configuration and
        project configuration JSON into the specified directory. The
        project directory path and existence state are updated when the
        operation succeeds.
        """

        try:
            target_dir = Path(dir_path)
            target_dir.mkdir(parents=True, exist_ok=True)

            market_file = target_dir / (
                self.market_config_handler.get_market_name() or "market.json"
            )
            pdf_file = target_dir / (
                self.market_config_handler.get_pdf_coordinates_config_name()
                or "pdf_display_config.json"
            )
            project_file = target_dir / (
                self.market_config_handler.get_storage_file_name()
                or "project.project"
            )

            self.data_manager.json_data = self.data_manager.export_to_json()
            self.data_manager.save(str(market_file))

            self.pdf_display_config_loader.save(str(pdf_file))

            self.market_config_handler.set_full_market_path(str(market_file))
            self.market_config_handler.set_full_pdf_coordinates_config_path(
                str(pdf_file)
            )
            self.market_config_handler.save_to(str(project_file))

            pdf_path = self.pdf_display_config_loader.get_full_pdf_path()
            if pdf_path and Path(pdf_path).is_file():
                destination = target_dir / Path(pdf_path).name
                if Path(pdf_path).resolve() != destination.resolve():
                    shutil.copy(pdf_path, destination)
                self.pdf_display_config_loader.set_full_pdf_path(str(destination))

            self.set_project_dir(dir_path)
            self.set_project_exists(True)

            self.status_info.emit("INFO", f"Projekt gespeichert: {project_file}")
            return True
        except Exception as err:  # pragma: no cover - runtime errors handled
            self.status_info.emit("ERROR", f"Fehler beim Speichern: {err}")
            return False


