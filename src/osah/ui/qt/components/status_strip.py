"""
StatusStrip — нижня смужка стану застосунку.
Показує шлях до БД, роль і статус.
StatusStrip — bottom status bar showing DB path, role and status.
"""
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QHBoxLayout, QLabel, QWidget

from osah.domain.entities.access_role import AccessRole
from osah.domain.services.security.format_access_role_label import format_access_role_label
from osah.ui.qt.design.tokens import COLOR, SIZE, SPACING


class StatusStrip(QWidget):
    """Нижня смужка статусу з інформацією про БД і роль.
    Bottom status strip with database and role information.
    """

    def __init__(self, database_path: Path, access_role: AccessRole) -> None:
        super().__init__()
        self.setProperty("role", "statusbar")
        self.setFixedHeight(SIZE["status_bar_height"])

        layout = QHBoxLayout(self)
        layout.setContentsMargins(SPACING["xl"], 0, SPACING["xl"], 0)
        layout.setSpacing(SPACING["xl"])

        # Шлях до БД / DB path
        db_label = QLabel(f"БД: {database_path.name}")
        db_label.setStyleSheet(f"color: {COLOR['text_muted']}; font-size: 9px;")
        layout.addWidget(db_label)

        # Розділювач / Separator
        sep = QLabel("·")
        sep.setStyleSheet(f"color: {COLOR['border_strong']}; font-size: 9px;")
        layout.addWidget(sep)

        # Роль / Role
        role_label = QLabel(f"Роль: {format_access_role_label(access_role)}")
        role_label.setStyleSheet(f"color: {COLOR['text_muted']}; font-size: 9px;")
        layout.addWidget(role_label)

        layout.addStretch()

        # Статус / Status
        status_label = QLabel("● Локальна БД")
        status_label.setStyleSheet(f"color: {COLOR['success']}; font-size: 9px;")
        status_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        layout.addWidget(status_label)
