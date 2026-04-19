import customtkinter as ctk
from tkinter import ttk

from osah.domain.entities.medical_record import MedicalRecord
from osah.domain.services.format_medical_decision_label import format_medical_decision_label
from osah.ui.desktop.content.medical.format_medical_status_label import format_medical_status_label
from osah.ui.desktop.content.medical.render_medical_details_modal import render_medical_details_modal
from osah.ui.desktop.content.ctk_styles import CARD, label_title, label_body


# ###### ВІДОБРАЖЕННЯ РЕЄСТРУ МЕДИЦИНИ / ОТРИСОВКА РЕЕСТРА МЕДИЦИНЫ ######
def render_medical_registry_table(parent: ctk.CTkFrame, medical_records: tuple[MedicalRecord, ...]) -> None:
    """Відображає таблицю реєстру медичних записів (Master-Detail).
    Отрисовывает таблицу реестра медицинских записей (Master-Detail).
    """

    table_frame = ctk.CTkFrame(parent, **CARD)
    table_frame.pack(fill="both", expand=True, pady=(0, 24))

    label_title(table_frame, "Реєстр медицини").pack(anchor="w", padx=20, pady=(18, 0))
    label_body(
        table_frame,
        "Реєстр строків допуску та медичних рішень. Клікніть по запису, щоб побачити робочі обмеження.",
        wraplength=640,
    ).pack(anchor="w", padx=20, pady=(8, 12))

    tree = ttk.Treeview(
        table_frame,
        columns=(
            "employee_full_name",
            "valid_from",
            "valid_until",
            "medical_decision",
            "status",
        ),
        show="headings",
        height=18,
    )
    tree.heading("employee_full_name", text="Працівник")
    tree.heading("valid_from", text="З")
    tree.heading("valid_until", text="До")
    tree.heading("medical_decision", text="Рішення")
    tree.heading("status", text="Статус")
    tree.column("employee_full_name", width=260, anchor="w")
    tree.column("valid_from", width=140, anchor="w")
    tree.column("valid_until", width=140, anchor="w")
    tree.column("medical_decision", width=220, anchor="w")
    tree.column("status", width=160, anchor="w")
    tree.pack(fill="both", expand=True, padx=4, pady=(0, 4))

    records_by_id: dict[str, MedicalRecord] = {}

    for medical_record in medical_records:
        record_id_str = str(medical_record.record_id)
        records_by_id[record_id_str] = medical_record
        tree.insert(
            "",
            "end",
            iid=record_id_str,
            values=(
                medical_record.employee_full_name,
                medical_record.valid_from,
                medical_record.valid_until,
                format_medical_decision_label(medical_record.medical_decision),
                format_medical_status_label(medical_record.status),
            ),
        )

    def _on_row_click(event) -> None:
        """Відкриває детальну інформацію про медогляд у спливаючому вікні при кліку."""
        item_id = tree.identify_row(event.y)
        if not item_id:
            return
            
        tree.selection_set(item_id)
        tree.focus(item_id)
        
        record = records_by_id.get(item_id)
        if record:
            render_medical_details_modal(parent.winfo_toplevel(), record)

    tree.bind("<ButtonRelease-1>", _on_row_click)
