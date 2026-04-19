import customtkinter as ctk
from tkinter import Misc

from osah.domain.entities.work_permit_record import WorkPermitRecord
from osah.domain.services.build_work_permit_participants_summary import build_work_permit_participants_summary
from osah.ui.desktop.content.work_permits.format_work_permit_status_label import format_work_permit_status_label
from osah.ui.desktop.content.ctk_styles import CARD, label_title, label_body, label_muted, BTN
from osah.ui.desktop.security.apply_desktop_theme import STYLE_TOKENS


# ###### ВІДОБРАЖЕННЯ МОДАЛЬНОГО ВІКНА ДЕТАЛЕЙ / ОТРИСОВКА МОДАЛЬНОГО ОКНА ДЕТАЛЕЙ ######
def render_work_permit_details_modal(
    parent: Misc,
    work_permit_record: WorkPermitRecord,
) -> None:
    """Відкриває спливаюче вікно з усіма деталями наряду-допуску (включаючи повні списки).
    Открывает всплывающее окно со всеми деталями наряда-допуска (включая полные списки).
    """

    window = ctk.CTkToplevel(parent)
    window.title(f"Деталі наряду-допуску № {work_permit_record.permit_number}")
    window.geometry("550x650")
    window.configure(fg_color=STYLE_TOKENS["root_background"])
    
    # Робимо вікно модальним
    window.transient(parent)
    window.grab_set()

    scroll_frame = ctk.CTkScrollableFrame(window, fg_color="transparent")
    scroll_frame.pack(fill="both", expand=True, padx=20, pady=20)

    card_frame = ctk.CTkFrame(scroll_frame, **CARD)
    card_frame.pack(fill="both", expand=True, padx=4, pady=4)

    # Заголовок картки
    label_title(card_frame, f"Наряд-допуск {work_permit_record.permit_number}").grid(row=0, column=0, columnspan=2, sticky="w", padx=20, pady=(20, 8))
    
    # Статус
    status_text = format_work_permit_status_label(work_permit_record.status)
    label_body(card_frame, f"Статус: {status_text}").grid(row=1, column=0, columnspan=2, sticky="w", padx=20, pady=(0, 20))

    details = (
        ("Вид робіт:", work_permit_record.work_kind),
        ("Місце:", work_permit_record.work_location),
        ("Період виконання:", f"{work_permit_record.starts_at} — {work_permit_record.ends_at}"),
        ("Відповідальний керівник:", work_permit_record.responsible_person),
        ("Особа, що видала наряд:", work_permit_record.issuer_person),
        ("Примітка:", work_permit_record.note_text if work_permit_record.note_text else "—"),
    )

    current_row = 2
    for label, val in details:
        label_muted(card_frame, label).grid(row=current_row, column=0, sticky="nw", padx=(20, 10), pady=8)
        # Використовуємо wraplength щоб текст переносився якщо він довгий
        val_label = ctk.CTkLabel(card_frame, text=val, text_color=STYLE_TOKENS["strong_text"], font=("Segoe UI", 11), justify="left", wraplength=280)
        val_label.grid(row=current_row, column=1, sticky="w", padx=(0, 20), pady=8)
        current_row += 1

    # Учасники
    label_muted(card_frame, "Учасники (бригада):").grid(row=current_row, column=0, columnspan=2, sticky="w", padx=20, pady=(24, 8))
    current_row += 1

    participants_text = build_work_permit_participants_summary(work_permit_record)
    if not participants_text:
        participants_text = "—"
    
    participants_label = ctk.CTkLabel(
        card_frame, 
        text=participants_text, 
        text_color=STYLE_TOKENS["strong_text"], 
        font=("Segoe UI", 11), 
        justify="left", 
        wraplength=450  # Достатньо місця для багаторядкового перенесення
    )
    participants_label.grid(row=current_row, column=0, columnspan=2, sticky="w", padx=20, pady=(0, 24))
    current_row += 1

    card_frame.grid_columnconfigure(1, weight=1)

    # Кнопка закриття
    ctk.CTkButton(
        window,
        text="Закрити",
        command=window.destroy,
        **BTN,
    ).pack(pady=(0, 20))
