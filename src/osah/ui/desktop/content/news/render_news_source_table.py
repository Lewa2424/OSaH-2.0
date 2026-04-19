from tkinter import ttk
import customtkinter as ctk

from osah.domain.entities.news_source import NewsSource
from osah.domain.services.format_news_source_kind_label import format_news_source_kind_label
from osah.ui.desktop.content.ctk_styles import CARD, label_title, label_body


# ###### ВІДОБРАЖЕННЯ РЕЄСТРУ ДЖЕРЕЛ НОВИН / ОТРИСОВКА РЕЕСТРА ИСТОЧНИКОВ НОВОСТЕЙ ######
def render_news_source_table(parent: ctk.CTkFrame, news_sources: tuple[NewsSource, ...]) -> None:
    """Відображає таблицю довірених джерел зовнішнього контуру.
    Отрисовывает таблицу доверенных источников внешнего контура.
    """

    table_frame = ctk.CTkFrame(parent, **CARD)
    table_frame.pack(fill="x", pady=(0, 20))

    label_title(table_frame, "Довірені джерела").pack(anchor="w", padx=20, pady=(18, 0))
    label_body(
        table_frame,
        "Перелік зовнішніх RSS/Atom-джерел, яким дозволено поповнювати локальний кеш новин і правових змін.",
        wraplength=640,
    ).pack(anchor="w", padx=20, pady=(8, 12))

    columns = ("name", "kind", "active", "checked", "url")
    tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=6)
    tree.heading("name", text="Назва")
    tree.heading("kind", text="Тип")
    tree.heading("active", text="Активне")
    tree.heading("checked", text="Остання перевірка")
    tree.heading("url", text="URL")
    tree.column("name", width=180, anchor="w")
    tree.column("kind", width=90, anchor="w")
    tree.column("active", width=90, anchor="w")
    tree.column("checked", width=180, anchor="w")
    tree.column("url", width=520, anchor="w")
    tree.pack(fill="x", padx=4, pady=(0, 4))

    for news_source in news_sources:
        tree.insert(
            "",
            "end",
            values=(
                news_source.source_name,
                format_news_source_kind_label(news_source.source_kind),
                "Так" if news_source.is_active else "Ні",
                news_source.last_checked_at_text or "-",
                news_source.source_url,
            ),
        )
