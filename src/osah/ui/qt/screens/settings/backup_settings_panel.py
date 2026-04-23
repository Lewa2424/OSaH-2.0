from PySide6.QtCore import Signal
from PySide6.QtWidgets import QCheckBox, QHBoxLayout, QLabel, QLineEdit, QPushButton

from osah.ui.qt.screens.settings.settings_section_card import SettingsSectionCard


class BackupSettingsPanel(SettingsSectionCard):
    """Backup settings section for Settings screen."""

    save_requested = Signal(bool, int)
    open_backup_requested = Signal()

    def __init__(
        self,
        backup_directory_path: str,
        snapshot_count: int,
        backup_auto_enabled: bool,
        backup_max_copies: int,
        read_only: bool,
    ) -> None:
        super().__init__()
        self._read_only = read_only
        layout = self.content_layout()

        title = QLabel("Бекап і відновлення")
        title.setProperty("role", "section_title")
        layout.addWidget(title)
        layout.addWidget(QLabel(f"Каталог копій: {backup_directory_path}"))
        layout.addWidget(QLabel(f"Наявні копії: {snapshot_count}"))

        self._auto_enabled = QCheckBox("Автокопіювання увімкнено")
        self._auto_enabled.setChecked(backup_auto_enabled)
        layout.addWidget(self._auto_enabled)

        row = QHBoxLayout()
        self._max_copies = QLineEdit(str(backup_max_copies))
        self._max_copies.setPlaceholderText("Макс. кількість копій")
        row.addWidget(self._max_copies)
        self._save_button = QPushButton("Зберегти політику бекапів")
        self._save_button.setProperty("variant", "secondary")
        self._save_button.clicked.connect(self._emit_save)
        row.addWidget(self._save_button)
        layout.addLayout(row)

        open_button = QPushButton("Відкрити каталог бекапів")
        open_button.setProperty("variant", "secondary")
        open_button.clicked.connect(self.open_backup_requested.emit)
        layout.addWidget(open_button)
        self._open_button = open_button
        self._apply_read_only()

    # ###### РЕЖИМ READ-ONLY / READ-ONLY MODE ######
    def _apply_read_only(self) -> None:
        """Applies read-only restrictions for manager role."""

        editable = not self._read_only
        self._auto_enabled.setEnabled(editable)
        self._max_copies.setReadOnly(not editable)
        self._save_button.setEnabled(editable)
        self._open_button.setEnabled(True)

    # ###### ЗБЕРЕЖЕННЯ ПОЛІТИКИ БЕКАПІВ / SAVE BACKUP POLICY ######
    def _emit_save(self) -> None:
        """Emits request to save backup behavior settings."""

        self.save_requested.emit(self._auto_enabled.isChecked(), int(self._max_copies.text() or "20"))
