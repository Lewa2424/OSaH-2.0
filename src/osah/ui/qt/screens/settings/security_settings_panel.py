from osah.domain.entities.access_role import AccessRole
from osah.domain.entities.security_profile import SecurityProfile
from osah.ui.qt.screens.settings.settings_section_card import SettingsSectionCard
from PySide6.QtWidgets import QLabel


class SecuritySettingsPanel(SettingsSectionCard):
    """Security profile section for Settings screen."""

    def __init__(self, profile: SecurityProfile, access_role: AccessRole) -> None:
        super().__init__()
        layout = self.content_layout()

        title = QLabel("Безпека")
        title.setProperty("role", "section_title")
        layout.addWidget(title)
        layout.addWidget(QLabel(f"Профіль: {'налаштовано' if profile.is_configured else 'не налаштовано'}"))
        layout.addWidget(QLabel(f"ID установки: {profile.installation_id or 'n/a'}"))
        layout.addWidget(QLabel(f"Невдалі входи: {profile.failed_attempt_count}"))
        layout.addWidget(QLabel(f"Блокування до: {profile.locked_until_text or 'немає'}"))
        layout.addWidget(QLabel(f"Recovery-файл: {profile.recovery_file_path or 'не створено'}"))
        layout.addWidget(QLabel(f"Recovery створено: {profile.recovery_created_at_text or 'n/a'}"))
        role_text = "Інспектор (повний доступ)" if access_role == AccessRole.INSPECTOR else "Керівник (read-only)"
        layout.addWidget(QLabel(f"Поточна роль: {role_text}"))
