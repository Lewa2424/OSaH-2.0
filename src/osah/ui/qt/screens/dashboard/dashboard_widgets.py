"""
Dashboard-specific visual widgets.
Визуальные виджеты, специфичные для главного экрана.
"""

from weakref import ReferenceType, ref

from PySide6.QtCore import QEasingCurve, QTimer, QVariantAnimation, Qt, Signal
from PySide6.QtGui import QColor, QFont
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget
from shiboken6 import isValid

from osah.ui.qt.components.animations.pulse import apply_pulse
from osah.ui.qt.design.tokens import COLOR, FONT, SPACING
from osah.ui.qt.screens.dashboard.dashboard_motion import DashboardGlassFrame


class AnimatedNumberLabel(QLabel):
    """Animated integer label. Анимированная числовая метка."""

    def __init__(self, value: int, *, color: str, size_px: int, pulse: bool = False) -> None:
        super().__init__("0")
        self._target_value = max(0, value)
        self._pulse = pulse
        self._started = False
        font = QFont(FONT["metric"][0], 1)
        font.setPixelSize(size_px)
        font.setBold(True)
        self.setFont(font)
        self.setStyleSheet(
            f"color: {color};"
            f"font-size: {size_px}px;"
            "font-weight: 900;"
            "background: transparent;"
        )
        self.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

    def showEvent(self, event) -> None:  # noqa: N802
        super().showEvent(event)
        if self._started:
            return
        self._started = True
        self._animation = QVariantAnimation(self)
        self._animation.setDuration(1200)
        self._animation.setStartValue(0.0)
        self._animation.setEndValue(float(self._target_value))
        self._animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._animation.valueChanged.connect(lambda value: self.setText(str(round(float(value)))))
        self._animation.finished.connect(self._on_finished)
        self._animation.start()

    def _on_finished(self) -> None:
        self.setText(str(self._target_value))
        if self._pulse and self._target_value > 0:
            apply_pulse(self, min_opacity=0.55, beat_ms=920)


class DashboardCtaButton(QPushButton):
    """Animated CTA for dashboard modules. Анимированная CTA-кнопка модулей дашборда."""

    _registered_buttons: list[ReferenceType["DashboardCtaButton"]] = []
    _cycle_timer: QTimer | None = None
    _cycle_index = 0
    _cycle_step_ms = 1250

    def __init__(self, text: str, *, accent_color: str) -> None:
        super().__init__(text)
        self._accent_color = QColor(accent_color)
        self._pulse_progress = 0.0
        self._pulse_animation = QVariantAnimation(self)
        self._pulse_animation.setDuration(820)
        self._pulse_animation.setStartValue(0.0)
        self._pulse_animation.setEndValue(1.0)
        self._pulse_animation.setEasingCurve(QEasingCurve.Type.InOutCubic)
        self._pulse_animation.valueChanged.connect(self._on_pulse_value_changed)
        self._pulse_animation.finished.connect(self._finish_pulse)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFlat(True)
        self.setStyleSheet(self._build_stylesheet())
        self.destroyed.connect(self._unregister_from_cycle)
        self._register_for_cycle()

    def _register_for_cycle(self) -> None:
        existing_buttons = self.__class__._alive_buttons()
        if self in existing_buttons:
            return
        self.__class__._registered_buttons.append(ref(self))
        self.__class__._ensure_cycle_timer()

    def _unregister_from_cycle(self, *_args) -> None:
        self.__class__._registered_buttons = [
            button_ref
            for button_ref in self.__class__._registered_buttons
            if (button := button_ref()) is not None and button is not self and isValid(button)
        ]
        self.__class__._stop_cycle_if_idle()

    @classmethod
    def _ensure_cycle_timer(cls) -> None:
        if cls._cycle_timer is not None:
            return
        cls._cycle_timer = QTimer()
        cls._cycle_timer.setInterval(cls._cycle_step_ms)
        cls._cycle_timer.timeout.connect(cls._pulse_next_button)
        cls._cycle_timer.start()

    @classmethod
    def _pulse_next_button(cls) -> None:
        alive_buttons: list["DashboardCtaButton"] = []
        for button in cls._alive_buttons():
            if not isValid(button):
                continue
            try:
                if button.isHidden():
                    continue
            except RuntimeError:
                continue
            alive_buttons.append(button)
        if not alive_buttons:
            cls._stop_cycle_if_idle()
            return
        if cls._cycle_index >= len(alive_buttons):
            cls._cycle_index = 0
        button = alive_buttons[cls._cycle_index]
        cls._cycle_index = (cls._cycle_index + 1) % len(alive_buttons)
        if not isValid(button):
            return
        try:
            if button.isVisible():
                button.pulse_once()
        except RuntimeError:
            return

    @classmethod
    def _alive_buttons(cls) -> list["DashboardCtaButton"]:
        alive: list["DashboardCtaButton"] = []
        fresh_refs: list[ReferenceType["DashboardCtaButton"]] = []
        for button_ref in cls._registered_buttons:
            button = button_ref()
            if button is None or not isValid(button):
                continue
            alive.append(button)
            fresh_refs.append(button_ref)
        cls._registered_buttons = fresh_refs
        return alive

    @classmethod
    def _stop_cycle_if_idle(cls) -> None:
        if cls._alive_buttons():
            return
        cls._cycle_index = 0
        if cls._cycle_timer is not None:
            cls._cycle_timer.stop()
            cls._cycle_timer.deleteLater()
            cls._cycle_timer = None

    def pulse_once(self) -> None:
        if self._pulse_animation.state() == QVariantAnimation.State.Running:
            return
        self._pulse_animation.setDirection(QVariantAnimation.Direction.Forward)
        self._pulse_animation.start()

    def _on_pulse_value_changed(self, value: object) -> None:
        self._pulse_progress = float(value)
        self.setStyleSheet(self._build_stylesheet())

    def _finish_pulse(self) -> None:
        if self._pulse_animation.direction() == QVariantAnimation.Direction.Forward:
            self._pulse_animation.setDirection(QVariantAnimation.Direction.Backward)
            self._pulse_animation.start()
            return
        self._pulse_progress = 0.0
        self.setStyleSheet(self._build_stylesheet())

    def _build_stylesheet(self) -> str:
        glow_alpha = int(28 + 42 * self._pulse_progress)
        border_alpha = int(36 + 70 * self._pulse_progress)
        text_color = self._mix_color(self._accent_color, QColor(COLOR["text_primary"]), 0.32 + 0.28 * self._pulse_progress)
        background = self._mix_color(QColor(255, 255, 255), self._accent_color, 0.08 + 0.12 * self._pulse_progress)
        border = QColor(self._accent_color)
        border.setAlpha(border_alpha)
        background.setAlpha(glow_alpha)
        return (
            "QPushButton {"
            f"color: {text_color.name()};"
            f"background: {background.name(QColor.NameFormat.HexArgb)};"
            f"border: 1px solid {border.name(QColor.NameFormat.HexArgb)};"
            "border-radius: 12px;"
            "padding: 7px 12px;"
            "font-size: 15px;"
            "font-weight: 800;"
            "text-align: center;"
            "}"
            "QPushButton:hover {"
            f"color: {self._accent_color.name()};"
            f"background: {self._mix_color(QColor(255, 255, 255), self._accent_color, 0.18).name(QColor.NameFormat.HexArgb)};"
            "}"
            "QPushButton:pressed {"
            f"color: {self._accent_color.name()};"
            f"background: {self._mix_color(QColor(255, 255, 255), self._accent_color, 0.24).name(QColor.NameFormat.HexArgb)};"
            "}"
        )

    @staticmethod
    def _mix_color(base: QColor, accent: QColor, ratio: float) -> QColor:
        ratio = max(0.0, min(1.0, ratio))
        inverse = 1.0 - ratio
        return QColor(
            int(base.red() * inverse + accent.red() * ratio),
            int(base.green() * inverse + accent.green() * ratio),
            int(base.blue() * inverse + accent.blue() * ratio),
        )


class DashboardStatCard(DashboardGlassFrame):
    """Primary dashboard stat card. Основная стат-карточка главного экрана."""

    def __init__(self, title: str, value: int, subtitle: str, accent_color: str) -> None:
        super().__init__(border_color=accent_color, fill_ratio=0.90)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(SPACING["lg"], SPACING["lg"], SPACING["lg"], SPACING["lg"])
        layout.setSpacing(6)

        title_label = QLabel(title)
        title_label.setStyleSheet(
            f"color: {COLOR['text_secondary']};"
            "font-size: 18px;"
            "font-weight: 800;"
            "letter-spacing: 0.5px;"
            "background: transparent;"
        )
        layout.addWidget(title_label)

        number_label = AnimatedNumberLabel(
            value,
            color=accent_color,
            size_px=22,
            pulse=accent_color == COLOR["critical"],
        )
        layout.addWidget(number_label)

        subtitle_label = QLabel(subtitle)
        subtitle_label.setWordWrap(True)
        subtitle_label.setStyleSheet(
            f"color: {COLOR['text_muted']};"
            "font-size: 15px;"
            "font-weight: 600;"
            "background: transparent;"
        )
        layout.addWidget(subtitle_label)
        layout.addStretch()


class DashboardModuleCard(DashboardGlassFrame):
    """Module focus tile with CTA. Плитка модуля с фокусом и действием."""

    clicked = Signal()

    def __init__(
        self,
        *,
        title: str,
        caption: str,
        critical_count: int,
        warning_count: int,
        accent_color: str,
        action_label: str,
    ) -> None:
        super().__init__(border_color=accent_color, fill_ratio=0.92)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(SPACING["lg"], SPACING["md"], SPACING["lg"], SPACING["md"])
        layout.setSpacing(8)

        title_label = QLabel(title)
        title_label.setStyleSheet(
            f"color: {COLOR['text_primary']};"
            "font-size: 18px;"
            "font-weight: 800;"
            "background: transparent;"
        )
        layout.addWidget(title_label)

        counts_row = QHBoxLayout()
        counts_row.setSpacing(SPACING["sm"])
        counts_row.addWidget(_build_signal_badge("Критично", critical_count, COLOR["critical"]))
        counts_row.addWidget(_build_signal_badge("Увага", warning_count, COLOR["warning"]))
        counts_row.addStretch()
        layout.addLayout(counts_row)

        caption_label = QLabel(caption)
        caption_label.setWordWrap(True)
        caption_label.setStyleSheet(
            f"color: {COLOR['text_secondary']};"
            "font-size: 15px;"
            "font-weight: 600;"
            "background: transparent;"
        )
        layout.addWidget(caption_label)
        layout.addStretch()

        button = DashboardCtaButton(action_label, accent_color=accent_color)
        button.clicked.connect(self.clicked.emit)
        layout.addWidget(button)


class DashboardFeedCard(DashboardGlassFrame):
    """Compact feed card for news and service logs. Компактная карточка для новостей и служебных событий."""

    def __init__(self, *, title: str, body: str, accent_color: str, meta: str = "") -> None:
        super().__init__(border_color=accent_color, fill_ratio=0.90)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(SPACING["md"], SPACING["md"], SPACING["md"], SPACING["md"])
        layout.setSpacing(6)

        title_label = QLabel(title)
        title_label.setWordWrap(True)
        title_label.setStyleSheet(
            f"color: {COLOR['text_primary']};"
            "font-size: 15px;"
            "font-weight: 800;"
            "background: transparent;"
        )
        layout.addWidget(title_label)

        body_label = QLabel(body)
        body_label.setWordWrap(True)
        body_label.setStyleSheet(
            f"color: {COLOR['text_secondary']};"
            "font-size: 14px;"
            "font-weight: 600;"
            "background: transparent;"
        )
        layout.addWidget(body_label)

        if meta:
            meta_label = QLabel(meta)
            meta_label.setStyleSheet(
                f"color: {COLOR['text_muted']};"
                "font-size: 13px;"
                "font-weight: 700;"
                "background: transparent;"
            )
            layout.addWidget(meta_label)


def _build_signal_badge(label: str, value: int, color: str) -> QWidget:
    """Builds colored signal badge. Создает цветной badge сигнала."""

    rgb = QColor(color)
    badge = QFrame()
    badge.setStyleSheet(
        f"background: rgba({rgb.red()}, {rgb.green()}, {rgb.blue()}, 24);"
        "border: none;"
        "border-radius: 9px;"
    )
    layout = QHBoxLayout(badge)
    layout.setContentsMargins(8, 2, 8, 2)
    layout.setSpacing(5)

    name_label = QLabel(label)
    name_label.setStyleSheet(
        f"color: {color};"
        "font-size: 12px;"
        "font-weight: 800;"
        "background: transparent;"
    )
    layout.addWidget(name_label)

    value_label = QLabel(str(value))
    value_label.setStyleSheet(
        f"color: {color};"
        "font-size: 14px;"
        "font-weight: 900;"
        "background: transparent;"
    )
    layout.addWidget(value_label)
    return badge
