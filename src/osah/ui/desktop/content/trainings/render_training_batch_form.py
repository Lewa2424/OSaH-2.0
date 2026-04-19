import tkinter as tk
from collections.abc import Callable
from pathlib import Path
from tkinter import StringVar, ttk
import customtkinter as ctk

from osah.ui.desktop.content.trainings.build_training_batch_submit_handler import build_training_batch_submit_handler
from osah.ui.desktop.content.trainings.build_training_type_options import build_training_type_options
from osah.ui.desktop.content.ctk_styles import CARD, BTN, ENTRY, label_title, label_body, label_muted


# ###### ВІДОБРАЖЕННЯ ФОРМИ МАСОВОГО ІНСТРУКТАЖУ / ОТРИСОВКА ФОРМЫ МАССОВОГО ИНСТРУКТАЖА ######
def render_training_batch_form(
    parent: ctk.CTkFrame,
    database_path: Path,
    employee_options: tuple[str, ...],
    on_success: Callable[[], None],
) -> None:
    """Відображає форму масового створення записів інструктажів.
    Отрисовывает форму массового создания записей инструктажей.
    """

    form_frame = ctk.CTkFrame(parent, **CARD)
    form_frame.pack(fill="x", pady=(0, 20))

    label_title(form_frame, "Масовий запис інструктажу").grid(row=0, column=0, columnspan=2, sticky="w", padx=20, pady=(20, 0))
    label_body(
        form_frame,
        "Один сценарій для групи працівників, якщо дата проведення, тип інструктажу і контролю збігаються.",
        wraplength=420,
    ).grid(row=1, column=0, columnspan=2, sticky="w", padx=20, pady=(8, 12))

    training_type_options = build_training_type_options()
    training_type_var = StringVar(value=training_type_options[0] if training_type_options else "")
    event_date_var = StringVar()
    next_control_date_var = StringVar()
    conducted_by_var = StringVar()
    note_var = StringVar()

    label_muted(form_frame, "Працівники").grid(row=2, column=0, sticky="nw", padx=20, pady=(16, 0))
    
    # Listbox не має прямого аналога в CTk, який так само зручно підтримував би множинний вибір
    # з коробки для великого списку, тому використаємо стандартний tk.Listbox зі стилізацією.
    employees_listbox = tk.Listbox(form_frame, selectmode=tk.MULTIPLE, height=6, exportselection=False)
    employees_listbox.configure(
        background="#ffffff",
        foreground="#142129",
        selectbackground="#dae5ea",
        selectforeground="#142129",
        highlightthickness=1,
        highlightbackground="#E5E7EB", # border_color
        relief="flat",
        font=("Segoe UI", 11),
    )
    for employee_option in employee_options:
        employees_listbox.insert(tk.END, employee_option)
    employees_listbox.grid(row=2, column=1, sticky="ew", padx=(10, 20), pady=(16, 0))

    label_muted(form_frame, "Тип інструктажу").grid(row=3, column=0, sticky="w", padx=20, pady=(16, 0))
    ttk.Combobox(
        form_frame,
        values=training_type_options,
        textvariable=training_type_var,
        state="readonly",
    ).grid(row=3, column=1, sticky="ew", padx=(10, 20), pady=(16, 0))

    label_muted(form_frame, "Дата проведення (РРРР-ММ-ДД)").grid(row=4, column=0, sticky="w", padx=20, pady=(16, 0))
    ctk.CTkEntry(form_frame, textvariable=event_date_var, **ENTRY).grid(row=4, column=1, sticky="ew", padx=(10, 20), pady=(16, 0))

    label_muted(form_frame, "Дата контролю (РРРР-ММ-ДД)").grid(row=5, column=0, sticky="w", padx=20, pady=(16, 0))
    ctk.CTkEntry(form_frame, textvariable=next_control_date_var, **ENTRY).grid(row=5, column=1, sticky="ew", padx=(10, 20), pady=(16, 0))

    label_muted(form_frame, "Хто проводив").grid(row=6, column=0, sticky="w", padx=20, pady=(16, 0))
    ctk.CTkEntry(form_frame, textvariable=conducted_by_var, **ENTRY).grid(row=6, column=1, sticky="ew", padx=(10, 20), pady=(16, 0))

    label_muted(form_frame, "Примітка").grid(row=7, column=0, sticky="w", padx=20, pady=(16, 0))
    ctk.CTkEntry(form_frame, textvariable=note_var, **ENTRY).grid(row=7, column=1, sticky="ew", padx=(10, 20), pady=(16, 0))

    form_frame.grid_columnconfigure(1, weight=1)
    ctk.CTkButton(
        form_frame,
        text="Зберегти для вибраних працівників",
        command=build_training_batch_submit_handler(
            database_path=str(database_path),
            employees_listbox=employees_listbox,
            training_type_var=training_type_var,
            event_date_var=event_date_var,
            next_control_date_var=next_control_date_var,
            conducted_by_var=conducted_by_var,
            note_var=note_var,
            on_success=on_success,
        ),
        **BTN,
    ).grid(row=8, column=0, columnspan=2, sticky="w", padx=20, pady=(24, 20))
