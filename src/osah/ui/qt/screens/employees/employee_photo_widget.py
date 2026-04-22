from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QLabel

from osah.ui.qt.design.tokens import COLOR


class EmployeePhotoWidget(QLabel):
    """Віджет фото працівника з безпечним fallback-placeholder.
    Employee photo widget with safe fallback placeholder.
    """

    def __init__(self, photo_path: str | None, full_name: str) -> None:
        super().__init__()
        self.setFixedSize(88, 88)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setStyleSheet(
            f"background: {COLOR['bg_panel']}; border: 1px solid {COLOR['border_soft']}; "
            "border-radius: 20px; font-size: 22px; font-weight: 800;"
        )
        self._load_photo(photo_path, full_name)

    # ###### ЗАВАНТАЖЕННЯ ФОТО / LOAD PHOTO ######
    def _load_photo(self, photo_path: str | None, full_name: str) -> None:
        """Показує фото з диска або ініціали, якщо фото недоступне.
        Shows a disk photo or initials when the photo is unavailable.
        """

        if photo_path and Path(photo_path).is_file():
            pixmap = QPixmap(photo_path)
            if not pixmap.isNull():
                scaled = pixmap.scaled(
                    self.size(),
                    Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                    Qt.TransformationMode.SmoothTransformation,
                )
                self.setPixmap(scaled)
                return

        initials = "".join(part[:1] for part in full_name.split()[:2]).upper()
        self.setText(initials or "П")
