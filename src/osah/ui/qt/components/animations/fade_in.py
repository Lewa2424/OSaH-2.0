"""
fade_in — утиліта для анімації появи віджетів.
"""
from PySide6.QtCore import QEasingCurve, QPropertyAnimation
from PySide6.QtWidgets import QGraphicsOpacityEffect, QWidget

from osah.ui.qt.design.tokens import ANIMATION


def apply_fade_in(widget: QWidget, duration: int = ANIMATION["normal"]) -> QPropertyAnimation:
    """Застосовує ефект прояву (Opacity) до віджета.
    Applies fade-in opacity effect to the widget.
    """
    
    effect = QGraphicsOpacityEffect(widget)
    widget.setGraphicsEffect(effect)

    animation = QPropertyAnimation(effect, b"opacity")
    animation.setDuration(duration)
    animation.setStartValue(0.0)
    animation.setEndValue(1.0)
    animation.setEasingCurve(QEasingCurve.Type.OutCubic)
    animation.start()
    
    # Треба зберігати посилання на анімацію, щоб GC її не видалив до завершення
    widget._fade_animation = animation
    return animation
