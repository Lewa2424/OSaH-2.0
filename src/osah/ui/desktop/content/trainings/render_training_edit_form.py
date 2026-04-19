from collections.abc import Callable
from pathlib import Path
from tkinter import StringVar, ttk
import customtkinter as ctk

from osah.domain.entities.training_record import TrainingRecord
from osah.ui.desktop.content.trainings.build_training_employee_options import build_training_employee_options
from osah.ui.desktop.content.trainings.build_training_record_lookup import build_training_record_lookup
from osah.ui.desktop.content.trainings.build_training_record_options import build_training_record_options
from osah.ui.desktop.content.trainings.build_training_record_select_handler import build_training_record_select_handler
from osah.ui.desktop.content.trainings.build_training_type_options import build_training_type_options
from osah.ui.desktop.content.trainings.build_training_update_submit_handler import build_training_update_submit_handler
from osah.ui.desktop.content.trainings.build_training_delete_handler import build_training_delete_handler
from osah.ui.desktop.content.ctk_styles import CARD, BTN, BTN_SEC, ENTRY, label_title, label_body, label_muted


# ###### ВІДОБРАЖЕННЯ ФОРМИ РЕДАГУВАННЯ ІНСТРУКТАЖУ / ОТРИСОВКА ФОРМЫ РЕДАКТИРОВАНИЯ ИНСТРУКТАЖА ######
def render_training_edit_form(
    parent: ctk.CTkFrame,
    database_path: Path,
    employee_options: tuple[str, ...],
    training_records: tuple[TrainingRecord, ...],
    on_success: Callable[[], None],
) -> None:
    """Відображає форму редагування та видалення існуючого запису інструктажу.
    Отрисовывает форму редактирования и удаления существующей записи инструктажа.
    """

    form_frame = ctk.CTkFrame(parent, **CARD)
    form_frame.pack(fill="x", pady=(0, 20))

    label_title(form_frame, "Керування записом інструктажу").grid(row=0, column=0, columnspan=2, sticky="w", padx=20, pady=(20, 0))
    label_body(
        form_frame,
        "Оновлення або видалення існуючого запису з повним контролем полів, що впливають на статус.",
        wraplength=420,
    ).grid(row=1, column=0, columnspan=2, sticky="w", padx=20, pady=(8, 12))

    if not training_records:
        label_body(
            form_frame,
            "Ще немає жодного запису інструктажу для редагування або видалення.",
            wraplength=860,
        ).grid(row=2, column=0, columnspan=2, sticky="w", padx=20, pady=(12, 20))
        return

    training_record_options = build_training_record_options(training_records)
    training_record_lookup = build_training_record_lookup(training_records)
    employee_option_lookup = {
        employee_option.split(" | ", maxsplit=1)[0].strip(): employee_option
        for employee_option in employee_options
        if " | " in employee_option
    }

    selected_record_var = StringVar(value=training_record_options[0] if training_record_options else "")
    selected_employee_var = StringVar(value=employee_options[0] if employee_options else "")
    training_type_options = build_training_type_options()
    training_type_var = StringVar(value=training_type_options[0] if training_type_options else "")
    event_date_var = StringVar()
    next_control_date_var = StringVar()
    conducted_by_var = StringVar()
    note_var = StringVar()

    field_specs = (
        ("Запис", 1),
        ("Працівник", 2),
        ("Тип інструктажу", 3),
        ("Дата проведення (РРРР-ММ-ДД)", 4),
        ("Дата контролю (РРРР-ММ-ДД)", 5),
        ("Хто проводив", 6),
        ("Примітка", 7),
    )
    for field_label, row_index in field_specs:
        label_muted(form_frame, field_label).grid(row=row_index + 1, column=0, sticky="w", padx=20, pady=(16, 0))

    record_box = ttk.Combobox(form_frame, values=training_record_options, textvariable=selected_record_var, state="readonly")
    record_box.grid(row=2, column=1, sticky="ew", padx=(10, 20), pady=(16, 0))
    ttk.Combobox(form_frame, values=employee_options, textvariable=selected_employee_var, state="readonly").grid(
        row=3,
        column=1,
        sticky="ew",
        padx=(10, 20),
        pady=(16, 0),
    )
    ttk.Combobox(form_frame, values=training_type_options, textvariable=training_type_var, state="readonly").grid(
        row=4,
        column=1,
        sticky="ew",
        padx=(10, 20),
        pady=(16, 0),
    )
    ctk.CTkEntry(form_frame, textvariable=event_date_var, **ENTRY).grid(row=5, column=1, sticky="ew", padx=(10, 20), pady=(16, 0))
    ctk.CTkEntry(form_frame, textvariable=next_control_date_var, **ENTRY).grid(row=6, column=1, sticky="ew", padx=(10, 20), pady=(16, 0))
    ctk.CTkEntry(form_frame, textvariable=conducted_by_var, **ENTRY).grid(row=7, column=1, sticky="ew", padx=(10, 20), pady=(16, 0))
    ctk.CTkEntry(form_frame, textvariable=note_var, **ENTRY).grid(row=8, column=1, sticky="ew", padx=(10, 20), pady=(16, 0))

    form_frame.grid_columnconfigure(1, weight=1)
    record_box.bind(
        "<<ComboboxSelected>>",
        build_training_record_select_handler(
            selected_record_var,
            training_record_lookup,
            employee_option_lookup,
            selected_employee_var,
            training_type_var,
            event_date_var,
            next_control_date_var,
            conducted_by_var,
            note_var,
        ),
    )

    actions_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
    actions_frame.grid(row=9, column=0, columnspan=2, sticky="w", padx=20, pady=(24, 20))

    ctk.CTkButton(
        actions_frame,
        text="Оновити запис",
        command=build_training_update_submit_handler(
            database_path=str(database_path),
            selected_record_var=selected_record_var,
            selected_employee_var=selected_employee_var,
            training_type_var=training_type_var,
            event_date_var=event_date_var,
            next_control_date_var=next_control_date_var,
            conducted_by_var=conducted_by_var,
            note_var=note_var,
            on_success=on_success,
        ),
        **BTN,
    ).pack(side="left")

    ctk.CTkButton(
        actions_frame,
        text="Видалити запис",
        command=build_training_delete_handler(
            database_path=str(database_path),
            selected_record_var=selected_record_var,
            on_success=on_success,
        ),
        **BTN_SEC,
    ).pack(side="left", padx=(12, 0))

    build_training_record_select_handler(
        selected_record_var,
        training_record_lookup,
        employee_option_lookup,
        selected_employee_var,
        training_type_var,
        event_date_var,
        next_control_date_var,
        conducted_by_var,
        note_var,
    )(None)
