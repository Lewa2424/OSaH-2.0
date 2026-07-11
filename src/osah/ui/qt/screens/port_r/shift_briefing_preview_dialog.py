import shutil
from pathlib import Path

from PySide6.QtCore import QUrl, Signal
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import (
    QDialog,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
)

from osah.ui.qt.design.tokens import COLOR, SPACING


class ShiftBriefingPreviewDialog(QDialog):
    """Діалог-підсумок після створення оперативного листа зміни.
    Summary dialog shown after a shift briefing has been generated.
    """

    copy_requested = Signal(Path, Path)

    def __init__(
        self,
        produced_file_path: Path,
        passport_code: str,
        key_risks_count: int,
        parent=None,
    ) -> None:
        super().__init__(parent)
        self._produced_file_path = produced_file_path
        self.setWindowTitle("Оперативний лист зміни")
        self.setModal(True)
        self.setMinimumWidth(560)
        self.setStyleSheet(
            f"""
            QDialog {{
                background:
                    qlineargradient(x1:0, y1:0, x2:1, y2:1,
                        stop:0 rgba(255, 255, 255, 248),
                        stop:1 rgba(232, 240, 248, 234));
            }}
            QLabel {{
                font-size: 15px;
                color: {COLOR['text_primary']};
            }}
            QPushButton {{
                min-height: 40px;
                border-radius: 14px;
                font-size: 14px;
                font-weight: 800;
            }}
            """
        )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(SPACING["lg"], SPACING["lg"], SPACING["lg"], SPACING["lg"])
        layout.setSpacing(SPACING["md"])

        title_label = QLabel("Оперативний лист зміни створено")
        title_label.setStyleSheet("font-weight: 800; font-size: 22px; color: #102846;")
        layout.addWidget(title_label)

        summary_lines = (
            f"Паспорт: {passport_code}",
            f"Ключових ризиків у листі: {key_risks_count}",
            f"Шлях: {produced_file_path}",
        )
        for line in summary_lines:
            line_label = QLabel(line)
            line_label.setWordWrap(True)
            layout.addWidget(line_label)

        buttons_row = QHBoxLayout()
        buttons_row.setSpacing(SPACING["sm"])

        save_copy_btn = QPushButton("Зберегти копію…")
        save_copy_btn.setProperty("variant", "accent")
        save_copy_btn.clicked.connect(self._on_save_copy)
        buttons_row.addWidget(save_copy_btn)

        open_location_btn = QPushButton("Відкрити місце зберігання")
        open_location_btn.setProperty("variant", "secondary")
        open_location_btn.clicked.connect(self._on_open_location)
        buttons_row.addWidget(open_location_btn)

        buttons_row.addStretch()

        close_btn = QPushButton("Закрити")
        close_btn.setProperty("variant", "secondary")
        close_btn.clicked.connect(self.accept)
        buttons_row.addWidget(close_btn)

        layout.addLayout(buttons_row)

    def produced_file_path(self) -> Path:
        return self._produced_file_path

    def _on_save_copy(self) -> None:
        suggested_name = self._produced_file_path.name
        destination_path_text, _ = QFileDialog.getSaveFileName(
            self,
            "Зберегти копію оперативного листа",
            suggested_name,
            "Word Document (*.docx)",
        )
        if not destination_path_text:
            return
        destination_path = Path(destination_path_text)
        try:
            shutil.copy2(self._produced_file_path, destination_path)
        except OSError:
            return
        self.copy_requested.emit(self._produced_file_path, destination_path)

    def _on_open_location(self) -> None:
        parent_directory = self._produced_file_path.parent
        QDesktopServices.openUrl(QUrl.fromLocalFile(str(parent_directory)))
