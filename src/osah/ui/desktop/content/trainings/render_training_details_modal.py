import customtkinter as ctk
from tkinter import Misc

from osah.domain.entities.training_registry_row import TrainingRegistryRow
from osah.ui.desktop.content.ctk_styles import CARD, label_title, label_body, label_muted, BTN
from osah.ui.desktop.security.apply_desktop_theme import STYLE_TOKENS


# ###### ВІДОБРАЖЕННЯ МОДАЛЬНОГО ВІКНА ДЕТАЛЕЙ / ОТРИСОВКА МОДАЛЬНОГО ОКНА ДЕТАЛЕЙ ######
def render_training_details_modal(
    parent: Misc,
    registry_row: TrainingRegistryRow,
) -> None:
    """Відкриває спливаюче вікно з усіма доступними деталями інструктажу за працівником і типом.
    Открывает всплывающее окно со всеми доступными деталями инструктажа по сотруднику и типу.
    """

    window = ctk.CTkToplevel(parent)
    window.title(f"Деталі: {registry_row.training_type_label}")
    window.geometry("500x480")
    window.configure(fg_color=STYLE_TOKENS["root_background"])
    
    window.transient(parent)
    window.grab_set()

    scroll_frame = ctk.CTkScrollableFrame(window, fg_color="transparent")
    scroll_frame.pack(fill="both", expand=True, padx=20, pady=20)

    card_frame = ctk.CTkFrame(scroll_frame, **CARD)
    card_frame.pack(fill="both", expand=True, padx=4, pady=4)

    label_title(card_frame, f"Інструктаж: {registry_row.training_type_label}").grid(row=0, column=0, columnspan=2, sticky="w", padx=20, pady=(20, 8))
    
    label_body(card_frame, f"Статус: {registry_row.status_label}").grid(row=1, column=0, columnspan=2, sticky="w", padx=20, pady=(0, 20))

    details = (
        ("Працівник:", registry_row.employee_full_name),
        ("Табельний номер:", registry_row.employee_personnel_number),
        ("Дата проведення:", registry_row.event_date_label),
        ("Наступний контроль:", registry_row.next_control_date_label),
        ("Відповідальний за проведення:", registry_row.conducted_by_label),
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
