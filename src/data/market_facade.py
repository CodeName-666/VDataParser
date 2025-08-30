"""High level facade combining various market related components."""

import shutil
import tempfile
from pathlib import Path
from typing import List, Callable

from PySide6.QtCore import QObject, Slot, Signal, QEventLoop

from backend import MySQLInterface
from backend.advanced_db_manager_thread import AdvancedDBManagerThread
from objects import SettingsContentDataClass


from .market_observer import MarketObserver
from .singleton_meta import SingletonMeta


class MarketFacade(QObject, metaclass=SingletonMeta):
    """
    A facade for market operations, providing a simplified interface to interact with market data.
    """

    status_info = Signal(str, str)
    db_connected = Signal()
    db_disconnected = Signal()
    db_connecting = Signal()

    def __init__(self):

        QObject.__init__(self)

        self._market_list: List = []
        self._db_thread: AdvancedDBManagerThread | None = None

    def connect_to_mysql_server(
        self, host: str, port: int, user: str, password: str
    ) -> bool:
        """Establish a connection to a MySQL server using a background thread.

        Parameters
        ----------
        host:
            Server address of the MySQL instance.
        port:
            Port number of the MySQL server.
        user:
            Username used for authentication.
        password:
            Password for the given user.

        Returns
        -------
        bool
            ``True`` if the connection thread was started successfully,
            ``False`` otherwise.
        """

        if self._db_thread is not None:
            self.status_info.emit(
                "INFO", f"Server bereits verbunden: {host}:{port}"
            )
            return True

        try:
            server_if = MySQLInterface(
                host=host, port=port, user=user, password=password
            )
            self.connect_to_db(server_if)
            self.status_info.emit(
                "INFO", f"Server verbunden: {host}:{port}"
            )
            return self._db_thread is not None
        except Exception as exc:  # pragma: no cover - runtime path
            self.status_info.emit(
                "ERROR", f"Verbindung fehlgeschlagen: {exc}"
            )
            self.db_disconnected.emit()
            return False

    def list_databases(self, prefix: str | None = None) -> list[str]:
        """Return a list of databases available on the connected server.

        Parameters
        ----------
        prefix:
            Optional prefix to filter database names.

        Returns
        -------
        list[str]
            A list of database names. An empty list is returned if the
            database thread is not running or an error occurred.
        """

        if self._db_thread is None:
            self.status_info.emit(
                "ERROR", "DB-Thread konnte nicht gestartet werden"
            )
            return []

        databases: list[str] = []
        loop = QEventLoop()

        def _handle_finished(result: object) -> None:  # pragma: no cover - Qt slot
            nonlocal databases
            databases = result
            loop.quit()

        def _handle_error(exc: Exception) -> None:  # pragma: no cover - Qt slot
            self.status_info.emit(
                "ERROR", f"Verbindung fehlgeschlagen: {exc}"
            )
            self.db_disconnected.emit()
            loop.quit()

        db_thread = self._db_thread
        db_thread.task_finished.connect(_handle_finished)
        db_thread.task_error.connect(_handle_error)
        db_thread.list_databases(prefix)
        loop.exec()
        db_thread.task_finished.disconnect(_handle_finished)
        db_thread.task_error.disconnect(_handle_error)

        return databases

    def select_database(self, name: str) -> bool:
        """Select a database on the connected server.

        Parameters
        ----------
        name:
            Name of the database to select.

        Returns
        -------
        bool
            ``True`` if the task was queued successfully, ``False`` otherwise.
        """

        if self._db_thread is None:
            self.status_info.emit("ERROR", "Keine Serververbindung")
            return False

        self._db_thread.add_task(lambda m: m.connect_to_db(name))
        return True

    def download_market_export(
        self, info: dict, output_path: str, on_finished: Callable[[bool], None]
    ) -> bool:
        """Export a MySQL database to ``output_path`` asynchronously.

        Parameters
        ----------
        info:
            Connection parameters including ``host``, ``port``, ``user``,
            ``password`` and ``database``.
        output_path:
            Destination file path where the JSON export will be written.
        on_finished:
            Callback invoked with ``True`` on success and ``False`` on failure.

        Returns
        -------
        bool
            ``True`` if the export task was started, ``False`` otherwise.
        """

        host = info.get("host")
        port = info.get("port")
        user = info.get("user")
        password = info.get("password")
        database = info.get("database")

        if not database:
            self.status_info.emit("ERROR", "Keine Datenbank angegeben")
            on_finished(False)
            return False

        try:
            if self._db_thread is None:
                if not self.connect_to_mysql_server(host, port, user, password):
                    on_finished(False)
                    return False

            if not self.select_database(database):
                on_finished(False)
                return False

            db_thread = self._db_thread
            pending = True

            def _handle_finished(_result: object) -> None:  # pragma: no cover - Qt slot
                nonlocal pending
                if pending:
                    pending = False
                    return
                db_thread.task_finished.disconnect(_handle_finished)
                db_thread.task_error.disconnect(_handle_error)
                on_finished(True)

            def _handle_error(exc: Exception) -> None:  # pragma: no cover - Qt slot
                self.status_info.emit(
                    "ERROR", f"Fehler beim Laden der Datenbank: {exc}"
                )
                db_thread.task_finished.disconnect(_handle_finished)
                db_thread.task_error.disconnect(_handle_error)
                on_finished(False)

            db_thread.task_finished.connect(_handle_finished)
            db_thread.task_error.connect(_handle_error)
            db_thread.add_task(lambda m: m.export_to_custom_json(output_path))
            return True
        except Exception as e:  # pragma: no cover - error path
            self.status_info.emit(
                "ERROR", f"Fehler beim Starten des DB-Threads: {e}"
            )
            on_finished(False)
            return False

    def load_online_market(self, market, info: dict) -> bool:
        """Load market data from a MySQL database.

        This helper uses :func:`download_market_export` to export the selected
        database to a temporary file and then loads it into ``market``. The
        caller is still responsible for switching views.
        """

        database = info.get("database")
        host = info.get("host")
        port = info.get("port")

        with tempfile.NamedTemporaryFile(delete=False, suffix=".json") as tmp:
            tmp_path = tmp.name

        def _post(success: bool) -> None:  # pragma: no cover - Qt slot
            if success:
                new_observer = self.create_observer(market)
                new_observer.connect_signals(market)
                ret_local = new_observer.load_local_market_export(tmp_path)
                if ret_local:
                    self.status_info.emit(
                        "INFO", f"Online-Datenbank geladen: {database}@{host}:{port}"
                    )
                else:
                    self.status_info.emit(
                        "ERROR", "Daten konnten nicht geladen werden"
                    )
            else:
                self.status_info.emit(
                    "ERROR", "Daten konnten nicht geladen werden"
                )
            if Path(tmp_path).exists():
                try:
                    Path(tmp_path).unlink()
                except OSError:
                    pass

        return self.download_market_export(info, tmp_path, _post)

    def connect_to_db(self, db_interface) -> None:
        """Start a background thread managing ``db_interface``."""
        if self._db_thread is not None:
            return
        db_thread = AdvancedDBManagerThread(db_interface)
        self._db_thread = db_thread
        db_thread.connected.connect(self.db_connected)
        db_thread.disconnected.connect(self.db_disconnected)
        db_thread.connecting.connect(self.db_connecting)
        db_thread.start()

    def disconnect_from_db(self) -> None:
        """Stop the background database thread if running."""
        if self._db_thread is None:
            return
        self._db_thread.stop()
        self._db_thread = None

    def load_local_market_porject(self, market, json_path: str) -> bool:
        """
        Load a local market project from a JSON file.

        :param json_path: Path to the local JSON file.
        """

        new_observer = self.create_observer(market, json_path)
        new_observer.connect_signals(market)
        ret = new_observer.load_local_market_project(json_path)

        return ret

    def load_local_market_export(self, market, json_path: str) -> bool:
        """Load market data from a local JSON export.

        Parameters
        ----------
        market:
            Target :class:`Market` view.
        json_path:
            Path to the local JSON export file.
        """
        new_observer = self.create_observer(market)
        new_observer.connect_signals(market)
        return new_observer.load_local_market_export(json_path)

    def market_already_exists(self, market) -> bool:
        market = next(
            ((mk, obs)[0] for mk, obs in self._market_list if mk == market), None
        )
        if market is not None:
            return True
        return False

    def get_observer(self, market):
        """
        Retrieve the observer for the specified market.

        :param market: The market instance to observe.
        :return: The observer instance for the market, or None if not found.
        """
        for mk, observer in self._market_list:
            if mk == market:
                return observer
        return None

    def create_observer(self, market, json_path="") -> MarketObserver:
        """
        Create an observer for the specified market.

        :param market: The market instance to observe.
        :return: An observer instance for the market.
        """

        if not self.market_already_exists(market):
            observer = MarketObserver()
            observer.status_info.connect(self.status_info)
            self._market_list.append((market, observer))
        else:
            observer = self.get_observer(market)
        return observer

    def create_project_from_export(
        self, market, export_path: str, target_dir: str
    ) -> tuple[bool, Path | None]:
        """Create a project configuration from a previously exported market.

        Parameters
        ----------
        market:
            Target :class:`Market` view.
        export_path:
            Path to the existing export file.
        target_dir:
            Directory where the new project should be created. The directory must
            be provided by the caller and will be created if it does not exist.

        Returns
        -------
        tuple[bool, Path | None]
            ``(True, Path)`` on success where ``Path`` points to the project
            directory. ``(False, None)`` if an error occurred.
        """

        observer: MarketObserver = self.get_observer(market)
        # Ensure an observer exists for ``market`` so a project can be
        # initialised even if no data was loaded beforehand.
        if not observer:
            observer = self.create_observer(market)

        if not target_dir:
            raise ValueError("target_dir must be provided")

        try:
            target = Path(target_dir)
            target.mkdir(parents=True, exist_ok=True)
            export_file = Path(export_path)
            new_export = target / export_file.name
            shutil.move(str(export_file), new_export)
        except Exception as err:
            self.status_info.emit(
                "ERROR", f"Export konnte nicht verschoben werden: {err}"
            )
            return False, None

        try:
            observer.init_project(str(new_export))
            project_name = Path(new_export).stem + ".project"
            project_file = target / project_name
            observer.market_config_handler.save_to(str(project_file))
        except Exception as err:
            self.status_info.emit(
                "ERROR", f"Projekt konnte nicht erstellt werden: {err}"
            )
            return False, None

        observer.set_project_dir(str(target))
        observer.set_project_exists(True)

        if observer._ask_for_default_pdf_config():
            observer._load_default_pdf_config(str(project_file))

        return True, target

    def prepare_pdf_generator(self, market, window):
        """Return a generator for PDF creation."""
        observer = self.get_observer(market)
        if not observer:
            self.status_info.emit("ERROR", "Kein Observer gefunden")
            return None, None
        return observer.prepare_pdf_generator(window)

    def prepare_seller_generator(self, market, window):
        """Return a generator for seller data creation."""
        observer = self.get_observer(market)
        if not observer:
            self.status_info.emit("ERROR", "Kein Observer gefunden")
            return None, None
        return observer.prepare_seller_generator(window)

    def prepare_all_generator(self, market, window):
        """Return a generator for full data creation."""
        observer = self.get_observer(market)
        if not observer:
            self.status_info.emit("ERROR", "Kein Observer gefunden")
            return None, None
        return observer.prepare_all_generator(window)

    @Slot(object, object)
    def create_pdf_data(self, market, window) -> bool:
        """
        Create PDF data for the specified market.

        :param market: The market instance for which to create PDF data.
        """
        observer = self.get_observer(market)
        if not observer:
            self.status_info.emit("ERROR", "Kein Observer gefunden")
            return False
        try:
            ok = observer.generate_pdf_data(window)
            self.status_info.emit(
                "INFO" if ok else "ERROR", "PDF Daten generiert" if ok else "PDF Fehler"
            )
            return ok
        except Exception as err:  # pragma: no cover - runtime errors handled
            self.status_info.emit("ERROR", str(err))
            return False

    @Slot(object, object)
    def create_seller_data(self, market, window) -> bool:
        """Create seller related data files for the specified market."""
        observer = self.get_observer(market)
        if not observer:
            self.status_info.emit("ERROR", "Kein Observer gefunden")
            return False
        try:
            ok = observer.generate_seller_data(window)
            self.status_info.emit(
                "INFO" if ok else "ERROR",
                "Verkäuferdaten generiert" if ok else "Fehler bei Verkäuferdaten",
            )
            return ok
        except Exception as err:  # pragma: no cover - runtime errors handled
            self.status_info.emit("ERROR", str(err))
            return False

    @Slot(object)
    def create_market_data(self, market) -> None:
        """
        Create market data for the specified market.

        :param market: The market instance for which to create data.
        """
        observer = self.get_observer(market)
        if not observer:
            self.status_info.emit("ERROR", "Market observer not found")
            return
        try:
            market.set_data(observer.get_data())
            self.status_info.emit("INFO", "Marktdaten generiert")
        except Exception as err:  # pragma: no cover - runtime errors handled
            self.status_info.emit("ERROR", str(err))

    @Slot(object, object)
    def create_all_data(self, market, window) -> bool:
        """
        Create all data for the specified market.

        :param market: The market instance for which to create all data.
        """
        observer = self.get_observer(market)
        if not observer:
            self.status_info.emit("ERROR", "Kein Observer gefunden")
            return False
        try:
            if observer.file_generator:
                ok = observer.generate_all(window)
                self.status_info.emit(
                    "INFO" if ok else "ERROR",
                    "Alle Daten erstellt" if ok else "Fehler bei Erstellung",
                )
                return ok
            else:
                raise RuntimeError("FileGenerator nicht bereit")
        except Exception as err:  # pragma: no cover - runtime errors handled
            self.status_info.emit("ERROR", str(err))
            return False

    def is_project(self, market) -> bool:
        """
        Check if a project exists for the specified market.

        :param market: The market instance to check.
        :return: True if a project exists, False otherwise.
        """
        observer: MarketObserver = self.get_observer(market)
        if observer:
            return observer.project_exists()
        return False

    def get_project_dir(self, market) -> str:
        """Return the directory path of the current project."""
        observer: MarketObserver = self.get_observer(market)
        return observer.get_project_dir() if observer else ""

    @Slot(object, str)
    def save_project(self, market, dir_path: str) -> bool:
        """Delegate project saving to the corresponding observer."""

        observer = self.get_observer(market)
        if not observer:
            self.status_info.emit("ERROR", "Kein Observer gefunden")
            return False

        ok = observer.save_project(dir_path)
        if ok:
            self.status_info.emit("INFO", "Projekt gespeichert")
        else:
            self.status_info.emit("ERROR", "Fehler beim Speichern")
        return ok

    # ------------------------------------------------------------------
    # Project creation from scratch (no existing export)
    # ------------------------------------------------------------------
    def create_new_project(
        self,
        market,
        target_dir: str,
        market_filename: str,
        settings: SettingsContentDataClass | None = None,
        server_info: dict | None = None,
    ) -> bool:
        """Create a new local project with the provided settings and server info.

        This will:
        - Ensure an observer exists for ``market``
        - Apply ``settings`` to the data manager (so they're exported to market JSON)
        - Set market path/name and database fields
        - Persist the project (market JSON, pdf display config, project file)
        - Copy default PDF configuration and template into the project directory

        Returns True on success, False otherwise.
        """
        observer = self.get_observer(market) or self.create_observer(market)
        try:
            # 1) Configure market path + name
            target = Path(target_dir)
            target.mkdir(parents=True, exist_ok=True)
            observer.market_config_handler.set_market(
                str(target) + ("/" if not str(target).endswith(("/", "\\")) else ""),
                market_filename,
            )

            # 2) Apply settings to be exported in the JSON
            if settings is not None:
                try:
                    observer.data_manager.set_new_settings(settings)
                except Exception:
                    pass

            # 3) Store server connection info in project config
            if server_info:
                try:
                    mch = observer.market_config_handler
                    mch.set_database(
                        server_info.get("host", ""),
                        str(server_info.get("port", "")),
                    )
                    mch.set_db_credentials(
                        server_info.get("database", ""),
                        server_info.get("user", ""),
                    )
                except Exception:
                    pass

            # 4) Persist project (writes market.json, pdf config, project.project)
            if not observer.save_project(str(target)):
                return False

            # 5) Ensure default PDF config/template exist and project references them
            try:
                project_file = str(target / "project.project")
                observer._load_default_pdf_config(project_file)
            except Exception:
                pass

            # 6) Prepare in-memory data for UI/generators
            try:
                observer.setup_data_generation()
            except Exception:
                pass

            self.status_info.emit("INFO", f"Neues Projekt erstellt: {target}")
            return True
        except Exception as err:  # pragma: no cover - runtime errors handled
            self.status_info.emit("ERROR", f"Projektanlage fehlgeschlagen: {err}")
            return False
