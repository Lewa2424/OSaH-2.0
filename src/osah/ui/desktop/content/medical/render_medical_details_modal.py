import customtkinter as ctk
from tkinter import Misc

from osah.domain.entities.medical_record import MedicalRecord
from osah.domain.services.format_medical_decision_label import format_medical_decision_label
from osah.ui.desktop.content.medical.format_medical_status_label import format_medical_status_label
from osah.ui.desktop.content.ctk_styles import CARD, label_title, label_body, label_muted, BTN
from osah.ui.desktop.security.apply_desktop_theme import STYLE_TOKENS


# ###### ВІДОБРАЖЕННЯ МОДАЛЬНОГО ВІКНА ДЕТАЛЕЙ / ОТРИСОВКА МОДАЛЬНОГО ОКНА ДЕТАЛЕЙ ######
def render_medical_details_modal(
    parent: Misc,
    medical_record: MedicalRecord,
) -> None:
    """Відкриває спливаюче вікно з усіма деталями медичного допуску.
    Открывает всплывающее окно со всеми деталями медицинского допуска.
    """

    window = ctk.CTkToplevel(parent)
    window.title(f"Деталі медогляду: {medical_record.employee_full_name}")
    window.geometry("500x480")
    window.configure(fg_color=STYLE_TOKENS["root_background"])
    
    window.transient(parent)
    window.grab_set()

    scroll_frame = ctk.CTkScrollableFrame(window, fg_color="transparent")
    scroll_frame.pack(fill="both", expand=True, padx=20, pady=20)

    card_frame = ctk.CTkFrame(scroll_frame, **CARD)
    card_frame.pack(fill="both", expand=True, padx=4, pady=4)

    label_title(card_frame, f"Медогляд: {medical_record.employee_full_name}").grid(row=0, column=0, columnspan=2, sticky="w", padx=20, pady=(20, 8))
    
    status_text = format_medical_status_label(medical_record.status)
    label_body(card_frame, f"Статус: {status_text}").grid(row=1, column=0, columnspan=2, sticky="w", padx=20, pady=(0, 20))

    details = (
        ("Табельний номер:", medical_record.employee_personnel_number),
        ("Період дії:", f"з {medical_record.valid_from} до {medical_record.valid_until}"),
        ("Медичне рішення:", format_medical_decision_label(medical_record.medical_decision)),
        ("Обмеження (примітка):", medical_record.restriction_note if medical_record.restriction_note else "—"),
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
