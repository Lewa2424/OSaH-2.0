from PySide6.QtCore import Signal
from PySide6.QtWidgets import QCheckBox, QFormLayout, QFrame, QHBoxLayout, QLabel, QLineEdit, QPushButton, QSpinBox

from osah.domain.entities.mail_settings import MailSettings
from osah.domain.services.build_default_smtp_settings import build_default_smtp_settings
from osah.domain.services.format_ui_date import format_ui_date
from osah.ui.qt.design.tokens import COLOR, RADIUS, SPACING
from osah.ui.qt.screens.settings.settings_section_card import SettingsSectionCard


class MailSettingsPanel(SettingsSectionCard):
    """Поштова секція екрана налаштувань.
    Mail settings section for Settings screen.
    """

    save_requested = Signal(MailSettings)

    def __init__(self, mail_settings: MailSettings, read_only: bool) -> None:
        super().__init__()
        self._read_only = read_only
        self._base_mail_settings = mail_settings
        layout = self.content_layout()

        title = QLabel("Пошта")
        title.setProperty("role", "section_title")
        layout.addWidget(title)

        help_label = QLabel(
            "Простий режим: отримувач, відправник, пароль пошти і час. SMTP-параметри доступні нижче лише за потреби."
        )
        help_label.setWordWrap(True)
        help_label.setStyleSheet(f"color: {COLOR['text_muted']}; font-style: italic;")
        layout.addWidget(help_label)

        self._enabled = QCheckBox("Автозвіт увімкнено")
        self._enabled.setChecked(mail_settings.daily_report_enabled)
        layout.addWidget(self._enabled)

        self._recipient = QLineEdit(mail_settings.recipient_email)
        self._recipient.setPlaceholderText("Одержувачі через ;")
        layout.addWidget(self._recipient)

        recipient_hint = QLabel("Якщо отримувачів кілька, розділяйте адреси символом ;")
        recipient_hint.setWordWrap(True)
        recipient_hint.setStyleSheet(f"color: {COLOR['text_muted']}; font-style: italic;")
        layout.addWidget(recipient_hint)

        row = QHBoxLayout()
        row.setSpacing(SPACING["md"])
        self._time = QLineEdit(mail_settings.daily_report_time)
        self._time.setPlaceholderText("Час (HH:MM)")
        row.addWidget(self._time, stretch=1)
        self._sender = QLineEdit(mail_settings.sender_email)
        self._sender.setPlaceholderText("Пошта відправника")
        self._sender.editingFinished.connect(self._apply_sender_defaults)
        row.addWidget(self._sender, stretch=2)
        layout.addLayout(row)

        self._password = QLineEdit(mail_settings.smtp_password)
        self._password.setPlaceholderText("Пароль пошти / окремий пароль для зовнішнього застосунку")
        self._password.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self._password)

        password_hint = QLabel(
            "Не пароль входу в OSaH. Якщо поштовий сервер вимагає окремий пароль для зовнішніх застосунків, використовуйте саме його."
        )
        password_hint.setWordWrap(True)
        password_hint.setStyleSheet(f"color: {COLOR['text_muted']}; font-style: italic;")
        layout.addWidget(password_hint)

        self._advanced_toggle = QCheckBox("Показати додаткові SMTP-параметри")
        self._advanced_toggle.setChecked(bool(mail_settings.smtp_host.strip()))
        self._advanced_toggle.toggled.connect(self._toggle_advanced)
        layout.addWidget(self._advanced_toggle)

        self._advanced_frame = QFrame()
        self._advanced_frame.setStyleSheet(
            f"background: {COLOR['bg_panel']}; border: 1px solid {COLOR['border_soft']}; "
            f"border-radius: {RADIUS['md']}px;"
        )
        advanced_layout = QFormLayout(self._advanced_frame)
        advanced_layout.setContentsMargins(SPACING["md"], SPACING["md"], SPACING["md"], SPACING["md"])
        advanced_layout.setHorizontalSpacing(SPACING["lg"])
        advanced_layout.setVerticalSpacing(SPACING["md"])

        self._smtp_host = QLineEdit(mail_settings.smtp_host)
        self._smtp_host.setPlaceholderText("smtp.example.com")
        self._smtp_port = QSpinBox()
        self._smtp_port.setRange(1, 65535)
        self._smtp_port.setValue(mail_settings.smtp_port if mail_settings.smtp_port > 0 else 587)
        self._smtp_username = QLineEdit(mail_settings.smtp_username)
        self._smtp_username.setPlaceholderText("Логін SMTP")
        self._tls = QCheckBox("TLS")
        self._tls.setChecked(mail_settings.use_tls)

        advanced_layout.addRow("SMTP host", self._smtp_host)
        advanced_layout.addRow("SMTP port", self._smtp_port)
        advanced_layout.addRow("SMTP користувач", self._smtp_username)
        advanced_layout.addRow("", self._tls)
        layout.addWidget(self._advanced_frame)

        self._save_button = QPushButton("Зберегти поштові налаштування")
        self._save_button.setProperty("variant", "accent")
        self._save_button.clicked.connect(self._emit_save)
        layout.addWidget(self._save_button)

        last_sent = format_ui_date(mail_settings.last_sent_date) if mail_settings.last_sent_date else "ще не відправлявся"
        layout.addWidget(QLabel(f"Остання відправка: {last_sent}"))
        self._apply_sender_defaults()
        self._toggle_advanced(self._advanced_toggle.isChecked())
        self._apply_read_only()

    def _apply_read_only(self) -> None:
        """Застосовує обмеження read-only для ролі керівника.
        Applies read-only restrictions for manager role.
        """

        for field in (
            self._enabled,
            self._recipient,
            self._time,
            self._sender,
            self._password,
            self._advanced_toggle,
            self._smtp_host,
            self._smtp_port,
            self._smtp_username,
            self._tls,
        ):
            field.setEnabled(not self._read_only)
        self._save_button.setEnabled(not self._read_only)

    def _emit_save(self) -> None:
        """Збирає значення та відправляє запит на збереження.
        Collects values and emits save request.
        """

        self._apply_sender_defaults()
        self.save_requested.emit(
            MailSettings(
                daily_report_enabled=self._enabled.isChecked(),
                smtp_host=self._smtp_host.text().strip(),
                smtp_port=int(self._smtp_port.value()),
                smtp_username=self._smtp_username.text().strip(),
                smtp_password=self._password.text(),
                sender_email=self._sender.text().strip(),
                recipient_email=self._recipient.text().strip(),
                use_tls=self._tls.isChecked(),
                last_sent_date=self._base_mail_settings.last_sent_date,
                daily_report_time=self._time.text().strip() or "08:00",
            )
        )

    def _toggle_advanced(self, visible: bool) -> None:
        """Перемикає видимість розширених SMTP-полів.
        Toggles visibility of advanced SMTP fields.
        """

        self._advanced_frame.setVisible(visible)

    def _apply_sender_defaults(self) -> None:
        """Підставляє базові SMTP-значення на основі адреси відправника.
        Fills baseline SMTP values based on sender address.
        """

        default_host, default_port, default_username, default_tls = build_default_smtp_settings(self._sender.text())
        if default_host and not self._smtp_host.text().strip():
            self._smtp_host.setText(default_host)
        if default_port > 0 and self._smtp_port.value() <= 1:
            self._smtp_port.setValue(default_port)
        if default_username and not self._smtp_username.text().strip():
            self._smtp_username.setText(default_username)
        if not self._tls.isChecked():
            self._tls.setChecked(default_tls)
