"""
count_up — анімований числовий лічильник для QLabel.
Animated integer counter for QLabel widgets.
"""
from PySide6.QtCore import QEasingCurve, QVariantAnimation
from PySide6.QtWidgets import QLabel

from osah.ui.qt.design.tokens import ANIMATION


def apply_count_up(label: QLabel, from_value: int, to_value: int, duration: int = ANIMATION["slow"]) -> QVariantAnimation:
    """
    Анімує числове значення QLabel від from_value до to_value за duration мс.
    Animates a QLabel numeric value from from_value to to_value over duration ms.
    """
    existing = getattr(label, "_count_up_anim", None)
    if existing is not None:
        existing.stop()

    animation = QVariantAnimation(label)
    animation.setDuration(duration)
    animation.setStartValue(float(from_value))
    animation.setEndValue(float(to_value))
    animation.setEasingCurve(QEasingCurve.Type.OutQuart)
    animation.valueChanged.connect(lambda v: label.setText(str(round(float(v)))))
    animation.start()

    label._count_up_anim = animation
    return animation
