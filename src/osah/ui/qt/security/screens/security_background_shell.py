"""
Security background shell with fullscreen image, translucent overlay and foreground content.
Security background shell with fullscreen image, translucent overlay and foreground content.
"""

from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget

from osah.ui.qt.design.tokens import COLOR


BACKGROUND_IMAGE_PATH = Path(__file__).resolve().parents[2] / "assets" / "security" / "auth_background.jpg"


class SecurityBackgroundShell(QWidget):
    """Фоновий shell для security-екранів із повноекранним зображенням і підкладкою.
    Background shell for security screens with a fullscreen image and translucent overlay.
    """

    def __init__(self) -> None:
        super().__init__()
        self._source_pixmap = QPixmap(str(BACKGROUND_IMAGE_PATH))

        self._background_label = QLabel(self)
        self._background_label.setScaledContents(False)

        self._overlay = QWidget(self)
        self._overlay.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self._overlay.setStyleSheet(
            f"background-color: {_build_overlay_rgba(COLOR['bg_app'], 0.40)};"
        )

        self._foreground = QWidget(self)
        self._foreground.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, False)
        self._foreground_layout = QVBoxLayout(self._foreground)
        self._foreground_layout.setContentsMargins(0, 0, 0, 0)
        self._foreground_layout.setSpacing(0)

    def content_layout(self) -> QVBoxLayout:
        """Повертає layout для контенту поверх фонового шару.
        Returns the layout used for content above the background layer.
        """

        return self._foreground_layout

    def resizeEvent(self, event) -> None:  # type: ignore[override]
        super().resizeEvent(event)
        bounds = self.rect()
        self._background_label.setGeometry(bounds)
        self._overlay.setGeometry(bounds)
        self._foreground.setGeometry(bounds)
        self._background_label.lower()
        self._overlay.raise_()
        self._foreground.raise_()
        self._update_background_pixmap()

    def _update_background_pixmap(self) -> None:
        """Масштабує фонове зображення за принципом cover без спотворення пропорцій.
        Scales the background image with a cover strategy and preserved aspect ratio.
        """

        if self._source_pixmap.isNull() or self.width() <= 0 or self.height() <= 0:
            self._background_label.clear()
            self._background_label.setStyleSheet(f"background-color: {COLOR['bg_app']};")
            return

        scaled = self._source_pixmap.scaled(
            self.size(),
            Qt.AspectRatioMode.KeepAspectRatioByExpanding,
            Qt.TransformationMode.SmoothTransformation,
        )
        crop_x = max(0, (scaled.width() - self.width()) // 2)
        crop_y = max(0, (scaled.height() - self.height()) // 2)
        cover = scaled.copy(crop_x, crop_y, self.width(), self.height())
        self._background_label.setPixmap(cover)
        self._background_label.setStyleSheet("background: transparent;")


def _build_overlay_rgba(hex_color: str, alpha_ratio: float) -> str:
    """Перетворює hex-колір у rgba-рядок для напівпрозорої підкладки.
    Converts a hex color into an rgba string for a translucent overlay.
    """

    value = hex_color.lstrip("#")
    if len(value) != 6:
        return "rgba(236, 239, 243, 184)"
    red = int(value[0:2], 16)
    green = int(value[2:4], 16)
    blue = int(value[4:6], 16)
    alpha = max(0, min(255, int(alpha_ratio * 255)))
    return f"rgba({red}, {green}, {blue}, {alpha})"
