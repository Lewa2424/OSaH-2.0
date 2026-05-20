"""
SideNav — ліва навігаційна панель.
Містить логотип, кнопки розділів та footer.
SideNav — left navigation panel containing logo, buttons and footer.
"""
from typing import Callable

from PySide6.QtCore import QRectF, Qt, Signal
from PySide6.QtGui import QFont, QPainter, QPainterPath, QPixmap
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QVBoxLayout, QWidget

from osah.domain.entities.access_role import AccessRole
from osah.domain.entities.app_section import AppSection
from osah.domain.entities.notification_level import NotificationLevel
from osah.ui.qt.branding import DISPLAY_NAME, LOGO_MARK_PATH
from osah.ui.qt.components.nav_button import NavButton
from osah.ui.qt.design.tokens import COLOR, FONT, SIZE, SPACING


class SideNav(QWidget):
    """Ліва навігаційна панель (Sidebar)."""

    section_selected = Signal(AppSection)

    def __init__(
        self,
        sections: tuple[AppSection, ...],
        access_role: AccessRole,
        section_levels: dict[AppSection, NotificationLevel],
    ) -> None:
        super().__init__()
        self.setProperty("role", "sidenav")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setFixedWidth(SIZE["nav_width"])

        layout = QVBoxLayout(self)
        layout.setContentsMargins(SPACING["lg"], SPACING["xl"], SPACING["lg"], SPACING["xl"])
        layout.setSpacing(SPACING["sm"])

        # ---- Логотип ----
        logo = QLabel()
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_size = int((SIZE["nav_width"] - (SPACING["lg"] * 2)) * 0.9)
        logo.setFixedSize(logo_size, logo_size)
        logo_pixmap = _build_rounded_logo_pixmap(LOGO_MARK_PATH, logo_size, 8)
        if not logo_pixmap.isNull():
            logo.setPixmap(logo_pixmap)
        else:
            logo.setText(DISPLAY_NAME)
            logo.setProperty("role", "logo")
            logo_font = QFont(FONT["title_xl"][0], 18)
            logo_font.setBold(True)
            logo.setFont(logo_font)
        layout.addWidget(logo)

        desc = QLabel("Локальний пульт інспектора з охорони праці.")
        desc.setWordWrap(True)
        desc.setProperty("role", "status_muted")
        desc.setStyleSheet(
            f"color: {COLOR['text_muted']}; "
            f"font-size: {FONT['nav_item'][1]}px; "
            f"font-weight: 700;"
        )
        layout.addWidget(desc)

        layout.addSpacing(SPACING["lg"])

        # ---- Кнопки навігації ----
        self._buttons: dict[AppSection, NavButton] = {}

        for section in sections:
            # Розділювач перед другорядною групою
            if section == AppSection.CONTRACTORS:
                sep = QFrame()
                sep.setFixedHeight(1)
                sep.setStyleSheet(f"background: {COLOR['border_soft']}; margin: 8px 0;")
                layout.addWidget(sep)

            btn = NavButton(section, section_levels.get(section))
            btn.clicked.connect(self._on_button_clicked)
            layout.addWidget(btn)
            self._buttons[section] = btn

        layout.addStretch()

        # ---- Footer ----
        footer = QLabel("Система працює автономно.")
        footer.setWordWrap(True)
        footer.setProperty("role", "status_muted")
        layout.addWidget(footer)

    def _on_button_clicked(self, section: AppSection) -> None:
        self.set_active_section(section)
        self.section_selected.emit(section)

    def set_active_section(self, active_section: AppSection) -> None:
        """Оновлює стан кнопок: підсвічує активну, скидає інші."""
        for section, btn in self._buttons.items():
            btn.set_active(section == active_section)

    def update_alert_levels(self, section_levels: dict[AppSection, NotificationLevel]) -> None:
        """Оновлює рівні сповіщень для всіх кнопок без перестворення меню."""
        for section, btn in self._buttons.items():
            btn.set_alert_level(section_levels.get(section))


def _build_rounded_logo_pixmap(image_path, size: int, radius: int) -> QPixmap:
    """Готує квадратну логомарку зі збереженням пропорцій та округленням кутів.
    Builds a square logo mark with preserved aspect ratio and rounded corners.
    """

    source = QPixmap(str(image_path))
    if source.isNull():
        return QPixmap()

    scaled = source.scaled(
        size,
        size,
        Qt.AspectRatioMode.KeepAspectRatioByExpanding,
        Qt.TransformationMode.SmoothTransformation,
    )
    crop_x = max(0, (scaled.width() - size) // 2)
    crop_y = max(0, (scaled.height() - size) // 2)
    square = scaled.copy(crop_x, crop_y, size, size)

    rounded = QPixmap(size, size)
    rounded.fill(Qt.GlobalColor.transparent)

    painter = QPainter(rounded)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
    painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)

    clip_path = QPainterPath()
    clip_path.addRoundedRect(QRectF(0, 0, size, size), radius, radius)
    painter.setClipPath(clip_path)
    painter.drawPixmap(0, 0, square)
    painter.end()

    return rounded
