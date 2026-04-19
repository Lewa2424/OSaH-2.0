from collections.abc import Callable
from pathlib import Path
from tkinter import StringVar, ttk
import customtkinter as ctk

from osah.ui.desktop.content.medical.build_medical_decision_options import build_medical_decision_options
from osah.ui.desktop.content.medical.build_medical_submit_handler import build_medical_submit_handler
from osah.ui.desktop.content.ctk_styles import CARD, BTN, ENTRY, label_title, label_body, label_muted


# ###### ВІДОБРАЖЕННЯ ФОРМИ МЕДИЦИНИ / ОТРИСОВКА ФОРМЫ МЕДИЦИНЫ ######
def render_medical_form(
    parent: ctk.CTkFrame,
    database_path: Path,
    employee_options: tuple[str, ...],
    on_success: Callable[[], None],
) -> None:
    """Відображає форму створення нового медичного запису (stacked layout).
    Отрисовывает форму создания новой медицинской записи (stacked layout).
    """

    form_frame = ctk.CTkFrame(parent, **CARD)
    form_frame.pack(fill="x", pady=(0, 20))

    label_title(form_frame, "Новий медичний запис").grid(row=0, column=0, sticky="w", padx=20, pady=(20, 0))
    label_body(
        form_frame,
        "Зберігається тільки мінімально потрібний контур: строки допуску, рішення і робочі обмеження без медичних деталей.",
        wraplength=420,
    ).grid(row=1, column=0, sticky="w", padx=20, pady=(8, 12))

    selected_employee_var = StringVar(value=employee_options[0] if employee_options else "")
    valid_from_var = StringVar()
    valid_until_var = StringVar()
    medical_decision_options = build_medical_decision_options()
    medical_decision_var = StringVar(value=medical_decision_options[0] if medical_decision_options else "")
    restriction_note_var = StringVar()

    field_specs = (
        ("Працівник", selected_employee_var, True),
        ("Дата початку (РРРР-ММ-ДД)", valid_from_var, False),
        ("Дата завершення (РРРР-ММ-ДД)", valid_until_var, False),
        ("Медичне рішення", medical_decision_var, True),
        ("Обмеження / примітка", restriction_note_var, False),
    )

    current_row = 2
    for field_label, var, is_combo in field_specs:
        label_muted(form_frame, field_label).grid(row=current_row, column=0, sticky="w", padx=20, pady=(16, 4))
        current_row += 1

        if is_combo:
            options = employee_options if field_label == "Працівник" else medical_decision_options
            ttk.Combobox(
                form_frame,
                values=options,
                textvariable=var,
                state="readonly"
            ).grid(row=current_row, column=0, sticky="ew", padx=20, pady=(0, 0))
        else:
            ctk.CTkEntry(
                form_frame,
                textvariable=var,
                **ENTRY
            ).grid(row=current_row, column=0, sticky="ew", padx=20, pady=(0, 0))
        current_row += 1

    form_frame.grid_columnconfigure(0, weight=1)

    submit_button = ctk.CTkButton(
        form_frame,
        text="Зберегти медичний запис",
        command=build_medical_submit_handler(
            database_path=str(database_path),
            selected_employee_var=selected_employee_var,
            valid_from_var=valid_from_var,
            valid_until_var=valid_until_var,
            medical_decision_var=medical_decision_var,
            restriction_note_var=restriction_note_var,
            on_success=on_success,
        ),
        **BTN,
    )
    submit_button.grid(row=current_row, column=0, sticky="w", padx=20, pady=(24, 20))
