from collections.abc import Callable
from pathlib import Path
from tkinter import StringVar, ttk
import customtkinter as ctk

from osah.ui.desktop.content.trainings.build_training_submit_handler import build_training_submit_handler
from osah.ui.desktop.content.trainings.build_training_type_options import build_training_type_options
from osah.ui.desktop.content.ctk_styles import CARD, BTN, ENTRY, label_title, label_body, label_muted


# ###### ВІДОБРАЖЕННЯ ФОРМИ ІНСТРУКТАЖУ / ОТРИСОВКА ФОРМЫ ИНСТРУКТАЖА ######
def render_training_form(
    parent: ctk.CTkFrame,
    database_path: Path,
    employee_options: tuple[str, ...],
    on_success: Callable[[], None],
) -> None:
    """Відображає форму створення нового запису інструктажу (stacked layout).
    Отрисовывает форму создания новой записи инструктажа (stacked layout).
    """

    form_frame = ctk.CTkFrame(parent, **CARD)
    form_frame.pack(fill="x", pady=(0, 20))

    label_title(form_frame, "Новий інструктаж").grid(row=0, column=0, sticky="w", padx=20, pady=(20, 0))
    label_body(
        form_frame,
        "Ручне внесення одного запису для конкретного працівника з датою проведення, контролю і відповідальним.",
        wraplength=420,
    ).grid(row=1, column=0, sticky="w", padx=20, pady=(8, 12))

    selected_employee_var = StringVar(value=employee_options[0] if employee_options else "")
    training_type_options = build_training_type_options()
    training_type_var = StringVar(value=training_type_options[0] if training_type_options else "")
    event_date_var = StringVar()
    next_control_date_var = StringVar()
    conducted_by_var = StringVar()
    note_var = StringVar()

    field_specs = (
        ("Працівник", selected_employee_var, True),
        ("Тип інструктажу", training_type_var, True),
        ("Дата проведення (РРРР-ММ-ДД)", event_date_var, False),
        ("Дата контролю (РРРР-ММ-ДД)", next_control_date_var, False),
        ("Хто проводив", conducted_by_var, False),
        ("Примітка", note_var, False),
    )

    current_row = 2
    for field_label, var, is_combo in field_specs:
        label_muted(form_frame, field_label).grid(row=current_row, column=0, sticky="w", padx=20, pady=(16, 4))
        current_row += 1

        if is_combo:
            options = employee_options if field_label == "Працівник" else training_type_options
            box = ttk.Combobox(
                form_frame,
                values=options,
                textvariable=var,
                state="readonly"
            )
            box.grid(row=current_row, column=0, sticky="ew", padx=20, pady=(0, 0))
            if field_label == "Тип інструктажу" and training_type_options:
                box.set(training_type_options[0])
        else:
            ctk.CTkEntry(
                form_frame,
                textvariable=var,
                **ENTRY
            ).grid(row=current_row, column=0, sticky="ew", padx=20, pady=(0, 0))
        current_row += 1

    form_frame.grid_columnconfigure(0, weight=1)

    submit_handler = build_training_submit_handler(
        database_path=str(database_path),
        selected_employee_var=selected_employee_var,
        training_type_var=training_type_var,
        event_date_var=event_date_var,
        next_control_date_var=next_control_date_var,
        conducted_by_var=conducted_by_var,
        note_var=note_var,
        on_success=on_success,
    )
    ctk.CTkButton(
        form_frame,
        text="Зберегти інструктаж",
        command=submit_handler,
        **BTN
    ).grid(row=current_row, column=0, sticky="w", padx=20, pady=(24, 20))
