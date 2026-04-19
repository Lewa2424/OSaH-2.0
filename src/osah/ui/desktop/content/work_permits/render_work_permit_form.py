from collections.abc import Callable
from pathlib import Path
from tkinter import StringVar, ttk
import customtkinter as ctk

from osah.ui.desktop.content.work_permits.build_work_permit_participant_role_options import (
    build_work_permit_participant_role_options,
)
from osah.ui.desktop.content.work_permits.build_work_permit_submit_handler import build_work_permit_submit_handler
from osah.ui.desktop.content.ctk_styles import CARD, BTN, ENTRY, label_title, label_body, label_muted


# ###### ВІДОБРАЖЕННЯ ФОРМИ НАРЯДУ / ОТРИСОВКА ФОРМЫ НАРЯДА ######
def render_work_permit_form(
    parent: ctk.CTkFrame,
    database_path: Path,
    employee_options: tuple[str, ...],
    on_success: Callable[[], None],
) -> None:
    """Відображає форму створення нового наряду-допуску у вертикальному компонуванні полів (stacked).
    Отрисовывает форму создания нового наряда-допуска в вертикальной компоновке полей (stacked).
    """

    form_frame = ctk.CTkFrame(parent, **CARD)
    form_frame.pack(fill="x", pady=(0, 20))

    label_title(form_frame, "Новий наряд-допуск").grid(row=0, column=0, sticky="w", padx=20, pady=(20, 0))
    label_body(
        form_frame,
        "Створення активного наряду з учасником, роллю, строком виконання і службовими відповідальними.",
        wraplength=420,
    ).grid(row=1, column=0, sticky="w", padx=20, pady=(8, 12))

    participant_role_options = build_work_permit_participant_role_options()
    permit_number_var = StringVar()
    work_kind_var = StringVar()
    work_location_var = StringVar()
    starts_at_var = StringVar()
    ends_at_var = StringVar()
    responsible_person_var = StringVar()
    issuer_person_var = StringVar()
    selected_employee_var = StringVar(value=employee_options[0] if employee_options else "")
    participant_role_var = StringVar(value=participant_role_options[0] if participant_role_options else "")
    note_var = StringVar()

    field_specs = (
        ("Номер наряду", permit_number_var, False),
        ("Вид робіт", work_kind_var, False),
        ("Місце робіт", work_location_var, False),
        ("Початок (РРРР-ММ-ДД ГГ:ХХ)", starts_at_var, False),
        ("Завершення (РРРР-ММ-ДД ГГ:ХХ)", ends_at_var, False),
        ("Відповідальний", responsible_person_var, False),
        ("Допускаючий", issuer_person_var, False),
        ("Учасник", selected_employee_var, True),
        ("Роль учасника", participant_role_var, True),
        ("Примітка", note_var, False),
    )

    current_row = 2
    for label_text, var, is_combo in field_specs:
        label_muted(form_frame, label_text).grid(row=current_row, column=0, sticky="w", padx=20, pady=(16, 4))
        current_row += 1

        if is_combo:
            options = employee_options if label_text == "Учасник" else participant_role_options
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

    ctk.CTkButton(
        form_frame,
        text="Зберегти наряд-допуск",
        command=build_work_permit_submit_handler(
            database_path=str(database_path),
            permit_number_var=permit_number_var,
            work_kind_var=work_kind_var,
            work_location_var=work_location_var,
            starts_at_var=starts_at_var,
            ends_at_var=ends_at_var,
            responsible_person_var=responsible_person_var,
            issuer_person_var=issuer_person_var,
            selected_employee_var=selected_employee_var,
            participant_role_var=participant_role_var,
            note_var=note_var,
            on_success=on_success,
        ),
        **BTN,
    ).grid(row=current_row, column=0, sticky="w", padx=20, pady=(24, 20))
