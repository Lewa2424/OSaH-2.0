from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QLabel, QVBoxLayout

from osah.domain.entities.news_item import NewsItem
from osah.domain.entities.news_source_kind import NewsSourceKind
from osah.domain.services.build_news_source_display_name import build_news_source_display_name
from osah.domain.services.format_ui_datetime import format_ui_datetime
from osah.ui.qt.design.tokens import COLOR, RADIUS, SPACING


class NewsItemDetailPanel(QFrame):
    """Панель детального перегляду вибраного матеріалу новин/НПА.
    Detail panel for the selected news/NPA item.
    """

    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("newsItemDetailPanel")
        self.setStyleSheet(
            f"""
            QFrame#newsItemDetailPanel {{
                background: {COLOR['bg_card']};
                border: 1px solid {COLOR['border_soft']};
                border-radius: {RADIUS['lg']}px;
            }}
            QLabel#newsDetailMeta {{
                color: {COLOR['text_secondary']};
                font-size: 13px;
                font-weight: 600;
            }}
            QLabel#newsDetailTitle {{
                color: {COLOR['text_primary']};
                font-size: 20px;
                font-weight: 700;
            }}
            QLabel#newsDetailBody {{
                color: {COLOR['text_secondary']};
                font-size: 15px;
                line-height: 1.35em;
            }}
            QLabel#newsDetailLink {{
                color: {COLOR['status_info']};
                font-size: 15px;
                font-weight: 600;
            }}
            """
        )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(SPACING["lg"], SPACING["lg"], SPACING["lg"], SPACING["lg"])
        layout.setSpacing(SPACING["sm"])

        self._meta_label = QLabel()
        self._meta_label.setObjectName("newsDetailMeta")
        self._meta_label.setWordWrap(True)
        layout.addWidget(self._meta_label)

        self._title_label = QLabel()
        self._title_label.setObjectName("newsDetailTitle")
        self._title_label.setWordWrap(True)
        self._title_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        layout.addWidget(self._title_label)

        self._body_label = QLabel()
        self._body_label.setObjectName("newsDetailBody")
        self._body_label.setWordWrap(True)
        self._body_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        layout.addWidget(self._body_label)

        self._link_label = QLabel()
        self._link_label.setObjectName("newsDetailLink")
        self._link_label.setWordWrap(True)
        self._link_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        layout.addWidget(self._link_label)

        self.show_placeholder()

    def set_item(self, news_item: NewsItem) -> None:
        """Показує деталі вибраного матеріалу у зрозумілому текстовому вигляді.
        Shows selected item details in a clear text layout.
        """

        kind_label = "НПА" if news_item.source_kind == NewsSourceKind.NPA else "Новина"
        published_label = format_ui_datetime(news_item.published_at_text)
        display_source_name = build_news_source_display_name(news_item.source_name)

        self._meta_label.setText(
            f"{kind_label} ({display_source_name}) • {published_label}"
        )
        self._title_label.setText(news_item.title_text or "Без заголовка")
        self._body_label.clear()
        self._link_label.setText(news_item.link_url or "Посилання відсутнє")

    def show_placeholder(self) -> None:
        """Показує нейтральний стан, коли матеріал ще не вибрано.
        Shows a neutral state when no item is selected yet.
        """

        self._meta_label.setText("Виберіть матеріал у списку вверху.")
        self._title_label.setText("Деталі новини з'являться тут.")
        self._body_label.clear()
        self._link_label.setText("Посилання з'явиться після вибору матеріалу.")
