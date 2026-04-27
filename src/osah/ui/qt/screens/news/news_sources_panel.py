from PySide6.QtWidgets import QAbstractItemView, QLabel, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget

from osah.domain.entities.news_source import NewsSource
from osah.ui.qt.components.scrollable_table_frame import ScrollableTableFrame


class NewsSourcesPanel(QWidget):
    """Панель перегляду довірених джерел НПА та новин (тільки перегляд).
    Read-only panel displaying trusted NPA/news sources list.
    """

    def __init__(self) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        hint = QLabel("Керування джерелами — у розділі «Налаштування».")
        hint.setProperty("role", "hint_label")
        layout.addWidget(hint)

        self.sources_table = QTableWidget(0, 4)
        self.sources_table.setHorizontalHeaderLabels(("Назва", "Тип", "Активно", "Стан перевірки"))
        self.sources_table.verticalHeader().setVisible(False)
        self.sources_table.horizontalHeader().setStretchLastSection(True)
        self.sources_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.sources_table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.sources_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        layout.addWidget(ScrollableTableFrame(self.sources_table))

    # ###### ВСТАНОВЛЕННЯ ДЖЕРЕЛ / SET SOURCES ######
    def set_sources(self, news_sources: tuple[NewsSource, ...]) -> None:
        """Показує список довірених джерел і дату останньої перевірки.
        Shows trusted sources and last check time.
        """

        self.sources_table.setRowCount(len(news_sources))
        kind_map = {"npa": "НПА", "news": "Новини"}
        for row_index, source in enumerate(news_sources):
            values = (
                source.source_name,
                kind_map.get(source.source_kind.value, source.source_kind.value.upper()),
                "так" if source.is_active else "ні",
                source.last_checked_at_text or "ще не перевірялось",
            )
            for column_index, value in enumerate(values):
                self.sources_table.setItem(row_index, column_index, QTableWidgetItem(value))
        self.sources_table.resizeColumnsToContents()
