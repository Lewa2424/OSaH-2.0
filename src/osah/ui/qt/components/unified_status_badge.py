from PySide6.QtCore import QEasingCurve, QVariantAnimation
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QLabel

from osah.ui.qt.design.tokens import ANIMATION, COLOR


class UnifiedStatusBadge(QLabel):
    """Unified status badge with animated transitions and critical pulse."""

    _STATUS_STYLE = {
        "critical": ("Критично", COLOR["critical_subtle"], COLOR["critical"]),
        "warning": ("Увага", COLOR["warning_subtle"], COLOR["warning"]),
        "normal": ("Норма", COLOR["success_subtle"], COLOR["success"]),
        "info": ("Інфо", COLOR["accent_subtle"], COLOR["accent"]),
        "archived": ("Архів", COLOR["bg_panel"], COLOR["text_muted"]),
        "readonly": ("Тільки перегляд", COLOR["bg_panel"], COLOR["text_secondary"]),
    }

    def __init__(self, status_key: str, reason_text: str = "") -> None:
        super().__init__()
        self.setWordWrap(True)
        self._current_bg = COLOR["accent_subtle"]
        self._current_border = COLOR["accent"]
        self._bg_animation: QVariantAnimation | None = None
        self.set_status(status_key, reason_text)

    # ###### ВСТАНОВЛЕННЯ СТАТУСУ БЕЙДЖА / SET BADGE STATUS ######
    def set_status(self, status_key: str, reason_text: str = "") -> None:
        """Встановлює стиль і текст бейджа, плавно переходить між кольорами.
        Sets badge style and text by status key with smooth color transition.
        """
        from osah.ui.qt.components.animations.pulse import apply_pulse, stop_pulse

        label_text, target_bg, target_border = self._STATUS_STYLE.get(
            status_key,
            ("Інфо", COLOR["accent_subtle"], COLOR["accent"]),
        )
        full_text = label_text if not reason_text.strip() else f"{label_text} — {reason_text}"
        self.setText(full_text)

        self._animate_colors(target_bg, target_border)

        if status_key == "critical":
            apply_pulse(self, min_opacity=0.45, beat_ms=900)
        else:
            stop_pulse(self)

    def _animate_colors(self, target_bg: str, target_border: str) -> None:
        """Плавно переходить між поточними та цільовими кольорами.
        Smoothly transitions between current and target badge colors.
        """
        if self._bg_animation is not None:
            self._bg_animation.stop()

        start_bg = self._current_bg
        start_border = self._current_border

        if start_bg == target_bg and start_border == target_border:
            self._apply_badge_style(target_bg, target_border)
            return

        animation = QVariantAnimation(self)
        animation.setDuration(ANIMATION["fast"])
        animation.setStartValue(0.0)
        animation.setEndValue(1.0)
        animation.setEasingCurve(QEasingCurve.Type.InOutCubic)
        animation.valueChanged.connect(
            lambda v: self._apply_badge_style(
                _mix_hex(start_bg, target_bg, float(v)),
                _mix_hex(start_border, target_border, float(v)),
            )
        )
        animation.finished.connect(lambda: self._on_color_transition_done(target_bg, target_border))
        animation.start()
        self._bg_animation = animation

    def _on_color_transition_done(self, final_bg: str, final_border: str) -> None:
        """Фіксує кінцеві кольори після завершення переходу."""
        self._current_bg = final_bg
        self._current_border = final_border
        self._bg_animation = None

    def _apply_badge_style(self, background: str, border: str) -> None:
        """Застосовує CSS-стиль з конкретними кольорами."""
        self.setStyleSheet(
            f"background: {background}; color: {border}; "
            "border-radius: 10px; border: 1px solid "
            f"{border}; padding: 3px 10px; font-weight: 700;"
        )


def _mix_hex(start_hex: str, end_hex: str, progress: float) -> str:
    """Змішує два hex-кольори за прогресом [0..1]. Mixes two hex colors by progress."""
    start = QColor(start_hex)
    end = QColor(end_hex)
    ratio = max(0.0, min(1.0, progress))
    red = round(start.red() + (end.red() - start.red()) * ratio)
    green = round(start.green() + (end.green() - start.green()) * ratio)
    blue = round(start.blue() + (end.blue() - start.blue()) * ratio)
    return QColor(red, green, blue).name()
