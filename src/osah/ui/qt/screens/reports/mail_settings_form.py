from PySide6.QtCore import QTime, Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QFormLayout,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSpinBox,
    QTimeEdit,
    QVBoxLayout,
    QWidget,
)

from osah.domain.entities.mail_settings import MailSettings
from osah.domain.services.build_default_smtp_settings import build_default_smtp_settings
from osah.ui.qt.design.tokens import COLOR, RADIUS, SPACING


class MailSettingsForm(QFrame):
    """Форма налаштувань поштового контуру та часу щоденного звіту.
    Form for mail channel settings and daily report time.
    """

    save_requested = Signal(MailSettings)

    def __init__(self, mail_settings: MailSettings) -> None:
        super().__init__()
        self.setProperty("card", "true")

        self.enabled_box = QCheckBox("Автощоденний звіт увімкнено")
        self.enabled_box.setChecked(mail_settings.daily_report_enabled)

        self.report_time = QTimeEdit()
        self.report_time.setDisplayFormat("HH:mm")
        parsed_time = QTime.fromString(mail_settings.daily_report_time or "08:00", "HH:mm")
        self.report_time.setTime(parsed_time if parsed_time.isValid() else QTime(8, 0))

        self.recipient = QLineEdit(mail_settings.recipient_email)
        self.recipient.setPlaceholderText("Пошта керівника / отримувача")
        self.sender = QLineEdit(mail_settings.sender_email)
        self.sender.setPlaceholderText("Пошта відправника")
        self.sender.editingFinished.connect(self._apply_sender_defaults)
        self.sender.textEdited.connect(lambda _text: self._provider_hint.setText(self._build_provider_hint()))
        self.smtp_secret = QLineEdit(mail_settings.smtp_password)
        self.smtp_secret.setPlaceholderText("Пароль для пошти / пароль застосунку Google")
        self.smtp_secret.setEchoMode(QLineEdit.EchoMode.Password)
        self.smtp_host = QLineEdit(mail_settings.smtp_host)
        self.smtp_host.setPlaceholderText("smtp.example.com")
        self.smtp_port = QSpinBox()
        self.smtp_port.setRange(1, 65535)
        self.smtp_port.setValue(mail_settings.smtp_port if mail_settings.smtp_port > 0 else 587)
        self.smtp_username = QLineEdit(mail_settings.smtp_username)
        self.smtp_username.setPlaceholderText("Логін SMTP")
        self.use_tls = QCheckBox("TLS")
        self.use_tls.setChecked(mail_settings.use_tls)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(SPACING["lg"], SPACING["lg"], SPACING["lg"], SPACING["lg"])
        layout.setSpacing(SPACING["lg"])

        title = QLabel("Налаштування доставки")
        title.setProperty("role", "section_title")
        layout.addWidget(title)

        hint = QLabel(
            "Заповніть прості поля нижче. Для типового сценарію система підставить базові SMTP-параметри автоматично."
        )
        hint.setWordWrap(True)
        hint.setStyleSheet(f"color: {COLOR['text_muted']}; font-style: italic;")
        layout.addWidget(hint)

        schedule_frame = _build_inset_frame()
        schedule_layout = QVBoxLayout(schedule_frame)
        schedule_layout.setContentsMargins(SPACING["md"], SPACING["md"], SPACING["md"], SPACING["md"])
        schedule_layout.setSpacing(SPACING["md"])
        schedule_title = QLabel("Розклад і адреси")
        schedule_title.setProperty("role", "section_title")
        schedule_layout.addWidget(schedule_title)
        schedule_layout.addWidget(self.enabled_box)

        schedule_row = QHBoxLayout()
        schedule_row.setSpacing(SPACING["md"])
        time_box = QVBoxLayout()
        time_label = QLabel("Час відправки")
        time_box.addWidget(time_label)
        time_box.addWidget(self.report_time)
        schedule_row.addLayout(time_box, stretch=1)
        sender_box = QVBoxLayout()
        sender_label = QLabel("Пошта відправника")
        sender_box.addWidget(sender_label)
        sender_box.addWidget(self.sender)
        schedule_row.addLayout(sender_box, stretch=2)
        schedule_layout.addLayout(schedule_row)

        recipient_box = QVBoxLayout()
        recipient_label = QLabel("Пошта керівника / отримувача")
        recipient_box.addWidget(recipient_label)
        recipient_box.addWidget(self.recipient)
        schedule_layout.addLayout(recipient_box)

        secret_box = QVBoxLayout()
        secret_label = QLabel("Пароль для пошти / пароль застосунку Google")
        secret_box.addWidget(secret_label)
        secret_box.addWidget(self.smtp_secret)
        secret_hint = QLabel("Не пароль входу в OSaH. Для Gmail використовуйте пароль застосунку Google.")
        secret_hint.setWordWrap(True)
        secret_hint.setStyleSheet(f"color: {COLOR['text_muted']}; font-style: italic;")
        secret_box.addWidget(secret_hint)
        schedule_layout.addLayout(secret_box)

        self._provider_hint = QLabel()
        self._provider_hint.setWordWrap(True)
        self._provider_hint.setStyleSheet(f"color: {COLOR['text_muted']}; font-style: italic;")
        schedule_layout.addWidget(self._provider_hint)
        layout.addWidget(schedule_frame)

        self._advanced_toggle = QCheckBox("Показати додаткові SMTP-параметри")
        self._advanced_toggle.toggled.connect(self._toggle_advanced)
        self._advanced_toggle.setChecked(bool(mail_settings.smtp_host.strip()))
        layout.addWidget(self._advanced_toggle)

        self._advanced_frame = _build_inset_frame()
        advanced_layout = QVBoxLayout(self._advanced_frame)
        advanced_layout.setContentsMargins(SPACING["md"], SPACING["md"], SPACING["md"], SPACING["md"])
        advanced_layout.setSpacing(SPACING["md"])
        advanced_title = QLabel("Додаткові SMTP-параметри")
        advanced_title.setProperty("role", "section_title")
        advanced_layout.addWidget(advanced_title)
        advanced_hint = QLabel("Використовуйте цей блок, якщо сервер нестандартний або автоматичних значень недостатньо.")
        advanced_hint.setWordWrap(True)
        advanced_hint.setStyleSheet(f"color: {COLOR['text_muted']}; font-style: italic;")
        advanced_layout.addWidget(advanced_hint)

        form = QFormLayout()
        form.setHorizontalSpacing(SPACING["lg"])
        form.setVerticalSpacing(SPACING["md"])
        form.addRow("SMTP host", self.smtp_host)
        form.addRow("SMTP port", self.smtp_port)
        form.addRow("SMTP користувач", self.smtp_username)
        form.addRow("", self.use_tls)
        advanced_layout.addLayout(form)
        layout.addWidget(self._advanced_frame)

        save_button = QPushButton("Зберегти налаштування")
        save_button.setProperty("variant", "accent")
        save_button.clicked.connect(self._emit_save_requested)
        layout.addWidget(save_button)

        self._apply_sender_defaults()
        self._toggle_advanced(self._advanced_toggle.isChecked())
        self._provider_hint.setText(self._build_provider_hint())

    # ###### ПІДГОТОВКА НАЛАШТУВАНЬ / BUILD SETTINGS ######
    def values(self, last_sent_date: str = "") -> MailSettings:
        """Повертає MailSettings із поточних полів форми.
        Returns MailSettings from the current form fields.
        """

        self._apply_sender_defaults()
        return MailSettings(
            daily_report_enabled=self.enabled_box.isChecked(),
            smtp_host=self.smtp_host.text(),
            smtp_port=int(self.smtp_port.value()),
            smtp_username=self.smtp_username.text(),
            smtp_password=self.smtp_secret.text(),
            sender_email=self.sender.text(),
            recipient_email=self.recipient.text(),
            use_tls=self.use_tls.isChecked(),
            last_sent_date=last_sent_date,
            daily_report_time=self.report_time.time().toString("HH:mm"),
        )

    # ###### ЗАПИТ ЗБЕРЕЖЕННЯ / SAVE REQUEST ######
    def _emit_save_requested(self) -> None:
        """Передає поточні налаштування екрану для збереження.
        Emits current settings for saving by the screen.
        """

        self._apply_sender_defaults()
        self.save_requested.emit(self.values())

    def _toggle_advanced(self, visible: bool) -> None:
        """Перемикає видимість розширених SMTP-параметрів.
        Toggles visibility of advanced SMTP parameters.
        """

        self._advanced_frame.setVisible(visible)

    def _apply_sender_defaults(self) -> None:
        """Підставляє базові SMTP-значення, якщо користувач їх ще не задавав.
        Fills baseline SMTP values when the user has not set them yet.
        """

        default_host, default_port, default_username, default_tls = build_default_smtp_settings(self.sender.text())
        if default_host and not self.smtp_host.text().strip():
            self.smtp_host.setText(default_host)
        if default_port > 0 and self.smtp_port.value() <= 1:
            self.smtp_port.setValue(default_port)
        if default_username and not self.smtp_username.text().strip():
            self.smtp_username.setText(default_username)
        if not self.use_tls.isChecked():
            self.use_tls.setChecked(default_tls)

    def _build_provider_hint(self) -> str:
        """Повертає коротку підказку щодо базових SMTP-значень.
        Returns a short hint about baseline SMTP values.
        """

        default_host, default_port, default_username, default_tls = build_default_smtp_settings(self.sender.text())
        if not default_host:
            return "Після введення адреси відправника система підставить базові SMTP-значення."
        tls_text = "TLS увімкнено" if default_tls else "TLS вимкнено"
        return (
            f"Базово буде використано: {default_host}:{default_port}, "
            f"логін {default_username or 'не задано'}, {tls_text}."
        )


def _build_inset_frame() -> QFrame:
    """Створює inset-картку для логічного групування полів форми.
    Creates an inset card for logical grouping of form fields.
    """

    frame = QFrame()
    frame.setStyleSheet(
        f"background: {COLOR['bg_panel']}; border: 1px solid {COLOR['border_soft']}; "
        f"border-radius: {RADIUS['lg']}px;"
    )
    return frame
