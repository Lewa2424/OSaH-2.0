"""
Scrollable table frame with top horizontal controls.
"""

from pathlib import Path

from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QHBoxLayout, QPushButton, QScrollBar, QTableWidget, QVBoxLayout, QWidget

from osah.ui.qt.design.tokens import COLOR, RADIUS, SPACING


_ICON_DIR = Path(__file__).resolve().parents[1] / "assets" / "icons"


class ScrollableTableFrame(QWidget):
    """Wrapper that adds a top scrollbar and column-step buttons to a table."""

    def __init__(self, table: QTableWidget, snap_to_columns: bool = False) -> None:
        super().__init__()
        self._table = table
        self._is_syncing = False
        self._snap_to_columns = snap_to_columns

        self._table.setHorizontalScrollMode(QTableWidget.ScrollMode.ScrollPerPixel)
        self._style_native_scrollbar()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(SPACING["xs"])

        controls = QWidget()
        controls.setObjectName("tableScrollControls")
        controls_layout = QHBoxLayout(controls)
        controls_layout.setContentsMargins(0, 0, 0, 0)
        controls_layout.setSpacing(SPACING["sm"])

        self._left_button = self._create_scroll_button("left")
        self._left_button.clicked.connect(self._scroll_previous_column)
        controls_layout.addWidget(self._left_button)

        self._top_scrollbar = QScrollBar(Qt.Orientation.Horizontal)
        self._top_scrollbar.setObjectName("tableTopScrollBar")
        self._top_scrollbar.setMinimumHeight(12)
        self._top_scrollbar.setStyleSheet(_build_scrollbar_style())
        self._top_scrollbar.valueChanged.connect(self._sync_table_scrollbar)
        controls_layout.addWidget(self._top_scrollbar, stretch=1)

        self._right_button = self._create_scroll_button("right")
        self._right_button.clicked.connect(self._scroll_next_column)
        controls_layout.addWidget(self._right_button)

        layout.addWidget(controls)
        layout.addWidget(self._table, stretch=1)

        native_scrollbar = self._table.horizontalScrollBar()
        native_scrollbar.rangeChanged.connect(self._sync_top_range)
        native_scrollbar.valueChanged.connect(self._sync_top_value)
        self._sync_top_range(native_scrollbar.minimum(), native_scrollbar.maximum())
        self._sync_top_value(native_scrollbar.value())

    def table(self) -> QTableWidget:
        """###### ТАБЛИЦЯ / TABLE ######

        Повертає таблицю, яку обгортає компонент.
        Returns the table wrapped by this component.
        """

        return self._table

    def _create_scroll_button(self, direction: str) -> QPushButton:
        """###### КНОПКА ПРОКРУТКИ / SCROLL BUTTON ######

        Створює компактну кнопку з напрямком горизонтальної прокрутки.
        Creates a compact button for horizontal scroll direction.
        """

        button = QPushButton()
        button.setFixedSize(28, 28)
        button.setIcon(_build_scroll_icon(direction))
        button.setIconSize(QSize(22, 22))
        button.setCursor(Qt.CursorShape.PointingHandCursor)
        button.setObjectName("tableScrollButton")
        button.setStyleSheet(_build_scroll_button_style())
        return button

    def _style_native_scrollbar(self) -> None:
        """###### НИЖНІЙ SCROLLBAR / NATIVE SCROLLBAR ######

        Робить штатний нижній scrollbar трохи товщим тільки для цієї таблиці.
        Makes the native bottom scrollbar slightly thicker only for this table.
        """

        self._table.horizontalScrollBar().setMinimumHeight(11)
        self._table.horizontalScrollBar().setStyleSheet(_build_scrollbar_style())

    def _sync_top_range(self, minimum: int, maximum: int) -> None:
        """###### СИНХРОНІЗАЦІЯ ДІАПАЗОНУ / RANGE SYNC ######

        Синхронізує діапазон верхнього scrollbar зі штатним scrollbar таблиці.
        Syncs the top scrollbar range with the table scrollbar range.
        """

        self._top_scrollbar.setRange(minimum, maximum)
        self._top_scrollbar.setPageStep(self._table.horizontalScrollBar().pageStep())
        self._update_button_state()

    def _sync_top_value(self, value: int) -> None:
        """###### СИНХРОНІЗАЦІЯ ЗНАЧЕННЯ / VALUE SYNC ######

        Передає поточну позицію нижнього scrollbar у верхній scrollbar.
        Mirrors the native scrollbar value to the top scrollbar.
        """

        if self._is_syncing:
            return
        self._is_syncing = True
        self._top_scrollbar.setValue(value)
        self._is_syncing = False
        self._update_button_state()

    def _sync_table_scrollbar(self, value: int) -> None:
        """###### ПРОКРУТКА ТАБЛИЦІ / TABLE SCROLL SYNC ######

        Передає позицію верхнього scrollbar у таблицю.
        Applies the top scrollbar value to the table scrollbar.
        """

        if self._is_syncing:
            return
        self._is_syncing = True
        self._table.horizontalScrollBar().setValue(value)
        self._is_syncing = False
        self._update_button_state()

    def _scroll_previous_column(self) -> None:
        """###### КОЛОНКА ЛІВОРУЧ / PREVIOUS COLUMN ######

        Зсуває таблицю приблизно на одну колонку ліворуч.
        Moves the table left by roughly one column width.
        """

        if self._snap_to_columns:
            self._scroll_to_adjacent_column(-1)
            return
        current = self._table.horizontalScrollBar().value()
        self._table.horizontalScrollBar().setValue(max(0, current - self._current_column_step()))

    def _scroll_next_column(self) -> None:
        """###### КОЛОНКА ПРАВОРУЧ / NEXT COLUMN ######

        Зсуває таблицю приблизно на одну колонку праворуч.
        Moves the table right by roughly one column width.
        """

        if self._snap_to_columns:
            self._scroll_to_adjacent_column(1)
            return
        scrollbar = self._table.horizontalScrollBar()
        scrollbar.setValue(min(scrollbar.maximum(), scrollbar.value() + self._current_column_step()))

    def _current_column_step(self) -> int:
        """###### КРОК КОЛОНКИ / COLUMN STEP ######

        Обчислює крок прокрутки за шириною першої видимої колонки.
        Computes scroll step from the first visible column width.
        """

        offset = self._table.horizontalHeader().offset()
        width_sum = 0
        fallback_width = 120

        for column_index in range(self._table.columnCount()):
            column_width = self._table.columnWidth(column_index)
            if self._table.isColumnHidden(column_index):
                continue
            if width_sum + column_width > offset:
                return max(48, column_width)
            width_sum += column_width

        return fallback_width

    def _scroll_to_adjacent_column(self, direction: int) -> None:
        """###### ПРОКРУТКА ДО СУСІДНЬОЇ КОЛОНКИ / SCROLL TO ADJACENT COLUMN ######

        Зсуває таблицю до початку попередньої або наступної видимої колонки.
        Moves the table to the start of the previous or next visible column.
        """

        header = self._table.horizontalHeader()
        visible_columns = [index for index in range(self._table.columnCount()) if not self._table.isColumnHidden(index)]
        if not visible_columns:
            return

        current_column = self._first_visible_column_index()
        if current_column not in visible_columns:
            current_column = visible_columns[0]
        current_position = visible_columns.index(current_column)
        target_position = max(0, min(len(visible_columns) - 1, current_position + direction))
        target_column = visible_columns[target_position]
        self._table.horizontalScrollBar().setValue(header.sectionPosition(target_column))

    def _first_visible_column_index(self) -> int:
        """###### ПЕРША ВИДИМА КОЛОНКА / FIRST VISIBLE COLUMN ######

        Повертає індекс першої колонки, яка хоча б частково видима у viewport таблиці.
        Returns the index of the first column at least partially visible in the table viewport.
        """

        header = self._table.horizontalHeader()
        viewport_width = self._table.viewport().width()
        fallback_column = 0

        for column_index in range(self._table.columnCount()):
            if self._table.isColumnHidden(column_index):
                continue
            fallback_column = column_index
            position = header.sectionViewportPosition(column_index)
            width = self._table.columnWidth(column_index)
            if position + width > 0 and position < viewport_width:
                return column_index

        return fallback_column

    def _update_button_state(self) -> None:
        """###### СТАН КНОПОК / BUTTON STATE ######

        Оновлює активність кнопок за поточною позицією горизонтальної прокрутки.
        Updates button availability from the current horizontal scroll position.
        """

        scrollbar = self._table.horizontalScrollBar()
        self._left_button.setEnabled(scrollbar.value() > scrollbar.minimum())
        self._right_button.setEnabled(scrollbar.value() < scrollbar.maximum())


def _build_scrollbar_style() -> str:
    """###### СТИЛЬ SCROLLBAR / SCROLLBAR STYLE ######"""

    return (
        f"QScrollBar:horizontal {{ background: {COLOR['bg_panel']}; height: 11px; border-radius: 5px; }}"
        f"QScrollBar::handle:horizontal {{ background: {COLOR['accent']}; border-radius: 5px; min-width: 48px; }}"
        f"QScrollBar::handle:horizontal:hover {{ background: {COLOR['accent_hover']}; }}"
        "QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal { width: 0px; }"
        "QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal { background: transparent; }"
    )


def _build_scroll_button_style() -> str:
    """###### СТИЛЬ КНОПКИ ПРОКРУТКИ / SCROLL BUTTON STYLE ######"""

    return (
        f"QPushButton#tableScrollButton {{ background: {COLOR['text_primary']}; color: {COLOR['text_on_accent']}; "
        f"border: 1px solid {COLOR['text_primary']}; border-radius: 14px; padding: 0px; }}"
        f"QPushButton#tableScrollButton:hover {{ background: {COLOR['accent_hover']}; border-color: {COLOR['accent_hover']}; }}"
        f"QPushButton#tableScrollButton:pressed {{ background: {COLOR['accent_active']}; }}"
        f"QPushButton#tableScrollButton:disabled {{ background: {COLOR['bg_panel']}; color: {COLOR['text_muted']}; "
        f"border: 1px solid {COLOR['border_soft']}; }}"
    )


def _build_scroll_icon(direction: str) -> QIcon:
    """###### ІКОНКА ПРОКРУТКИ / SCROLL ICON ######"""

    icon = QIcon()
    icon.addFile(str(_ICON_DIR / f"chevron_{direction}_white.svg"), QSize(22, 22), QIcon.Mode.Normal)
    icon.addFile(str(_ICON_DIR / f"chevron_{direction}_muted.svg"), QSize(22, 22), QIcon.Mode.Disabled)
    return icon
