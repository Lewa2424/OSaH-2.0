"""
pulse — нескінченна пульсуюча opacity-анімація для привернення уваги.
Infinite pulsing opacity animation to draw user attention.
"""
from PySide6.QtCore import QEasingCurve, QPropertyAnimation, QSequentialAnimationGroup
from PySide6.QtWidgets import QGraphicsOpacityEffect, QWidget


def apply_pulse(widget: QWidget, min_opacity: float = 0.35, beat_ms: int = 850) -> QSequentialAnimationGroup:
    """
    Запускає нескінченний пульс opacity (1.0 → min_opacity → 1.0 ...) на widget.
    Starts an infinite opacity pulse (1.0 → min_opacity → 1.0 ...) on the widget.
    """
    stop_pulse(widget)

    effect = QGraphicsOpacityEffect(widget)
    effect.setOpacity(1.0)
    widget.setGraphicsEffect(effect)

    fade_out = QPropertyAnimation(effect, b"opacity")
    fade_out.setDuration(beat_ms)
    fade_out.setStartValue(1.0)
    fade_out.setEndValue(min_opacity)
    fade_out.setEasingCurve(QEasingCurve.Type.InOutSine)

    fade_in = QPropertyAnimation(effect, b"opacity")
    fade_in.setDuration(beat_ms)
    fade_in.setStartValue(min_opacity)
    fade_in.setEndValue(1.0)
    fade_in.setEasingCurve(QEasingCurve.Type.InOutSine)

    group = QSequentialAnimationGroup(widget)
    group.addAnimation(fade_out)
    group.addAnimation(fade_in)
    group.setLoopCount(-1)
    group.start()

    widget._pulse_group = group
    return group


def stop_pulse(widget: QWidget) -> None:
    """
    Зупиняє пульс і прибирає графічний ефект.
    Stops the pulse and removes the graphics effect.
    """
    group = getattr(widget, "_pulse_group", None)
    if group is not None:
        group.stop()
        widget._pulse_group = None
    widget.setGraphicsEffect(None)
