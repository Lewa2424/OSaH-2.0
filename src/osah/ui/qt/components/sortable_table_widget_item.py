from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QTableWidgetItem


ROW_KEY_ROLE = Qt.ItemDataRole.UserRole
SORT_VALUE_ROLE = Qt.ItemDataRole.UserRole + 1
MATCH_VALUE_ROLE = Qt.ItemDataRole.UserRole + 2


class SortableTableWidgetItem(QTableWidgetItem):
    """Table item with explicit row identity and stable sort value."""

    def __init__(
        self,
        text: str,
        *,
        row_key: str,
        sort_value: object | None = None,
        match_value: object | None = None,
    ) -> None:
        super().__init__(text)
        self.setData(ROW_KEY_ROLE, row_key)
        self.setData(SORT_VALUE_ROLE, _normalize_sort_value(text if sort_value is None else sort_value))
        if match_value is not None:
            self.setData(MATCH_VALUE_ROLE, match_value)

    def __lt__(self, other: QTableWidgetItem) -> bool:
        left_value = self.data(SORT_VALUE_ROLE)
        right_value = other.data(SORT_VALUE_ROLE)
        try:
            return left_value < right_value
        except TypeError:
            return str(left_value) < str(right_value)


def _normalize_sort_value(value: object) -> object:
    if isinstance(value, str):
        return value.casefold()
    return value
