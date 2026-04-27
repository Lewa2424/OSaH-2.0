from pathlib import Path

from PySide6.QtCore import QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import QFileDialog, QHBoxLayout, QLineEdit, QPushButton, QScrollArea, QVBoxLayout, QWidget
from PySide6.QtCore import QObject

from osah.application.services.create_news_source import create_news_source
from osah.application.services.delete_news_source import delete_news_source
from osah.application.services.load_latest_employee_import_review import load_latest_employee_import_review
from osah.application.services.load_system_settings_workspace import load_system_settings_workspace
from osah.application.services.save_mail_settings import save_mail_settings
from osah.application.services.save_news_refresh_time import save_news_refresh_time
from osah.application.services.save_system_behavior_settings import save_system_behavior_settings
from osah.application.services.toggle_news_source_activity import toggle_news_source_activity
from osah.domain.entities.access_role import AccessRole
from osah.domain.entities.mail_settings import MailSettings
from osah.domain.entities.news_source_kind import NewsSourceKind
from osah.ui.qt.components.form_feedback_label import FormFeedbackLabel
from osah.ui.qt.components.read_only_banner import ReadOnlyBanner
from osah.ui.qt.components.section_header import SectionHeader
from osah.ui.qt.components.task_progress_widget import TaskProgressWidget
from osah.ui.qt.design.tokens import SPACING
from osah.ui.qt.screens.settings.backup_settings_panel import BackupSettingsPanel
from osah.ui.qt.screens.settings.mail_settings_panel import MailSettingsPanel
from osah.ui.qt.screens.settings.news_sources_settings_panel import NewsSourcesSettingsPanel
from osah.ui.qt.screens.settings.operations_settings_panel import OperationsSettingsPanel
from osah.ui.qt.screens.settings.security_settings_panel import SecuritySettingsPanel
from osah.ui.qt.screens.settings.settings_section_card import SettingsSectionCard
from osah.ui.qt.workers.backup_create_worker import BackupCreateWorker
from osah.ui.qt.workers.import_worker import ImportWorker
from osah.ui.qt.workers.news_refresh_worker import NewsRefreshWorker
from osah.ui.qt.workers.restore_backup_worker import RestoreBackupWorker
from osah.ui.qt.workers.worker_task_controller import WorkerTaskController


class SettingsScreen(QWidget):
    """Settings command center with non-blocking heavy service operations."""

    def __init__(self, database_path: Path, access_role: AccessRole) -> None:
        super().__init__()
        self._database_path = database_path
        self._access_role = access_role
        self._read_only = access_role != AccessRole.INSPECTOR
        self._workspace = load_system_settings_workspace(database_path)
        self._active_task_name: str | None = None

        self._task_controller = WorkerTaskController()
        self._task_controller.started.connect(self._on_task_started)
        self._task_controller.progress.connect(self._on_task_progress)
        self._task_controller.success.connect(self._on_task_success)
        self._task_controller.error.connect(self._on_task_error)
        self._task_controller.finished.connect(self._on_task_finished)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(SPACING["xl"], SPACING["lg"], SPACING["xl"], SPACING["lg"])
        layout.setSpacing(SPACING["lg"])

        self._section_header = SectionHeader(
            "Налаштування",
            "Командний центр конфігурації системи без змішування внутрішнього та зовнішнього контурів.",
        )
        layout.addWidget(self._section_header)

        if self._read_only:
            layout.addWidget(ReadOnlyBanner())

        self._feedback = FormFeedbackLabel()
        layout.addWidget(self._feedback)

        self._task_progress = TaskProgressWidget()
        layout.addWidget(self._task_progress)

        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._content_widget = QWidget()
        self._content_layout = QVBoxLayout(self._content_widget)
        self._content_layout.setContentsMargins(0, 0, 0, 0)
        self._content_layout.setSpacing(SPACING["md"])
        self._scroll.setWidget(self._content_widget)
        layout.addWidget(self._scroll, stretch=1)

        self._operations_panel: OperationsSettingsPanel | None = None
        self._rebuild_sections()

    # ###### ПЕРЕБУДОВА СЕКЦІЙ ЕКРАНУ / REBUILD SETTINGS SECTIONS ######
    def _rebuild_sections(self) -> None:
        """Rebuilds settings section cards from current workspace."""

        while self._content_layout.count():
            item = self._content_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

        self._workspace = load_system_settings_workspace(self._database_path)
        self._content_layout.addWidget(SecuritySettingsPanel(self._workspace.security_profile, self._access_role))

        mail_panel = MailSettingsPanel(self._workspace.mail_settings, self._read_only)
        mail_panel.save_requested.connect(self._save_mail_settings)
        self._content_layout.addWidget(mail_panel)

        sources_panel = NewsSourcesSettingsPanel(
            self._workspace.news_sources,
            self._read_only,
            news_refresh_time=self._workspace.news_refresh_time,
        )
        sources_panel.source_created.connect(self._create_news_source)
        sources_panel.source_toggled.connect(self._toggle_source_activity)
        sources_panel.sources_deleted.connect(self._delete_news_sources)
        sources_panel.refresh_now_requested.connect(self._start_news_refresh)
        sources_panel.refresh_time_saved.connect(self._save_news_refresh_schedule)
        self._content_layout.addWidget(sources_panel)

        backup_panel = BackupSettingsPanel(
            backup_directory_path=self._workspace.backup_directory_path,
            snapshot_count=self._workspace.backup_snapshot_count,
            backup_auto_enabled=self._workspace.backup_auto_enabled,
            backup_max_copies=self._workspace.backup_max_copies,
            read_only=self._read_only,
        )
        backup_panel.save_requested.connect(self._save_backup_preferences)
        backup_panel.open_backup_requested.connect(self._open_backup_directory)
        self._content_layout.addWidget(backup_panel)

        self._operations_panel = OperationsSettingsPanel(read_only=self._read_only)
        self._operations_panel.create_backup_requested.connect(self._start_create_backup)
        self._operations_panel.restore_backup_requested.connect(self._start_restore_backup)
        self._operations_panel.create_import_batch_requested.connect(self._start_create_import_batch)
        self._operations_panel.apply_latest_import_requested.connect(self._start_apply_latest_import_batch)
        self._content_layout.addWidget(self._operations_panel)

        self._content_layout.addWidget(self._build_behavior_panel())
        self._content_layout.addWidget(self._build_service_info_panel())
        self._content_layout.addStretch()

    # ###### ПАНЕЛЬ ПОВЕДІНКИ СИСТЕМИ / BUILD BEHAVIOR PANEL ######
    def _build_behavior_panel(self) -> QWidget:
        """Builds behavior settings card."""

        from PySide6.QtWidgets import QLabel

        card = SettingsSectionCard()
        layout = card.content_layout()
        title = QLabel("Поведінка системи")
        title.setProperty("role", "section_title")
        layout.addWidget(title)

        row = QHBoxLayout()
        self._ppe_warning_days = QLineEdit(str(self._workspace.ppe_warning_days))
        self._ppe_warning_days.setPlaceholderText("Поріг попередження ЗІЗ (днів)")
        self._ppe_warning_days.setReadOnly(self._read_only)
        row.addWidget(self._ppe_warning_days)
        save_button = QPushButton("Зберегти пороги")
        save_button.setProperty("variant", "secondary")
        save_button.setEnabled(not self._read_only)
        save_button.clicked.connect(self._save_behavior_settings)
        row.addWidget(save_button)
        layout.addLayout(row)
        return card

    # ###### ПАНЕЛЬ СЛУЖБОВОЇ ІНФОРМАЦІЇ / BUILD SERVICE INFO PANEL ######
    def _build_service_info_panel(self) -> QWidget:
        """Builds service information card."""

        from PySide6.QtWidgets import QLabel

        card = SettingsSectionCard()
        layout = card.content_layout()
        title = QLabel("Службова інформація")
        title.setProperty("role", "section_title")
        layout.addWidget(title)
        layout.addWidget(QLabel(f"Версія: {self._workspace.app_version}"))
        layout.addWidget(QLabel(f"База даних: {self._workspace.database_path}"))
        layout.addWidget(QLabel(f"Каталог даних: {self._workspace.data_directory_path}"))
        init_text = "готово" if self._workspace.is_initialized else "не готово"
        layout.addWidget(QLabel(f"Стан ініціалізації: {init_text}"))
        return card

    # ###### ЗБЕРЕЖЕННЯ ПОШТОВИХ НАЛАШТУВАНЬ / SAVE MAIL SETTINGS ######
    def _save_mail_settings(self, mail_settings: MailSettings) -> None:
        """Saves mail settings through application service."""

        if self._read_only:
            self._feedback.show_error("Режим read-only: зміни недоступні.")
            return
        try:
            save_mail_settings(self._database_path, mail_settings)
        except Exception as error:  # noqa: BLE001
            self._feedback.show_error(f"Не вдалося зберегти пошту: {error}")
            return
        self._feedback.show_success("Поштові налаштування збережено.")
        self._rebuild_sections()

    # ###### СТВОРЕННЯ ДЖЕРЕЛА НОВИН / CREATE NEWS SOURCE ######
    def _create_news_source(self, source_name: str, source_url: str, source_kind_value: str) -> None:
        """Creates trusted source through application service."""

        if self._read_only:
            self._feedback.show_error("Режим read-only: зміни недоступні.")
            return
        try:
            create_news_source(self._database_path, source_name, source_url, NewsSourceKind(source_kind_value))
        except Exception as error:  # noqa: BLE001
            self._feedback.show_error(f"Не вдалося створити джерело: {error}")
            return
        self._feedback.show_success("Джерело додано.")
        self._rebuild_sections()

    # ###### ПЕРЕМИКАННЯ АКТИВНОСТІ ДЖЕРЕЛА / TOGGLE SOURCE ACTIVITY ######
    def _toggle_source_activity(self, source_id: int, is_active: bool) -> None:
        """Toggles source activity through application service."""

        if self._read_only:
            self._feedback.show_error("Режим read-only: зміни недоступні.")
            self._rebuild_sections()
            return
        try:
            toggle_news_source_activity(self._database_path, source_id, is_active)
        except Exception as error:  # noqa: BLE001
            self._feedback.show_error(f"Не вдалося оновити джерело: {error}")
            self._rebuild_sections()
            return
        self._feedback.show_success("Стан джерела оновлено.")
        self._rebuild_sections()

    # ###### ВИДАЛЕННЯ ДЖЕРЕЛ НОВИН / DELETE NEWS SOURCES ######
    def _delete_news_sources(self, source_ids: list) -> None:
        """Deletes selected trusted sources through application service."""

        if self._read_only:
            self._feedback.show_error("Режим read-only: зміни недоступні.")
            return
        errors: list[str] = []
        for source_id in source_ids:
            try:
                delete_news_source(self._database_path, source_id)
            except Exception as error:  # noqa: BLE001
                errors.append(str(error))
        if errors:
            self._feedback.show_error(f"Помилки при видаленні: {'; '.join(errors)}")
        else:
            self._feedback.show_success(f"Видалено джерел: {len(source_ids)}.")
        self._rebuild_sections()

    # ###### НЕГАЙНА ПЕРЕВІРКА НОВИН / START NEWS REFRESH NOW ######
    def _start_news_refresh(self) -> None:
        """Starts immediate news refresh in background."""

        self._start_task("news.refresh", NewsRefreshWorker(self._database_path))

    # ###### ЗБЕРЕЖЕННЯ РОЗКЛАДУ ПЕРЕВІРКИ / SAVE NEWS REFRESH SCHEDULE ######
    def _save_news_refresh_schedule(self, refresh_time: str) -> None:
        """Saves daily news refresh time through application service."""

        if self._read_only:
            self._feedback.show_error("Режим read-only: зміни недоступні.")
            return
        try:
            save_news_refresh_time(self._database_path, refresh_time)
        except Exception as error:  # noqa: BLE001
            self._feedback.show_error(f"Не вдалося зберегти розклад: {error}")
            return
        self._feedback.show_success(f"Розклад перевірки збережено: щодня о {refresh_time}.")
        self._rebuild_sections()

    # ###### ЗБЕРЕЖЕННЯ НАЛАШТУВАНЬ БЕКАПУ / SAVE BACKUP PREFERENCES ######
    def _save_backup_preferences(self, backup_auto_enabled: bool, backup_max_copies: int) -> None:
        """Saves backup-related preferences through behavior settings service."""

        self._save_behavior_settings(backup_auto_enabled=backup_auto_enabled, backup_max_copies=backup_max_copies)

    # ###### ЗБЕРЕЖЕННЯ ПОВЕДІНКОВИХ ПАРАМЕТРІВ / SAVE BEHAVIOR SETTINGS ######
    def _save_behavior_settings(
        self,
        backup_auto_enabled: bool | None = None,
        backup_max_copies: int | None = None,
    ) -> None:
        """Saves behavior settings with validation."""

        if self._read_only:
            self._feedback.show_error("Режим read-only: зміни недоступні.")
            return
        try:
            ppe_warning_days = int(self._ppe_warning_days.text() or str(self._workspace.ppe_warning_days))
            save_system_behavior_settings(
                self._database_path,
                ppe_warning_days=ppe_warning_days,
                backup_auto_enabled=backup_auto_enabled
                if backup_auto_enabled is not None
                else self._workspace.backup_auto_enabled,
                backup_max_copies=backup_max_copies
                if backup_max_copies is not None
                else self._workspace.backup_max_copies,
            )
        except Exception as error:  # noqa: BLE001
            self._feedback.show_error(f"Не вдалося зберегти параметри: {error}")
            return
        self._feedback.show_success("Поведінкові налаштування оновлено.")
        self._rebuild_sections()

    # ###### ВІДКРИТТЯ КАТАЛОГУ БЕКАПІВ / OPEN BACKUP DIRECTORY ######
    def _open_backup_directory(self) -> None:
        """Opens backup directory in file manager."""

        QDesktopServices.openUrl(QUrl.fromLocalFile(self._workspace.backup_directory_path))

    # ###### ЗАПУСК СТВОРЕННЯ БЕКАПУ / START BACKUP CREATE ######
    def _start_create_backup(self) -> None:
        """Starts manual backup creation in background."""

        self._start_task("backup.create_manual", BackupCreateWorker(self._database_path))

    # ###### ЗАПУСК ВІДНОВЛЕННЯ / START RESTORE ######
    def _start_restore_backup(self) -> None:
        """Starts restore operation from selected backup file in background."""

        selected_file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Оберіть файл резервної копії",
            self._workspace.backup_directory_path,
            "Backup files (*.sqlite3 *.db *.bak);;All files (*.*)",
        )
        if not selected_file_path:
            return
        self._start_task(
            "backup.restore",
            RestoreBackupWorker(self._database_path, Path(selected_file_path)),
        )

    # ###### ЗАПУСК ІМПОРТУ ЧЕРНЕТОК / START IMPORT DRAFT CREATION ######
    def _start_create_import_batch(self) -> None:
        """Starts import draft creation from selected file in background."""

        selected_file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Оберіть файл імпорту працівників",
            self._workspace.data_directory_path,
            "Supported files (*.json *.xlsx);;JSON (*.json);;Excel (*.xlsx)",
        )
        if not selected_file_path:
            return
        self._start_task(
            "import.create_batch",
            ImportWorker(
                database_path=self._database_path,
                operation_kind="create_batch",
                source_file_path=Path(selected_file_path),
            ),
        )

    # ###### ЗАПУСК ЗАСТОСУВАННЯ ПАРТІЇ ІМПОРТУ / START IMPORT BATCH APPLY ######
    def _start_apply_latest_import_batch(self) -> None:
        """Starts apply operation for latest import batch in background."""

        latest_batch_summary, _ = load_latest_employee_import_review(self._database_path)
        if latest_batch_summary is None:
            self._feedback.show_error("Немає доступної партії імпорту для застосування.")
            return
        if latest_batch_summary.applied_at:
            self._feedback.show_error("Останню партію імпорту вже застосовано.")
            return
        self._start_task(
            "import.apply_batch",
            ImportWorker(
                database_path=self._database_path,
                operation_kind="apply_batch",
                batch_id=latest_batch_summary.batch_id,
            ),
        )

    # ###### СТАРТ ФОНОВОЇ ОПЕРАЦІЇ / START BACKGROUND TASK ######
    def _start_task(self, task_name: str, worker: QObject) -> None:
        """Starts background worker and protects from double-run."""

        if self._read_only:
            self._feedback.show_error("Режим read-only: операція недоступна.")
            return
        self._active_task_name = task_name
        if not self._task_controller.start_worker(worker):
            self._feedback.show_error("Операція вже виконується. Дочекайтеся завершення.")
            self._active_task_name = None

    # ###### СТАРТ ФОНОВОЇ ЗАДАЧІ / BACKGROUND TASK START ######
    def _on_task_started(self) -> None:
        """Applies busy-state on task start."""

        self._task_progress.show_indeterminate("Запущено фонову операцію...")
        if self._operations_panel is not None:
            self._operations_panel.setEnabled(False)

    # ###### ПРОГРЕС ФОНОВОЇ ЗАДАЧІ / BACKGROUND TASK PROGRESS ######
    def _on_task_progress(self, progress_value: int, message_text: str) -> None:
        """Updates progress text/value for active heavy task."""

        self._task_progress.show_progress(message_text, progress_value)
        if self._operations_panel is not None:
            self._operations_panel.set_status_text(message_text)

    # ###### УСПІХ ФОНОВОЇ ЗАДАЧІ / BACKGROUND TASK SUCCESS ######
    def _on_task_success(self, payload: object) -> None:
        """Handles successful completion for each heavy operation."""

        if self._active_task_name == "backup.create_manual":
            if isinstance(payload, Path):
                self._feedback.show_success(f"Резервну копію створено: {payload}")
            else:
                self._feedback.show_success("Резервну копію створено.")
            self._rebuild_sections()
            return

        if self._active_task_name == "backup.restore":
            if isinstance(payload, dict):
                restored_from = payload.get("restored_from")
                safety_copy = payload.get("safety_copy")
                self._feedback.show_success(
                    f"Відновлення завершено: {restored_from}. Страхувальна копія: {safety_copy}."
                )
            else:
                self._feedback.show_success("Відновлення завершено.")
            self._rebuild_sections()
            return

        if self._active_task_name == "import.create_batch":
            if isinstance(payload, dict):
                self._feedback.show_success(f"Партію імпорту #{payload.get('batch_id')} створено.")
            else:
                self._feedback.show_success("Партію імпорту створено.")
            return

        if self._active_task_name == "import.apply_batch":
            if isinstance(payload, dict):
                self._feedback.show_success(f"Партію імпорту #{payload.get('batch_id')} застосовано.")
            else:
                self._feedback.show_success("Партію імпорту застосовано.")
            self._rebuild_sections()
            return

        if self._active_task_name == "news.refresh":
            count = payload if isinstance(payload, int) else 0
            self._feedback.show_success(f"Перевірку завершено. Знайдено нових матеріалів: {count}.")
            self._rebuild_sections()
            return

        self._feedback.show_success("Фонову операцію завершено.")

    # ###### ПОМИЛКА ФОНОВОЇ ЗАДАЧІ / BACKGROUND TASK ERROR ######
    def _on_task_error(self, message_text: str) -> None:
        """Shows background task error text."""

        self._feedback.show_error(message_text)

    # ###### ФІНАЛ ФОНОВОЇ ЗАДАЧІ / BACKGROUND TASK FINISH ######
    def _on_task_finished(self) -> None:
        """Resets busy-state after task completion."""

        self._task_progress.hide_state()
        if self._operations_panel is not None:
            self._operations_panel.setEnabled(True)
            self._operations_panel.set_status_text(
                "Тут запускаються важкі операції у фоновому режимі без блокування інтерфейсу."
            )
        self._active_task_name = None
