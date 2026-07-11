from PySide6.QtCore import Signal
from PySide6.QtWidgets import QLabel, QPushButton, QVBoxLayout, QWidget

from osah.domain.entities.archive_entry import ArchiveEntry


class ArchiveDetailsPane(QWidget):
    """Detail pane for archive entry."""

    reactivate_requested = Signal(str)

    def __init__(self, allow_reactivation: bool) -> None:
        super().__init__()
        self._allow_reactivation = allow_reactivation
        self._entry_key: str | None = None
        self.setObjectName("archiveDetailsPane")
        self.setStyleSheet(
            """
            QWidget#archiveDetailsPane {
                background: rgba(255, 255, 255, 0.94);
                border: 1px solid #D6E1EC;
                border-radius: 24px;
            }
            QWidget#archiveDetailsPane QLabel[role="section_title"] {
                color: #102846;
                font-size: 24px;
                font-weight: 800;
            }
            QWidget#archiveDetailsPane QLabel {
                color: #1D3557;
                font-size: 15px;
            }
            QWidget#archiveDetailsPane QPushButton {
                min-height: 40px;
                font-size: 14px;
                font-weight: 800;
                border-radius: 14px;
            }
            """
        )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)
        title = QLabel("Деталі архіву")
        title.setProperty("role", "section_title")
        layout.addWidget(title)

        self._meta = QLabel("Оберіть запис у реєстрі.")
        self._meta.setWordWrap(True)
        layout.addWidget(self._meta)

        self._reactivate_button = QPushButton("Відновити / реактивувати")
        self._reactivate_button.setProperty("variant", "accent")
        self._reactivate_button.clicked.connect(self._emit_reactivate)
        layout.addWidget(self._reactivate_button)
        layout.addStretch()
        self._reactivate_button.setVisible(False)

    # ###### ПОКАЗ ДЕТАЛЕЙ ЗАПИСУ / SHOW ENTRY DETAILS ######
    def show_entry(self, entry: ArchiveEntry) -> None:
        """Displays selected archive entry details."""

        self._entry_key = entry.entry_key
        self._meta.setText(
            f"Тип: {entry.entry_type.value}\n"
            f"Назва: {entry.title}\n"
            f"Статус: {entry.status_label}\n"
            f"Дата архівації: {entry.archived_at_text}\n"
            f"Причина: {entry.reason_text}"
        )
        self._reactivate_button.setVisible(self._allow_reactivation and entry.can_reactivate)

    # ###### ВІДНОВЛЕННЯ ЗАПИСУ / REACTIVATE ENTRY ######
    def _emit_reactivate(self) -> None:
        """Emits reactivate request for selected employee entry."""

        if self._entry_key is None:
            return
        self.reactivate_requested.emit(self._entry_key)
