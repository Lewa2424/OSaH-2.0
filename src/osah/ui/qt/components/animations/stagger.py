"""
stagger — покрокова анімація появи групи widget.
Staggered fade-in animation for a group of widgets.
"""
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QWidget

from osah.ui.qt.components.animations.fade_in import apply_fade_in


def apply_stagger(widgets: list[QWidget], step_ms: int = 60, duration: int | None = None) -> None:
    """
    Послідовно запускає fade-in для кожного widget із затримкою step_ms між ними.
    Sequentially fades in each widget with step_ms delay between each one.
    """
    for index, widget in enumerate(widgets):
        delay = index * step_ms
        if duration is not None:
            QTimer.singleShot(delay, lambda w=widget, d=duration: apply_fade_in(w, d))
        else:
            QTimer.singleShot(delay, lambda w=widget: apply_fade_in(w))
