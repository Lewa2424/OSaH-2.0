from html import escape

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QAbstractItemView, QHeaderView, QLabel, QTableWidget

from osah.domain.entities.news_item import NewsItem
from osah.domain.entities.news_item_read_state import NewsItemReadState
from osah.domain.services.build_news_source_display_name import build_news_source_display_name
from osah.domain.services.format_ui_datetime import format_ui_datetime
from osah.ui.qt.components.sortable_table_widget_item import ROW_KEY_ROLE, SortableTableWidgetItem


class NewsItemsTable(QTableWidget):
    """Table of cached NPA/news materials with interactive column sorting."""

    item_selected = Signal(int)

    def __init__(self) -> None:
        super().__init__(0, 2)
        self._rows_by_key: dict[str, NewsItem] = {}
        self._default_sort_column = 0
        self.setHorizontalHeaderLabels(("Дата", "Матеріал"))
        self.setStyleSheet("QTableWidget { font-size: 16px; }")
        self.verticalHeader().setVisible(False)
        self.setAlternatingRowColors(True)
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.setWordWrap(True)
        self.setSortingEnabled(True)
        self.setShowGrid(False)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        header = self.horizontalHeader()
        header_font = QFont(header.font())
        header_font.setPointSize(max(18, header_font.pointSize() * 2))
        header.setFont(header_font)
        header.setDefaultAlignment(Qt.AlignmentFlag.AlignCenter)
        header.setStretchLastSection(False)
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSortIndicatorShown(True)
        header.setSortIndicator(self._default_sort_column, Qt.SortOrder.DescendingOrder)
        for column_index in range(self.columnCount()):
            header_item = self.horizontalHeaderItem(column_index)
            if header_item is not None:
                header_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.itemSelectionChanged.connect(self._emit_selected_item)

    def set_items(self, news_items: tuple[NewsItem, ...]) -> None:
        """Fills the table with items from the external cache."""

        sort_column = self.horizontalHeader().sortIndicatorSection()
        sort_order = self.horizontalHeader().sortIndicatorOrder()
        self.blockSignals(True)
        self.setSortingEnabled(False)
        self._rows_by_key = {str(item.item_id): item for item in news_items}
        self.clearSelection()
        self.setRowCount(len(news_items))

        for row_index, news_item in enumerate(news_items):
            published_text = format_ui_datetime(news_item.published_at_text)
            published_item = SortableTableWidgetItem(
                published_text,
                row_key=str(news_item.item_id),
                sort_value=news_item.published_at_text,
            )
            published_item.setFlags(published_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            published_item.setToolTip(_build_item_tooltip(news_item, 0))
            published_item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            self.setItem(row_index, 0, published_item)

            preview_item = SortableTableWidgetItem(
                _build_news_preview_text(news_item),
                row_key=str(news_item.item_id),
                sort_value=_build_news_preview_text(news_item),
            )
            preview_item.setFlags(preview_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            preview_item.setToolTip(_build_item_tooltip(news_item, 1))
            preview_item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            self.setItem(row_index, 1, preview_item)
            self.setCellWidget(row_index, 1, _build_news_preview_widget(news_item))
            self._apply_row_visual_state(row_index, news_item)
            self.setRowHeight(row_index, 92)

        self.setSortingEnabled(True)
        self.sortItems(sort_column if sort_column >= 0 else self._default_sort_column, sort_order)
        self.blockSignals(False)

    def mark_item_as_read(self, item_id: int) -> None:
        """Updates local row state after the material has been viewed."""

        news_item = self._rows_by_key.get(str(item_id))
        if news_item is None:
            return
        news_item.read_state = NewsItemReadState.READ
        for row_index in range(self.rowCount()):
            item = self.item(row_index, 0)
            if item is None or item.data(ROW_KEY_ROLE) != str(item_id):
                continue
            preview_item = self.item(row_index, 1)
            if preview_item is not None:
                preview_item.setToolTip(_build_item_tooltip(news_item, 1))
            preview_widget = self.cellWidget(row_index, 1)
            if isinstance(preview_widget, QLabel):
                preview_widget.setText(_build_news_preview_html(news_item))
            self._apply_row_visual_state(row_index, news_item)
            return

    def current_news_item(self) -> NewsItem | None:
        """Returns the selected item or None."""

        selected_rows = self.selectionModel().selectedRows()
        if not selected_rows:
            return None
        item = self.item(selected_rows[0].row(), 0)
        if item is None:
            return None
        return self._rows_by_key.get(str(item.data(ROW_KEY_ROLE)))

    def _emit_selected_item(self) -> None:
        """Emits selected item id for screen detail actions."""

        current_item = self.current_news_item()
        if current_item is not None:
            self.item_selected.emit(current_item.item_id)

    def _apply_row_visual_state(self, row_index: int, news_item: NewsItem) -> None:
        """Applies row text color depending on read state."""

        text_color = Qt.GlobalColor.darkGreen if news_item.read_state == NewsItemReadState.NEW else Qt.GlobalColor.black
        for column_index in range(self.columnCount()):
            item = self.item(row_index, column_index)
            if item is not None:
                item.setForeground(text_color)
        preview_widget = self.cellWidget(row_index, 1)
        if isinstance(preview_widget, QLabel):
            color_hex = "#006400" if news_item.read_state == NewsItemReadState.NEW else "#111827"
            preview_widget.setStyleSheet(
                f"color: {color_hex}; font-size: 16px; padding: 10px 12px; background: transparent;"
            )


def _build_news_preview_text(news_item: NewsItem) -> str:
    source_prefix = "НПА" if news_item.source_kind.value == "npa" else "Новина"
    preview_title = (news_item.title_text or "Без заголовка").strip()
    display_source_name = build_news_source_display_name(news_item.source_name)
    return (
        f"{source_prefix} ({display_source_name})\n"
        f"{preview_title}\n"
        "(Для перегляду повної новини відкрийте посилання нижче.)"
    )


def _build_news_preview_html(news_item: NewsItem) -> str:
    source_prefix = "НПА" if news_item.source_kind.value == "npa" else "Новина"
    display_source_name = build_news_source_display_name(news_item.source_name)
    preview_title = escape((news_item.title_text or "Без заголовка").strip())
    return (
        f"<div>"
        f"<div><span>{escape(source_prefix)} ({escape(display_source_name)})</span></div>"
        f"<div>{preview_title}</div>"
        "<div><i>(Для перегляду повної новини відкрийте посилання нижче.)</i></div>"
        "</div>"
    )


def _build_news_preview_widget(news_item: NewsItem) -> QLabel:
    preview_label = QLabel()
    preview_label.setWordWrap(True)
    preview_label.setTextFormat(Qt.TextFormat.RichText)
    preview_label.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)
    preview_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
    preview_label.setText(_build_news_preview_html(news_item))
    return preview_label


def _build_item_tooltip(news_item: NewsItem, column_index: int) -> str:
    if column_index == 0:
        return format_ui_datetime(news_item.published_at_text)
    return f"{_build_news_preview_text(news_item)}\n\nПосилання: {news_item.link_url}"
