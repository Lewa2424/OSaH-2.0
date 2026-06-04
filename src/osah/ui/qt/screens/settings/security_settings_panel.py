from PySide6.QtCore import Signal
from PySide6.QtWidgets import QLabel, QLineEdit, QPushButton

from osah.domain.entities.access_role import AccessRole
from osah.domain.entities.security_profile import SecurityProfile
from osah.ui.qt.design.tokens import COLOR, SPACING
from osah.ui.qt.screens.settings.settings_section_card import SettingsSectionCard


class SecuritySettingsPanel(SettingsSectionCard):
    """Security profile section for Settings screen."""

    password_change_requested = Signal(str, str, str)

    def __init__(self, profile: SecurityProfile, access_role: AccessRole) -> None:
        super().__init__()
        layout = self.content_layout()

        title = QLabel("Безпека")
        title.setProperty("role", "section_title")
        layout.addWidget(title)
        layout.addWidget(QLabel(f"Профіль: {'налаштовано' if profile.is_configured else 'не налаштовано'}"))
        layout.addWidget(QLabel(f"Ідентифікатор установки: {profile.installation_id or 'не задано'}"))
        layout.addWidget(QLabel(f"Невдалі входи: {profile.failed_attempt_count}"))
        layout.addWidget(QLabel(f"Блокування до: {profile.locked_until_text or 'немає'}"))
        layout.addWidget(QLabel(f"Файл відновлення: {profile.recovery_file_path or 'не створено'}"))
        layout.addWidget(QLabel(f"Файл відновлення створено: {profile.recovery_created_at_text or 'не задано'}"))
        role_text = "Інспектор (повний доступ)" if access_role == AccessRole.INSPECTOR else "Керівник (лише перегляд)"
        layout.addWidget(QLabel(f"Поточна роль: {role_text}"))

        if not profile.is_configured:
            return

        role_password_label = "інспектора" if access_role == AccessRole.INSPECTOR else "керівника"
        change_title = QLabel("Змінити пароль")
        change_title.setProperty("role", "section_title")
        layout.addWidget(change_title)

        hint = QLabel(
            f"Змінюється лише пароль {role_password_label}. Мінімум 8 символів; паролі ролей мають відрізнятися."
        )
        hint.setWordWrap(True)
        hint.setStyleSheet(f"color: {COLOR['text_muted']}; font-style: italic;")
        layout.addWidget(hint)

        self._current_password = QLineEdit()
        self._current_password.setPlaceholderText("Поточний пароль")
        self._current_password.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self._current_password)

        self._new_password = QLineEdit()
        self._new_password.setPlaceholderText("Новий пароль")
        self._new_password.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self._new_password)

        self._confirm_password = QLineEdit()
        self._confirm_password.setPlaceholderText("Підтвердження нового пароля")
        self._confirm_password.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self._confirm_password)

        save_button = QPushButton("Зберегти новий пароль")
        save_button.setProperty("variant", "accent")
        save_button.clicked.connect(self._emit_password_change)
        layout.addWidget(save_button)
        layout.addSpacing(SPACING["sm"])

    # ###### ЗАПИТ ЗМІНИ ПАРОЛЯ / EMIT PASSWORD CHANGE ######
    def _emit_password_change(self) -> None:
        """Емітить запит зміни пароля після локальної перевірки підтвердження.
        Emits password change request after local confirmation check.
        """

        self.password_change_requested.emit(
            self._current_password.text(),
            self._new_password.text(),
            self._confirm_password.text(),
        )
