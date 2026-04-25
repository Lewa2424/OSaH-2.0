from PySide6.QtCore import Signal
from PySide6.QtWidgets import QComboBox, QFormLayout, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget

from osah.domain.entities.news_source import NewsSource
from osah.domain.entities.news_source_kind import NewsSourceKind
from osah.ui.qt.components.scrollable_table_frame import ScrollableTableFrame


class NewsSourcesPanel(QWidget):
    """Панель довірених джерел НПА та новин.
    Panel for trusted NPA/news sources.
    """

    create_source_requested = Signal(str, str, str)
    refresh_requested = Signal()

    def __init__(self) -> None:
        super().__init__()
        layout = QVBoxLayout(self)

        self.sources_table = QTableWidget(0, 5)
        self.sources_table.setHorizontalHeaderLabels(("Назва", "Тип", "Активне", "Довірене", "Остання перевірка"))
        self.sources_table.verticalHeader().setVisible(False)
        layout.addWidget(ScrollableTableFrame(self.sources_table))

        form = QFormLayout()
        self.source_name = QLineEdit()
        self.source_url = QLineEdit()
        self.source_kind = QComboBox()
        self.source_kind.addItem("Новини", NewsSourceKind.NEWS.value)
        self.source_kind.addItem("НПА", NewsSourceKind.NPA.value)
        form.addRow("Назва", self.source_name)
        form.addRow("URL", self.source_url)
        form.addRow("Тип", self.source_kind)
        layout.addLayout(form)

        create_button = QPushButton("Додати довірене джерело")
        create_button.clicked.connect(self._emit_create_source)
        layout.addWidget(create_button)

        refresh_button = QPushButton("Перевірити джерела")
        refresh_button.clicked.connect(self.refresh_requested.emit)
        layout.addWidget(refresh_button)

    # ###### ВСТАНОВЛЕННЯ ДЖЕРЕЛ / SET SOURCES ######
    def set_sources(self, news_sources: tuple[NewsSource, ...]) -> None:
        """Показує список довірених джерел і дату останньої перевірки.
        Shows trusted sources and last check time.
        """

        self.sources_table.setRowCount(len(news_sources))
        for row_index, source in enumerate(news_sources):
            values = (
                source.source_name,
                source.source_kind.value.upper(),
                "так" if source.is_active else "ні",
                "так" if source.is_trusted else "ні",
                source.last_checked_at_text or "-",
            )
            for column_index, value in enumerate(values):
                self.sources_table.setItem(row_index, column_index, QTableWidgetItem(value))

    # ###### СТВОРЕННЯ ДЖЕРЕЛА / CREATE SOURCE ######
    def _emit_create_source(self) -> None:
        """Передає дані нового довіреного джерела у screen-level сервіс.
        Sends new trusted source data to the screen-level service call.
        """

        self.create_source_requested.emit(
            self.source_name.text(),
            self.source_url.text(),
            str(self.source_kind.currentData()),
        )
