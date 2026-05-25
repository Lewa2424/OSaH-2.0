from PySide6.QtCore import Signal
from PySide6.QtWidgets import QLabel, QPushButton

from osah.ui.qt.screens.settings.settings_section_card import SettingsSectionCard


class OperationsSettingsPanel(SettingsSectionCard):
    """Service operations panel for backup, restore, and employee import flow."""

    create_backup_requested = Signal()
    restore_backup_requested = Signal()
    import_requested = Signal()

    def __init__(self, read_only: bool) -> None:
        super().__init__()
        self._read_only = read_only

        layout = self.content_layout()
        title = QLabel("Службові операції")
        title.setProperty("role", "section_title")
        layout.addWidget(title)

        self._status = QLabel(
            "Тут виконуються резервне копіювання, відновлення та імпорт даних. "
            "Операції запускаються у фоновому режимі без блокування вікна."
        )
        self._status.setProperty("role", "section_header_subtitle")
        self._status.setWordWrap(True)
        layout.addWidget(self._status)

        self._create_backup_button = QPushButton("Створити резервну копію")
        self._create_backup_button.setProperty("variant", "secondary")
        self._create_backup_button.clicked.connect(self.create_backup_requested.emit)
        layout.addWidget(self._create_backup_button)

        self._restore_backup_button = QPushButton("Відновити з резервної копії")
        self._restore_backup_button.setProperty("variant", "secondary")
        self._restore_backup_button.clicked.connect(self.restore_backup_requested.emit)
        layout.addWidget(self._restore_backup_button)

        self._import_button = QPushButton("Імпорт працівників з файлу (ТЕСТОВИЙ РЕЖИМ)")
        self._import_button.setProperty("variant", "secondary")
        self._import_button.clicked.connect(self.import_requested.emit)
        layout.addWidget(self._import_button)

        self._apply_read_only()

    # ###### STATUS / OPERATION STATUS ######
    def set_status_text(self, status_text: str) -> None:
        """Updates operation status text.
        Оновлює текст статусу операцій.
        """

        self._status.setText(status_text)

    # ###### READ-ONLY MODE / READ-ONLY MODE ######
    def _apply_read_only(self) -> None:
        """Disables modifying actions for read-only role.
        Вимикає змінювальні дії для режиму лише перегляду.
        """

        editable = not self._read_only
        self._create_backup_button.setEnabled(editable)
        self._restore_backup_button.setEnabled(editable)
        self._import_button.setEnabled(editable)
