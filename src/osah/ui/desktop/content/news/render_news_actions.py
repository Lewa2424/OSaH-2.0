from pathlib import Path
from tkinter import StringVar, ttk
import customtkinter as ctk

from osah.domain.entities.news_item import NewsItem
from osah.ui.desktop.content.news.build_mark_news_item_as_read_handler import build_mark_news_item_as_read_handler
from osah.ui.desktop.content.news.build_news_item_options import build_news_item_options
from osah.ui.desktop.content.news.build_refresh_news_sources_handler import build_refresh_news_sources_handler
from osah.ui.desktop.content.ctk_styles import CARD, BTN, BTN_SEC, label_title, label_body


# ###### ВІДОБРАЖЕННЯ ДІЙ НОВИННОГО КОНТУРУ / ОТРИСОВКА ДЕЙСТВИЙ НОВОСТНОГО КОНТУРА ######
def render_news_actions(
    parent: ctk.CTkFrame,
    database_path: Path,
    unread_news_items: tuple[NewsItem, ...],
    on_success,
) -> None:
    """Відображає ручний refresh і позначення матеріалу як прочитаного.
    Отрисовывает ручной refresh и пометку материала как прочитанного.
    """

    action_frame = ctk.CTkFrame(parent, **CARD)
    action_frame.pack(fill="x", padx=24, pady=(0, 20))

    label_title(action_frame, "Дії із зовнішнім контуром").pack(anchor="w", padx=20, pady=(18, 0))
    label_body(
        action_frame,
        "Інспектор може вручну оновити активні довірені джерела та позначити вибраний матеріал як прочитаний.",
        wraplength=880,
    ).pack(anchor="w", padx=20, pady=(8, 0))

    button_row = ctk.CTkFrame(action_frame, fg_color="transparent")
    button_row.pack(fill="x", padx=20, pady=(14, 20))

    ctk.CTkButton(
        button_row,
        text="Оновити джерела",
        command=build_refresh_news_sources_handler(database_path, on_success),
        **BTN,
    ).pack(side="left")

    news_item_options = build_news_item_options(unread_news_items)
    selected_news_item_var = StringVar(value=news_item_options[0] if news_item_options else "")
    ttk.Combobox(
        button_row,
        values=news_item_options,
        textvariable=selected_news_item_var,
        state="readonly",
    ).pack(side="left", padx=(12, 0), fill="x", expand=True)

    ctk.CTkButton(
        button_row,
        text="Позначити як прочитане",
        command=build_mark_news_item_as_read_handler(database_path, selected_news_item_var, on_success),
        **BTN_SEC,
    ).pack(side="left", padx=(12, 0))
