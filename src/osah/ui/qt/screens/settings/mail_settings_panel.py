from PySide6.QtCore import Signal
from PySide6.QtWidgets import QCheckBox, QHBoxLayout, QLabel, QLineEdit, QPushButton

from osah.domain.entities.mail_settings import MailSettings
from osah.ui.qt.screens.settings.settings_section_card import SettingsSectionCard


class MailSettingsPanel(SettingsSectionCard):
    """Mail settings section for Settings screen."""

    save_requested = Signal(MailSettings)

    def __init__(self, mail_settings: MailSettings, read_only: bool) -> None:
        super().__init__()
        self._read_only = read_only
        self._base_mail_settings = mail_settings
        layout = self.content_layout()

        title = QLabel("Пошта")
        title.setProperty("role", "section_title")
        layout.addWidget(title)

        self._enabled = QCheckBox("Автозвіт увімкнено")
        self._enabled.setChecked(mail_settings.daily_report_enabled)
        layout.addWidget(self._enabled)

        self._recipient = QLineEdit(mail_settings.recipient_email)
        self._recipient.setPlaceholderText("Адреса керівника")
        layout.addWidget(self._recipient)

        row = QHBoxLayout()
        self._time = QLineEdit(mail_settings.daily_report_time)
        self._time.setPlaceholderText("Час (HH:MM)")
        row.addWidget(self._time)
        self._sender = QLineEdit(mail_settings.sender_email)
        self._sender.setPlaceholderText("Відправник")
        row.addWidget(self._sender)
        layout.addLayout(row)

        self._save_button = QPushButton("Зберегти поштові налаштування")
        self._save_button.setProperty("variant", "accent")
        self._save_button.clicked.connect(self._emit_save)
        layout.addWidget(self._save_button)

        last_sent = mail_settings.last_sent_date or "ще не відправлявся"
        layout.addWidget(QLabel(f"Остання відправка: {last_sent}"))
        self._apply_read_only()

    # ###### РЕЖИМ READ-ONLY / READ-ONLY MODE ######
    def _apply_read_only(self) -> None:
        """Applies read-only restrictions for manager role."""

        for field in (self._enabled, self._recipient, self._time, self._sender):
            field.setEnabled(not self._read_only)
        self._save_button.setEnabled(not self._read_only)

    # ###### ЗБЕРЕЖЕННЯ ПОШТОВИХ НАЛАШТУВАНЬ / SAVE MAIL SETTINGS ######
    def _emit_save(self) -> None:
        """Collects values and emits save request."""

        self.save_requested.emit(
            MailSettings(
                daily_report_enabled=self._enabled.isChecked(),
                smtp_host=self._base_mail_settings.smtp_host,
                smtp_port=self._base_mail_settings.smtp_port,
                smtp_username=self._base_mail_settings.smtp_username,
                smtp_password=self._base_mail_settings.smtp_password,
                sender_email=self._sender.text().strip(),
                recipient_email=self._recipient.text().strip(),
                use_tls=self._base_mail_settings.use_tls,
                last_sent_date=self._base_mail_settings.last_sent_date,
                daily_report_time=self._time.text().strip() or "08:00",
            )
        )
