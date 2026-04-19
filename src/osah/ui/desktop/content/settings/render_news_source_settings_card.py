from tkinter import StringVar, ttk
import customtkinter as ctk

from osah.domain.entities.news_source_kind import NewsSourceKind
from osah.ui.desktop.content.settings.build_create_news_source_handler import build_create_news_source_handler
from osah.ui.desktop.content.ctk_styles import CARD, BTN, ENTRY, label_title, label_body, label_muted


# ###### ВІДОБРАЖЕННЯ КАРТКИ НАЛАШТУВАННЯ ДЖЕРЕЛ НОВИН / ОТРИСОВКА КАРТОЧКИ НАСТРОЙКИ ИСТОЧНИКОВ НОВОСТЕЙ ######
def render_news_source_settings_card(parent: ctk.CTkFrame, database_path, on_success) -> None:
    """Відображає форму додавання або оновлення довіреного джерела.
    Отрисовывает форму добавления или обновления доверенного источника.
    """

    source_name_var = StringVar()
    source_url_var = StringVar()
    source_kind_var = StringVar(value=NewsSourceKind.NEWS.value)

    card_frame = ctk.CTkFrame(parent, **CARD)
    card_frame.pack(fill="x", pady=(0, 20))

    label_title(card_frame, "Джерела новин / НПА").grid(row=0, column=0, columnspan=2, sticky="w", padx=20, pady=(20, 0))
    label_body(
        card_frame,
        "Тільки довірені RSS/Atom-джерела зовнішнього контуру. Цей блок не змінює внутрішні кадрові дані.",
        wraplength=420,
    ).grid(row=1, column=0, columnspan=2, sticky="w", padx=20, pady=(8, 12))

    label_muted(card_frame, "Назва джерела").grid(row=2, column=0, sticky="w", padx=20, pady=(16, 0))
    ctk.CTkEntry(card_frame, textvariable=source_name_var, **ENTRY).grid(row=2, column=1, sticky="ew", padx=(10, 20), pady=(16, 0))
    
    label_muted(card_frame, "URL feed").grid(row=3, column=0, sticky="w", padx=20, pady=(16, 0))
    ctk.CTkEntry(card_frame, textvariable=source_url_var, **ENTRY).grid(row=3, column=1, sticky="ew", padx=(10, 20), pady=(16, 0))
    
    label_muted(card_frame, "Тип джерела").grid(row=4, column=0, sticky="w", padx=20, pady=(16, 0))
    ttk.Combobox(
        card_frame,
        values=(NewsSourceKind.NEWS.value, NewsSourceKind.NPA.value),
        textvariable=source_kind_var,
        state="readonly",
    ).grid(row=4, column=1, sticky="ew", padx=(10, 20), pady=(16, 0))
    
    card_frame.grid_columnconfigure(1, weight=1)
    
    ctk.CTkButton(
        card_frame,
        text="Зберегти джерело",
        command=build_create_news_source_handler(
            database_path=database_path,
            source_name_var=source_name_var,
            source_url_var=source_url_var,
            source_kind_var=source_kind_var,
            on_success=on_success,
        ),
        **BTN,
    ).grid(row=5, column=0, columnspan=2, sticky="w", padx=20, pady=(24, 20))
