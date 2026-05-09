from html import escape

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QAbstractItemView, QHeaderView, QLabel, QTableWidget, QTableWidgetItem

from osah.domain.entities.news_item import NewsItem
from osah.domain.entities.news_item_read_state import NewsItemReadState
from osah.domain.services.build_news_source_display_name import build_news_source_display_name
from osah.domain.services.format_ui_datetime import format_ui_datetime


class NewsItemsTable(QTableWidget):
    """Таблиця кешованих матеріалів НПА та новин зі статусом прочитання.
    Table of cached NPA/news materials with read state.
    """

    item_selected = Signal(int)

    def __init__(self) -> None:
        super().__init__(0, 2)
        self._rows: tuple[NewsItem, ...] = ()
        self.setHorizontalHeaderLabels(("Дата", "Матеріал"))
        self.setStyleSheet("QTableWidget { font-size: 16px; }")
        self.verticalHeader().setVisible(False)
        self.setAlternatingRowColors(True)
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.setWordWrap(True)
        self.setSortingEnabled(False)
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
        for column_index in range(self.columnCount()):
            header_item = self.horizontalHeaderItem(column_index)
            if header_item is not None:
                header_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.itemSelectionChanged.connect(self._emit_selected_item)

    def set_items(self, news_items: tuple[NewsItem, ...]) -> None:
        """Заповнює таблицю матеріалами із зовнішнього кешу.
        Fills the table with items from the external cache.
        """

        self.blockSignals(True)
        self._rows = news_items
        self.clearSelection()
        self.setRowCount(len(news_items))
        for row_index, news_item in enumerate(news_items):
            values = (
                format_ui_datetime(news_item.published_at_text),
                "",
            )
            for column_index, value in enumerate(values):
                item = QTableWidgetItem(value)
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                item.setToolTip(_build_item_tooltip(news_item, column_index))
                item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
                self.setItem(row_index, column_index, item)
            self.setCellWidget(row_index, 1, _build_news_preview_widget(news_item))
            self._apply_row_visual_state(row_index, news_item)
            self.setRowHeight(row_index, 92)
        self.blockSignals(False)

    def mark_item_as_read(self, item_id: int) -> None:
        """Оновлює локальний стан рядка після перегляду матеріалу.
        Updates local row state after the material has been viewed.
        """

        for row_index, news_item in enumerate(self._rows):
            if news_item.item_id != item_id:
                continue
            news_item.read_state = NewsItemReadState.READ
            preview_item = self.item(row_index, 1)
            if preview_item is not None:
                preview_item.setToolTip(_build_item_tooltip(news_item, 1))
            preview_widget = self.cellWidget(row_index, 1)
            if isinstance(preview_widget, QLabel):
                preview_widget.setText(_build_news_preview_html(news_item))
            self._apply_row_visual_state(row_index, news_item)
            return

    def current_news_item(self) -> NewsItem | None:
        """Повертає вибраний матеріал або None.
        Returns the selected item or None.
        """

        selected_rows = self.selectionModel().selectedRows()
        if not selected_rows:
            return None
        row_index = selected_rows[0].row()
        if row_index < 0 or row_index >= len(self._rows):
            return None
        return self._rows[row_index]

    def _emit_selected_item(self) -> None:
        """Передає id вибраного матеріалу для detail-actions екрана.
        Emits selected item id for screen detail actions.
        """

        current_item = self.current_news_item()
        if current_item is not None:
            self.item_selected.emit(current_item.item_id)

    def _apply_row_visual_state(self, row_index: int, news_item: NewsItem) -> None:
        """Застосовує колір тексту до рядка залежно від стану прочитання.
        Applies row text color depending on read state.
        """

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
    """Повертає багаторядковий preview матеріалу для спрощеного списку.
    Returns a multiline material preview for the simplified list.
    """

    source_prefix = "НПА" if news_item.source_kind.value == "npa" else "Новина"
    preview_title = (news_item.title_text or "Без заголовка").strip()
    display_source_name = build_news_source_display_name(news_item.source_name)
    return (
        f"{source_prefix} ({display_source_name})\n"
        f"{preview_title}\n"
        "(Для перегляду повної новини відкрийте посилання нижче.)"
    )


def _build_news_preview_html(news_item: NewsItem) -> str:
    """Повертає HTML-версію preview для багаторядкового rich-text відображення.
    Returns an HTML preview for multiline rich-text rendering.
    """

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
    """Створює QLabel для rich-text відображення основного блоку новини.
    Creates a QLabel for rich-text rendering of the main news block.
    """

    preview_label = QLabel()
    preview_label.setWordWrap(True)
    preview_label.setTextFormat(Qt.TextFormat.RichText)
    preview_label.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)
    preview_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
    preview_label.setText(_build_news_preview_html(news_item))
    return preview_label


def _build_item_tooltip(news_item: NewsItem, column_index: int) -> str:
    """Повертає tooltip з повним змістом осередку без втрати деталей.
    Returns a tooltip with full cell content without losing details.
    """

    if column_index == 0:
        return format_ui_datetime(news_item.published_at_text)
    return (
        f"{_build_news_preview_text(news_item)}\n\n"
        f"Посилання: {news_item.link_url}"
    )
