from PySide6.QtWidgets import QTableWidget


def ensure_table_column_width(table: QTableWidget, column_index: int, extra_padding: int = 28) -> None:
    """###### ШИРИНА КОЛОНКИ ТАБЛИЦІ / ENSURE TABLE COLUMN WIDTH ######

    Гарантує, що колонка таблиці достатньо широка для заголовка, тексту або cell-widget.
    Ensures that a table column is wide enough for its header, text, or cell widget.
    """

    header_item = table.horizontalHeaderItem(column_index)
    header_text = header_item.text() if header_item is not None else ""
    header_width = table.horizontalHeader().fontMetrics().horizontalAdvance(header_text) + extra_padding
    content_width = 0

    for row_index in range(table.rowCount()):
        widget = table.cellWidget(row_index, column_index)
        if widget is not None:
            content_width = max(content_width, widget.sizeHint().width() + extra_padding)
            continue

        item = table.item(row_index, column_index)
        if item is not None:
            item_width = table.fontMetrics().horizontalAdvance(item.text()) + extra_padding
            content_width = max(content_width, item_width)

    table.setColumnWidth(column_index, max(header_width, content_width))
