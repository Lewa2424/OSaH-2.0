import customtkinter as ctk
from tkinter import Misc

from osah.domain.entities.ppe_record import PpeRecord
from osah.ui.desktop.content.ppe.format_ppe_status_label import format_ppe_status_label
from osah.ui.desktop.content.ctk_styles import CARD, label_title, label_body, label_muted, BTN
from osah.ui.desktop.security.apply_desktop_theme import STYLE_TOKENS


# ###### ВІДОБРАЖЕННЯ МОДАЛЬНОГО ВІКНА ДЕТАЛЕЙ / ОТРИСОВКА МОДАЛЬНОГО ОКНА ДЕТАЛЕЙ ######
def render_ppe_details_modal(
    parent: Misc,
    ppe_record: PpeRecord,
) -> None:
    """Відкриває спливаюче вікно з усіма деталями ЗІЗ.
    Открывает всплывающее окно со всеми деталями СИЗ.
    """

    window = ctk.CTkToplevel(parent)
    window.title(f"Деталі ЗІЗ: {ppe_record.ppe_name}")
    window.geometry("500x530")
    window.configure(fg_color=STYLE_TOKENS["root_background"])
    
    window.transient(parent)
    window.grab_set()

    scroll_frame = ctk.CTkScrollableFrame(window, fg_color="transparent")
    scroll_frame.pack(fill="both", expand=True, padx=20, pady=20)

    card_frame = ctk.CTkFrame(scroll_frame, **CARD)
    card_frame.pack(fill="both", expand=True, padx=4, pady=4)

    label_title(card_frame, f"ЗІЗ: {ppe_record.ppe_name}").grid(row=0, column=0, columnspan=2, sticky="w", padx=20, pady=(20, 8))
    
    status_text = format_ppe_status_label(ppe_record.status)
    label_body(card_frame, f"Статус: {status_text}").grid(row=1, column=0, columnspan=2, sticky="w", padx=20, pady=(0, 20))

    required_label = "Так" if ppe_record.is_required else "Ні"
    issued_label = "Так" if ppe_record.is_issued else "Ні (не видано)"

    details = (
        ("Працівник:", ppe_record.employee_full_name),
        ("Табельний номер:", ppe_record.employee_personnel_number),
        ("Дата видачі:", ppe_record.issue_date),
        ("Дата заміни:", ppe_record.replacement_date),
        ("Кількість:", str(ppe_record.quantity)),
        ("Обов'язковий:", required_label),
        ("Фактично виданий:", issued_label),
        ("Примітка:", ppe_record.note_text if ppe_record.note_text else "—"),
    )

    current_row = 2
    for label, val in details:
        label_muted(card_frame, label).grid(row=current_row, column=0, sticky="nw", padx=(20, 10), pady=8)
        val_label = ctk.CTkLabel(card_frame, text=val, text_color=STYLE_TOKENS["strong_text"], font=("Segoe UI", 11), justify="left", wraplength=280)
        val_label.grid(row=current_row, column=1, sticky="w", padx=(0, 20), pady=8)
        current_row += 1

    card_frame.grid_columnconfigure(1, weight=1)

    ctk.CTkButton(
        window,
        text="Закрити",
        command=window.destroy,
        **BTN,
    ).pack(pady=(0, 20))
