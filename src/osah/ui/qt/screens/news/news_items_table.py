from PySide6.QtCore import Signal
from PySide6.QtWidgets import QAbstractItemView, QHeaderView, QTableWidget, QTableWidgetItem

from osah.domain.entities.news_item import NewsItem
from osah.domain.entities.news_item_read_state import NewsItemReadState


class NewsItemsTable(QTableWidget):
    """Таблиця кешованих матеріалів НПА та новин зі статусом прочитання.
    Table of cached NPA/news materials with read state.
    """

    item_selected = Signal(int)

    def __init__(self) -> None:
        super().__init__(0, 6)
        self._rows: tuple[NewsItem, ...] = ()
        self.setHorizontalHeaderLabels(("Статус", "Тип", "Джерело", "Дата", "Заголовок", "Посилання"))
        self.verticalHeader().setVisible(False)
        self.setAlternatingRowColors(True)
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.itemSelectionChanged.connect(self._emit_selected_item)

    # ###### ВСТАНОВЛЕННЯ МАТЕРІАЛІВ / SET ITEMS ######
    def set_items(self, news_items: tuple[NewsItem, ...]) -> None:
        """Заповнює таблицю матеріалами із зовнішнього кешу.
        Fills the table with items from the external cache.
        """

        self._rows = news_items
        self.setRowCount(len(news_items))
        for row_index, news_item in enumerate(news_items):
            values = (
                _read_state_label(news_item.read_state),
                news_item.source_kind.value.upper(),
                news_item.source_name,
                news_item.published_at_text,
                news_item.title_text,
                news_item.link_url,
            )
            for column_index, value in enumerate(values):
                self.setItem(row_index, column_index, QTableWidgetItem(value))

    # ###### ПОТОЧНИЙ МАТЕРІАЛ / CURRENT ITEM ######
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

    # ###### СИГНАЛ ВИБОРУ / SELECTION SIGNAL ######
    def _emit_selected_item(self) -> None:
        """Передає id вибраного матеріалу для detail-actions екрана.
        Emits selected item id for screen detail actions.
        """

        current_item = self.current_news_item()
        if current_item is not None:
            self.item_selected.emit(current_item.item_id)


# ###### МІТКА ПРОЧИТАННЯ / READ STATE LABEL ######
def _read_state_label(read_state: NewsItemReadState) -> str:
    """Перетворює внутрішній статус прочитання на коротку UI-мітку.
    Converts internal read state to a short UI label.
    """

    if read_state == NewsItemReadState.READ:
        return "прочитано"
    return "нове"
