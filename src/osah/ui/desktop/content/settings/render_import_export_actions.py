from pathlib import Path
import customtkinter as ctk

from osah.ui.desktop.content.settings.build_apply_latest_import_batch_handler import (
    build_apply_latest_import_batch_handler,
)
from osah.ui.desktop.content.settings.build_create_import_batch_handler import build_create_import_batch_handler
from osah.ui.desktop.content.settings.build_export_full_state_handler import build_export_full_state_handler
from osah.ui.desktop.content.ctk_styles import CARD, BTN, BTN_SEC, label_title, label_body


# ###### ВІДОБРАЖЕННЯ ДІЙ ІМПОРТУ ТА ЕКСПОРТУ / ОТРИСОВКА ДЕЙСТВИЙ ИМПОРТА И ЭКСПОРТА ######
def render_import_export_actions(parent: ctk.CTkFrame, database_path: Path, on_refresh) -> None:
    """Відображає кнопки сервісних операцій імпорту та експорту.
    Отрисовывает кнопки сервисных операций импорта и экспорта.
    """

    action_frame = ctk.CTkFrame(parent, **CARD)
    action_frame.pack(fill="x", pady=(0, 20))

    label_title(action_frame, "Імпорт / експорт").pack(anchor="w", padx=20, pady=(20, 0))
    label_body(
        action_frame,
        "Імпорт працівників створює чернетки для перевірки. Експорт формує повний JSON-зліпок локальної системи.",
        wraplength=420,
    ).pack(anchor="w", padx=20, pady=(8, 0))

    button_row = ctk.CTkFrame(action_frame, fg_color="transparent")
    button_row.pack(fill="x", padx=20, pady=(14, 20))

    ctk.CTkButton(
        button_row,
        text="Створити чернетки імпорту",
        command=build_create_import_batch_handler(database_path, on_refresh),
        **BTN,
    ).pack(fill="x")

    ctk.CTkButton(
        button_row,
        text="Застосувати останню партію",
        command=build_apply_latest_import_batch_handler(database_path, on_refresh),
        **BTN_SEC,
    ).pack(fill="x", pady=(10, 0))

    ctk.CTkButton(
        button_row,
        text="Повний експорт JSON",
        command=build_export_full_state_handler(database_path, on_refresh),
        **BTN_SEC,
    ).pack(fill="x", pady=(10, 0))
