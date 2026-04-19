from collections.abc import Callable
from pathlib import Path
from tkinter import StringVar, ttk
import customtkinter as ctk

from osah.domain.entities.work_permit_record import WorkPermitRecord
from osah.ui.desktop.content.work_permits.build_work_permit_close_handler import build_work_permit_close_handler
from osah.ui.desktop.content.work_permits.build_work_permit_close_options import build_work_permit_close_options
from osah.ui.desktop.content.ctk_styles import CARD, BTN, label_title, label_body, label_muted


# ###### ВІДОБРАЖЕННЯ ФОРМИ ЗАКРИТТЯ НАРЯДУ / ОТРИСОВКА ФОРМЫ ЗАКРЫТИЯ НАРЯДА ######
def render_work_permit_close_form(
    parent: ctk.CTkFrame,
    database_path: Path,
    work_permit_records: tuple[WorkPermitRecord, ...],
    on_success: Callable[[], None],
) -> None:
    """Відображає форму ручного закриття активного наряду-допуску.
    Отрисовывает форму ручного закрытия активного наряда-допуска.
    """

    close_options = build_work_permit_close_options(work_permit_records)
    close_frame = ctk.CTkFrame(parent, **CARD)
    close_frame.pack(fill="x", pady=(0, 20))
    
    label_title(close_frame, "Ручне закриття наряду").grid(row=0, column=0, columnspan=2, sticky="w", padx=20, pady=(20, 0))
    label_body(
        close_frame,
        "Закриття виконується окремою дією: завершення за часом не вважається коректним закриттям наряду.",
        wraplength=420,
    ).grid(row=1, column=0, columnspan=2, sticky="w", padx=20, pady=(8, 12))

    label_muted(close_frame, "Обрати наряд").grid(row=2, column=0, sticky="w", padx=20, pady=(16, 0))
    selected_record_var = StringVar(value=close_options[0] if close_options else "")
    
    ttk.Combobox(close_frame, values=close_options, textvariable=selected_record_var, state="readonly").grid(
        row=2,
        column=1,
        sticky="ew",
        padx=(10, 20),
        pady=(16, 0),
    )

    close_frame.grid_columnconfigure(1, weight=1)
    
    ctk.CTkButton(
        close_frame,
        text="Закрити наряд-допуск",
        command=build_work_permit_close_handler(
            database_path=str(database_path),
            selected_record_var=selected_record_var,
            on_success=on_success,
        ),
        **BTN,
    ).grid(row=3, column=0, columnspan=2, sticky="w", padx=20, pady=(24, 20))
