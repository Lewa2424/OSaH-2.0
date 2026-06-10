"""
Глобальний захист від випадкової зміни QComboBox під час прокрутки форми.
Global guard against accidental QComboBox changes while scrolling a form.
"""
from PySide6.QtCore import QEvent, QObject, Qt
from PySide6.QtWidgets import QApplication, QComboBox, QScrollArea, QWidget


def combo_box_focus_policy_without_wheel() -> Qt.FocusPolicy:
    """Повертає політику фокусу без WheelFocus для QComboBox.
    Returns a focus policy without WheelFocus for QComboBox widgets.
    """
    return Qt.FocusPolicy(Qt.FocusPolicy.TabFocus | Qt.FocusPolicy.ClickFocus)


def find_scroll_area_viewport(widget: QWidget) -> QWidget | None:
    """Шукає viewport найближчого QScrollArea для перенаправлення колеса.
    Finds the nearest QScrollArea viewport to forward wheel events to.
    """
    parent = widget.parentWidget()
    while parent is not None:
        if isinstance(parent, QScrollArea):
            return parent.viewport()
        parent = parent.parentWidget()
    return None


def is_combo_box_popup_visible(combo_box: QComboBox) -> bool:
    """Перевіряє, чи відкритий випадаючий список QComboBox.
    Checks whether the QComboBox dropdown popup is currently open.
    """
    view = combo_box.view()
    return view is not None and view.isVisible()


class _ComboBoxWheelScrollGuard(QObject):
    """Блокує колесо для закритого QComboBox і передає прокрутку батьківській області.
    Blocks wheel events for closed QComboBox widgets and forwards scrolling to parents.
    """

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:  # type: ignore[override]
        if not isinstance(watched, QComboBox):
            return super().eventFilter(watched, event)

        if event.type() == QEvent.Type.Show:
            watched.setFocusPolicy(combo_box_focus_policy_without_wheel())
            return False

        if event.type() != QEvent.Type.Wheel or is_combo_box_popup_visible(watched):
            return super().eventFilter(watched, event)

        viewport = find_scroll_area_viewport(watched)
        if viewport is not None:
            QApplication.sendEvent(viewport, event)
        return True


_guard: _ComboBoxWheelScrollGuard | None = None


def install_combo_box_wheel_scroll_guard(application: QApplication) -> None:
    """Встановлює глобальний фільтр подій для всіх випадаючих списків.
    Installs a global event filter for all combo boxes in the application.
    """
    global _guard
    if _guard is not None:
        return

    _guard = _ComboBoxWheelScrollGuard(application)
    application.installEventFilter(_guard)
