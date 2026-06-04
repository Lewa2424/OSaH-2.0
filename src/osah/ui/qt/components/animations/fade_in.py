"""
fade_in — утиліта для анімації появи widgets.
Utility for fade-in appearance animation of widgets.
"""
from PySide6.QtCore import QEasingCurve, QPropertyAnimation
from PySide6.QtWidgets import QGraphicsOpacityEffect, QWidget

from osah.ui.qt.design.tokens import ANIMATION


def apply_fade_in(widget: QWidget, duration: int = ANIMATION["normal"]) -> QPropertyAnimation:
    """
    Застосовує fade-in opacity ефект до widget.
    Applies a fade-in opacity effect to the widget.

    Починає з opacity 0.0, плавно підіймає до 1.0 за duration мс,
    після завершення знімає QGraphicsEffect щоб не навантажувати рендер.
    """
    effect = QGraphicsOpacityEffect(widget)
    effect.setOpacity(0.0)
    widget.setGraphicsEffect(effect)

    animation = QPropertyAnimation(effect, b"opacity", widget)
    animation.setDuration(duration)
    animation.setStartValue(0.0)
    animation.setEndValue(1.0)
    animation.setEasingCurve(QEasingCurve.Type.OutQuart)
    animation.finished.connect(lambda: _remove_effect(widget))
    animation.start()

    widget._fade_animation = animation
    return animation


def _remove_effect(widget: QWidget) -> None:
    """
    Знімає QGraphicsEffect після завершення анімації.
    Removes QGraphicsEffect after animation completes.
    """
    try:
        widget.setGraphicsEffect(None)
    except RuntimeError:
        pass
