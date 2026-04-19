from pathlib import Path
import customtkinter as ctk

from osah.ui.desktop.content.reports.build_save_daily_report_copy_handler import build_save_daily_report_copy_handler
from osah.ui.desktop.content.reports.build_send_daily_report_handler import build_send_daily_report_handler
from osah.ui.desktop.content.ctk_styles import CARD, BTN, BTN_SEC, label_title, label_body


# ###### ВІДОБРАЖЕННЯ ДІЙ ЩОДЕННОГО ЗВІТУ / ОТРИСОВКА ДЕЙСТВИЙ ЕЖЕДНЕВНОГО ОТЧЁТА ######
def render_report_actions(parent: ctk.CTkFrame, database_path: Path, on_success) -> None:
    """Відображає кнопки збереження копії та ручного надсилання щоденного звіту.
    Отрисовывает кнопки сохранения копии и ручной отправки ежедневного отчёта.
    """

    action_frame = ctk.CTkFrame(parent, **CARD)
    action_frame.pack(fill="x", padx=24, pady=(0, 20))

    label_title(action_frame, "Дії зі звітом").pack(anchor="w", padx=20, pady=(18, 0))
    label_body(
        action_frame,
        "Можна зберегти локальну копію звіту або одразу відправити його поштою з трьома спробами.",
        wraplength=880,
    ).pack(anchor="w", padx=20, pady=(8, 0))

    button_row = ctk.CTkFrame(action_frame, fg_color="transparent")
    button_row.pack(fill="x", padx=20, pady=(14, 20))

    ctk.CTkButton(
        button_row,
        text="Зберегти копію звіту",
        command=build_save_daily_report_copy_handler(database_path, on_success),
        **BTN,
    ).pack(side="left")

    ctk.CTkButton(
        button_row,
        text="Надіслати зараз",
        command=build_send_daily_report_handler(database_path, on_success),
        **BTN_SEC,
    ).pack(side="left", padx=(12, 0))
