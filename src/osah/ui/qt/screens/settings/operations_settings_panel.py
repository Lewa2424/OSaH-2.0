from PySide6.QtCore import Signal
from PySide6.QtWidgets import QLabel, QPushButton

from osah.ui.qt.screens.settings.settings_section_card import SettingsSectionCard


class OperationsSettingsPanel(SettingsSectionCard):
    """Service operations panel for backup/restore/import actions."""

    create_backup_requested = Signal()
    restore_backup_requested = Signal()
    create_import_batch_requested = Signal()
    apply_latest_import_requested = Signal()

    def __init__(self, read_only: bool) -> None:
        super().__init__()
        self._read_only = read_only

        layout = self.content_layout()
        title = QLabel("Службові операції")
        title.setProperty("role", "section_title")
        layout.addWidget(title)

        self._status = QLabel("Тут запускаються важкі операції у фоновому режимі без блокування інтерфейсу.")
        self._status.setProperty("role", "section_header_subtitle")
        self._status.setWordWrap(True)
        layout.addWidget(self._status)

        self._create_backup_button = QPushButton("Створити ручний бекап")
        self._create_backup_button.setProperty("variant", "secondary")
        self._create_backup_button.clicked.connect(self.create_backup_requested.emit)
        layout.addWidget(self._create_backup_button)

        self._restore_backup_button = QPushButton("Відновити з файла бекапу")
        self._restore_backup_button.setProperty("variant", "secondary")
        self._restore_backup_button.clicked.connect(self.restore_backup_requested.emit)
        layout.addWidget(self._restore_backup_button)

        self._create_import_button = QPushButton("Імпорт працівників з файла")
        self._create_import_button.setProperty("variant", "secondary")
        self._create_import_button.clicked.connect(self.create_import_batch_requested.emit)
        layout.addWidget(self._create_import_button)

        self._apply_import_button = QPushButton("Застосувати останню партію імпорту")
        self._apply_import_button.setProperty("variant", "secondary")
        self._apply_import_button.clicked.connect(self.apply_latest_import_requested.emit)
        layout.addWidget(self._apply_import_button)

        self._apply_read_only()

    # ###### СТАТУС ОПЕРАЦІЙ / OPERATION STATUS ######
    def set_status_text(self, status_text: str) -> None:
        """Updates operation status text."""

        self._status.setText(status_text)

    # ###### РЕЖИМ READ-ONLY / READ-ONLY MODE ######
    def _apply_read_only(self) -> None:
        """Disables modifying actions for read-only role."""

        editable = not self._read_only
        self._create_backup_button.setEnabled(editable)
        self._restore_backup_button.setEnabled(editable)
        self._create_import_button.setEnabled(editable)
        self._apply_import_button.setEnabled(editable)
