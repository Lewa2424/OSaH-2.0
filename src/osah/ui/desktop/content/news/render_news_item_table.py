from tkinter import ttk
import customtkinter as ctk

from osah.domain.entities.news_item import NewsItem
from osah.domain.services.format_news_item_read_state_label import format_news_item_read_state_label
from osah.domain.services.format_news_source_kind_label import format_news_source_kind_label
from osah.ui.desktop.content.ctk_styles import CARD, label_title


# ###### ВІДОБРАЖЕННЯ РЕЄСТРУ НОВИННИХ МАТЕРІАЛІВ / ОТРИСОВКА РЕЕСТРА НОВОСТНЫХ МАТЕРИАЛОВ ######
def render_news_item_table(parent: ctk.CTkFrame, news_items: tuple[NewsItem, ...]) -> None:
    """Відображає локальний реєстр кешованих новин і матеріалів НПА.
    Отрисовывает локальный реестр кэшированных новостей и материалов НПА.
    """

    table_frame = ctk.CTkFrame(parent, **CARD)
    table_frame.pack(fill="both", expand=True, padx=24, pady=(0, 24))

    label_title(table_frame, "Кешовані матеріали").pack(anchor="w", padx=20, pady=(18, 0))

    columns = ("source", "kind", "state", "published", "title")
    tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=12)
    tree.heading("source", text="Джерело")
    tree.heading("kind", text="Тип")
    tree.heading("state", text="Стан")
    tree.heading("published", text="Дата")
    tree.heading("title", text="Заголовок")
    tree.column("source", width=180, anchor="w")
    tree.column("kind", width=90, anchor="w")
    tree.column("state", width=110, anchor="w")
    tree.column("published", width=180, anchor="w")
    tree.column("title", width=540, anchor="w")
    tree.pack(fill="both", expand=True, padx=4, pady=(12, 4))

    for news_item in news_items:
        tree.insert(
            "",
            "end",
            values=(
                news_item.source_name,
                format_news_source_kind_label(news_item.source_kind),
                format_news_item_read_state_label(news_item.read_state),
                news_item.published_at_text or "-",
                news_item.title_text,
            ),
        )
