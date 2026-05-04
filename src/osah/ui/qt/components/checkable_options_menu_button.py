from collections.abc import Iterable

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QMenu, QPushButton

from osah.ui.qt.design.tokens import COLOR, RADIUS


class CheckableOptionsMenuButton(QPushButton):
    """Кнопка з popup-меню для множинного вибору прапорцями.
    Button with a popup menu for multiple checkbox-like selections.
    """

    values_changed = Signal(tuple)

    def __init__(self, title_text: str, option_values: Iterable[str]) -> None:
        super().__init__(title_text)
        self._title_text = title_text
        self._menu = QMenu(self)
        self._menu.setStyleSheet(_build_menu_stylesheet())
        self._actions_by_value: dict[str, object] = {}
        self.setProperty("variant", "secondary")
        self.clicked.connect(self._open_menu)
        self._build_actions(tuple(option_values))
        self._refresh_caption()

    def checked_values(self) -> tuple[str, ...]:
        """Повертає всі відмічені значення.
        Returns all checked values.
        """

        return tuple(
            value
            for value, action in self._actions_by_value.items()
            if action.isChecked()
        )

    def set_checked_values(self, values: Iterable[str]) -> None:
        """Встановлює перелік відмічених значень без зміни моделі даних.
        Sets the checked values list without changing the data model.
        """

        selected = set(values)
        changed = False
        for value, action in self._actions_by_value.items():
            should_be_checked = value in selected
            if action.isChecked() != should_be_checked:
                action.setChecked(should_be_checked)
                changed = True
        self._refresh_caption()
        if changed:
            self.values_changed.emit(self.checked_values())

    def clear_checked_values(self) -> None:
        """Знімає всі прапорці.
        Clears all checked values.
        """

        self.set_checked_values(())

    def _build_actions(self, option_values: tuple[str, ...]) -> None:
        for value in option_values:
            action = self._menu.addAction(value)
            action.setCheckable(True)
            action.toggled.connect(self._on_actions_changed)
            self._actions_by_value[value] = action

    def _open_menu(self) -> None:
        self._menu.popup(self.mapToGlobal(self.rect().bottomLeft()))

    def _on_actions_changed(self) -> None:
        self._refresh_caption()
        self.values_changed.emit(self.checked_values())

    def _refresh_caption(self) -> None:
        selected_count = len(self.checked_values())
        if selected_count <= 0:
            self.setText(self._title_text)
            return
        self.setText(f"{self._title_text}: {selected_count}")


def _build_menu_stylesheet() -> str:
    """Повертає локальний стиль popup-меню у палітрі застосунку.
    Returns local popup-menu styling in the application palette.
    """

    c = COLOR
    r = RADIUS
    return f"""
QMenu {{
    background: {c["bg_card"]};
    color: {c["text_primary"]};
    border: 1px solid {c["border_default"]};
    border-radius: {r["md"]}px;
    padding: 6px 0px;
}}
QMenu::item {{
    background: transparent;
    color: {c["text_primary"]};
    padding: 8px 14px 8px 14px;
    margin: 0px 4px;
    border-radius: {r["sm"]}px;
}}
QMenu::item:selected {{
    background: {c["selection_bg"]};
    color: {c["text_primary"]};
}}
QMenu::item:checked {{
    background: {c["accent_soft"]};
    color: {c["accent"]};
    font-weight: 700;
}}
QMenu::item:checked:selected {{
    background: {c["selection_bg"]};
    color: {c["accent_active"]};
}}
"""
