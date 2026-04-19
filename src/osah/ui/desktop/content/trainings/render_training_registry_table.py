import customtkinter as ctk
from tkinter import ttk

from osah.domain.entities.training_registry_row import TrainingRegistryRow
from osah.ui.desktop.content.trainings.render_training_details_modal import render_training_details_modal
from osah.ui.desktop.content.ctk_styles import CARD, label_title, label_body


# ###### ВІДОБРАЖЕННЯ РЕЄСТРУ ІНСТРУКТАЖІВ / ОТРИСОВКА РЕЕСТРА ИНСТРУКТАЖЕЙ ######
def render_training_registry_table(parent: ctk.CTkFrame, registry_rows: tuple[TrainingRegistryRow, ...]) -> None:
    """Відображає таблицю реєстру інструктажів (Master-Detail).
    Отрисовывает таблицу реестра инструктажей (Master-Detail).
    """

    table_frame = ctk.CTkFrame(parent, **CARD)
    table_frame.pack(fill="both", expand=True, pady=(0, 24))

    label_title(table_frame, "Реєстр інструктажів").pack(anchor="w", padx=20, pady=(18, 0))
    label_body(
        table_frame,
        "Робочий список записів і відсутніх інструктажів. Клікніть по рядку для перегляду повних деталей інструктажу.",
        wraplength=640,
    ).pack(anchor="w", padx=20, pady=(8, 12))

    tree = ttk.Treeview(
        table_frame,
        columns=(
            "employee_full_name",
            "training_type",
            "event_date",
            "next_control_date",
            "status",
        ),
        show="headings",
        height=18,
    )
    tree.heading("employee_full_name", text="Працівник")
    tree.heading("training_type", text="Тип")
    tree.heading("event_date", text="Дата проведення")
    tree.heading("next_control_date", text="Дата контролю")
    tree.heading("status", text="Статус")
    
    # Даємо багато місця полям "Працівник" та "Тип"
    tree.column("employee_full_name", width=280, anchor="w")
    tree.column("training_type", width=180, anchor="w")
    tree.column("event_date", width=140, anchor="w")
    tree.column("next_control_date", width=140, anchor="w")
    tree.column("status", width=160, anchor="w")
    
    tree.pack(fill="both", expand=True, padx=4, pady=(0, 4))

    records_by_idx: dict[str, TrainingRegistryRow] = {}

    for row_index, registry_row in enumerate(registry_rows):
        idx_str = str(row_index)
        records_by_idx[idx_str] = registry_row
        tree.insert(
            "",
            "end",
            iid=idx_str,
            values=(
                registry_row.employee_full_name,
                registry_row.training_type_label,
                registry_row.event_date_label,
                registry_row.next_control_date_label,
                registry_row.status_label,
            ),
        )

    def _on_row_click(event) -> None:
        """Відкриває детальну інформацію про інструктаж у спливаючому вікні при кліку."""
        item_id = tree.identify_row(event.y)
        if not item_id:
            return
            
        tree.selection_set(item_id)
        tree.focus(item_id)
        
        record = records_by_idx.get(item_id)
        if record:
            render_training_details_modal(parent.winfo_toplevel(), record)

    tree.bind("<ButtonRelease-1>", _on_row_click)
