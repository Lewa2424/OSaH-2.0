from pathlib import Path

from PySide6.QtCore import QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from osah.application.services.create_news_source import create_news_source
from osah.application.services.load_system_settings_workspace import load_system_settings_workspace
from osah.application.services.save_mail_settings import save_mail_settings
from osah.application.services.save_system_behavior_settings import save_system_behavior_settings
from osah.application.services.toggle_news_source_activity import toggle_news_source_activity
from osah.domain.entities.access_role import AccessRole
from osah.domain.entities.mail_settings import MailSettings
from osah.domain.entities.news_source_kind import NewsSourceKind
from osah.domain.entities.settings_workspace import SettingsWorkspace
from osah.ui.qt.components.form_feedback_label import FormFeedbackLabel
from osah.ui.qt.design.tokens import COLOR, SPACING
from osah.ui.qt.screens.settings.backup_settings_panel import BackupSettingsPanel
from osah.ui.qt.screens.settings.mail_settings_panel import MailSettingsPanel
from osah.ui.qt.screens.settings.news_sources_settings_panel import NewsSourcesSettingsPanel
from osah.ui.qt.screens.settings.security_settings_panel import SecuritySettingsPanel
from osah.ui.qt.screens.settings.settings_section_card import SettingsSectionCard


class SettingsScreen(QWidget):
    """Full settings screen for configuration and service controls."""

    def __init__(self, database_path: Path, access_role: AccessRole) -> None:
        super().__init__()
        self._database_path = database_path
        self._access_role = access_role
        self._workspace = load_system_settings_workspace(database_path)
        self._read_only = access_role != AccessRole.INSPECTOR

        layout = QVBoxLayout(self)
        layout.setContentsMargins(SPACING["xl"], SPACING["lg"], SPACING["xl"], SPACING["lg"])
        layout.setSpacing(SPACING["lg"])

        title = QLabel("Налаштування")
        title.setStyleSheet("font-size: 22px; font-weight: 900;")
        layout.addWidget(title)
        subtitle = QLabel("Командний центр конфігурації системи без змішування внутрішнього й зовнішнього контурів.")
        subtitle.setStyleSheet(f"color: {COLOR['text_secondary']};")
        layout.addWidget(subtitle)

        self._feedback = FormFeedbackLabel()
        layout.addWidget(self._feedback)

        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._content_widget = QWidget()
        self._content_layout = QVBoxLayout(self._content_widget)
        self._content_layout.setContentsMargins(0, 0, 0, 0)
        self._content_layout.setSpacing(SPACING["md"])
        self._scroll.setWidget(self._content_widget)
        layout.addWidget(self._scroll, stretch=1)

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

        sources_panel = NewsSourcesSettingsPanel(self._workspace.news_sources, self._read_only)
        sources_panel.source_created.connect(self._create_news_source)
        sources_panel.source_toggled.connect(self._toggle_source_activity)
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

        self._content_layout.addWidget(self._build_behavior_panel())
        self._content_layout.addWidget(self._build_service_info_panel())
        self._content_layout.addStretch()

    # ###### ПАНЕЛЬ ПОВЕДІНКИ СИСТЕМИ / BUILD BEHAVIOR PANEL ######
    def _build_behavior_panel(self) -> QWidget:
        """Builds behavior settings card."""

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

        card = SettingsSectionCard()
        layout = card.content_layout()
        title = QLabel("Службова інформація")
        title.setProperty("role", "section_title")
        layout.addWidget(title)
        layout.addWidget(QLabel(f"Версія: {self._workspace.app_version}"))
        layout.addWidget(QLabel(f"База даних: {self._workspace.database_path}"))
        layout.addWidget(QLabel(f"Каталог даних: {self._workspace.data_directory_path}"))
        layout.addWidget(QLabel(f"Стан ініціалізації: {'готово' if self._workspace.is_initialized else 'не готово'}"))
        if self._read_only:
            layout.addWidget(QLabel("Роль read-only: редагування налаштувань вимкнено."))
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

    # ###### ЗБЕРЕЖЕННЯ НАЛАШТУВАНЬ БЕКАПУ / SAVE BACKUP PREFERENCES ######
    def _save_backup_preferences(self, backup_auto_enabled: bool, backup_max_copies: int) -> None:
        """Saves backup-related preferences through shared behavior service."""

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
                backup_auto_enabled=backup_auto_enabled if backup_auto_enabled is not None else self._workspace.backup_auto_enabled,
                backup_max_copies=backup_max_copies if backup_max_copies is not None else self._workspace.backup_max_copies,
            )
        except Exception as error:  # noqa: BLE001
            self._feedback.show_error(f"Не вдалося зберегти параметри: {error}")
            return
        self._feedback.show_success("Поведінкові налаштування оновлено.")
        self._rebuild_sections()

    # ###### ВІДКРИТТЯ КАТАЛОГУ БЕКАПІВ / OPEN BACKUP DIRECTORY ######
    def _open_backup_directory(self) -> None:
        """Opens backup directory in system file manager."""

        QDesktopServices.openUrl(QUrl.fromLocalFile(self._workspace.backup_directory_path))
