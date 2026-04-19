from collections.abc import Callable
from pathlib import Path
from tkinter import BooleanVar, StringVar, ttk
import customtkinter as ctk

from osah.ui.desktop.content.ppe.build_ppe_submit_handler import build_ppe_submit_handler
from osah.ui.desktop.content.ctk_styles import CARD, BTN, ENTRY, CHECKBOX, label_title, label_body, label_muted


# ###### ВІДОБРАЖЕННЯ ФОРМИ ЗІЗ / ОТРИСОВКА ФОРМЫ СИЗ ######
def render_ppe_form(
    parent: ctk.CTkFrame,
    database_path: Path,
    employee_options: tuple[str, ...],
    on_success: Callable[[], None],
) -> None:
    """Відображає форму створення нового запису ЗІЗ (stacked layout).
    Отрисовывает форму создания новой записи СИЗ (stacked layout).
    """

    form_frame = ctk.CTkFrame(parent, **CARD)
    form_frame.pack(fill="x", pady=(0, 20))

    label_title(form_frame, "Новий запис ЗІЗ").grid(row=0, column=0, sticky="w", padx=20, pady=(20, 0))
    label_body(
        form_frame,
        "Фіксація видачі, строку заміни, кількості та базової відповідності нормі для конкретного працівника.",
        wraplength=420,
    ).grid(row=1, column=0, sticky="w", padx=20, pady=(8, 12))

    selected_employee_var = StringVar(value=employee_options[0] if employee_options else "")
    ppe_name_var = StringVar()
    is_required_var = BooleanVar(value=True)
    is_issued_var = BooleanVar(value=True)
    issue_date_var = StringVar()
    replacement_date_var = StringVar()
    quantity_var = StringVar(value="1")
    note_var = StringVar()

    field_specs = (
        ("Працівник", selected_employee_var, True),
        ("Назва ЗІЗ", ppe_name_var, False),
        ("Дата видачі (РРРР-ММ-ДД)", issue_date_var, False),
        ("Дата заміни (РРРР-ММ-ДД)", replacement_date_var, False),
        ("Кількість", quantity_var, False),
        ("Примітка", note_var, False),
    )

    current_row = 2
    for field_label, var, is_combo in field_specs:
        label_muted(form_frame, field_label).grid(row=current_row, column=0, sticky="w", padx=20, pady=(16, 4))
        current_row += 1

        if is_combo:
            ttk.Combobox(
                form_frame,
                values=employee_options,
                textvariable=var,
                state="readonly"
            ).grid(row=current_row, column=0, sticky="ew", padx=20, pady=(0, 0))
            current_row += 1
            
            # Чекбокси вставляємо одразу після Назви (наступним кроком) або після співробітника?
            # Раніше вони були між Назвою і Датою видачі. Тому додамо їх жорстко після Назви ЗІЗ.
        else:
            ctk.CTkEntry(
                form_frame,
                textvariable=var,
                **ENTRY
            ).grid(row=current_row, column=0, sticky="ew", padx=20, pady=(0, 0))
            current_row += 1

        if field_label == "Назва ЗІЗ":
            ctk.CTkCheckBox(form_frame, text="Обов'язковий ЗІЗ", variable=is_required_var, **CHECKBOX).grid(row=current_row, column=0, sticky="w", padx=20, pady=(16, 0))
            current_row += 1
            ctk.CTkCheckBox(form_frame, text="ЗІЗ видано", variable=is_issued_var, **CHECKBOX).grid(row=current_row, column=0, sticky="w", padx=20, pady=(10, 0))
            current_row += 1

    form_frame.grid_columnconfigure(0, weight=1)

    submit_button = ctk.CTkButton(
        form_frame,
        text="Зберегти запис ЗІЗ",
        command=build_ppe_submit_handler(
            database_path=str(database_path),
            selected_employee_var=selected_employee_var,
            ppe_name_var=ppe_name_var,
            is_required_var=is_required_var,
            is_issued_var=is_issued_var,
            issue_date_var=issue_date_var,
            replacement_date_var=replacement_date_var,
            quantity_var=quantity_var,
            note_var=note_var,
            on_success=on_success,
        ),
        **BTN,
    )
    submit_button.grid(row=current_row, column=0, sticky="w", padx=20, pady=(24, 20))
