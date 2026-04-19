import customtkinter as ctk
from tkinter import ttk

from osah.domain.entities.ppe_record import PpeRecord
from osah.ui.desktop.content.ppe.format_ppe_status_label import format_ppe_status_label
from osah.ui.desktop.content.ppe.render_ppe_details_modal import render_ppe_details_modal
from osah.ui.desktop.content.ctk_styles import CARD, label_title, label_body


# ###### ВІДОБРАЖЕННЯ РЕЄСТРУ ЗІЗ / ОТРИСОВКА РЕЕСТРА СИЗ ######
def render_ppe_registry_table(parent: ctk.CTkFrame, ppe_records: tuple[PpeRecord, ...]) -> None:
    """Відображає таблицю реєстру ЗІЗ (Master-Detail).
    Отрисовывает таблицу реестра СИЗ (Master-Detail).
    """

    table_frame = ctk.CTkFrame(parent, **CARD)
    table_frame.pack(fill="both", expand=True, pady=(0, 24))

    label_title(table_frame, "Реєстр ЗІЗ").pack(anchor="w", padx=20, pady=(18, 0))
    label_body(
        table_frame,
        "Клікніть по запису ЗІЗ, щоб переглянути його розгорнуті деталі та примітки.",
        wraplength=640,
    ).pack(anchor="w", padx=20, pady=(8, 12))

    tree = ttk.Treeview(
        table_frame,
        columns=(
            "employee_full_name",
            "ppe_name",
            "issue_date",
            "replacement_date",
            "quantity",
            "status",
        ),
        show="headings",
        height=18,
    )
    tree.heading("employee_full_name", text="Працівник")
    tree.heading("ppe_name", text="ЗІЗ")
    tree.heading("issue_date", text="Дата видачі")
    tree.heading("replacement_date", text="Дата заміни")
    tree.heading("quantity", text="Кількість")
    tree.heading("status", text="Статус")
    tree.column("employee_full_name", width=260, anchor="w")
    tree.column("ppe_name", width=220, anchor="w")
    tree.column("issue_date", width=120, anchor="w")
    tree.column("replacement_date", width=120, anchor="w")
    tree.column("quantity", width=90, anchor="w")
    tree.column("status", width=120, anchor="w")
    tree.pack(fill="both", expand=True, padx=4, pady=(0, 4))

    records_by_id: dict[str, PpeRecord] = {}

    for ppe_record in ppe_records:
        record_id_str = str(ppe_record.record_id)
        records_by_id[record_id_str] = ppe_record
        tree.insert(
            "",
            "end",
            iid=record_id_str,
            values=(
                ppe_record.employee_full_name,
                ppe_record.ppe_name,
                ppe_record.issue_date,
                ppe_record.replacement_date,
                str(ppe_record.quantity),
                format_ppe_status_label(ppe_record.status),
            ),
        )

    def _on_row_click(event) -> None:
        """Відкриває детальну інформацію про ЗІЗ у спливаючому вікні при кліку."""
        item_id = tree.identify_row(event.y)
        if not item_id:
            return
            
        tree.selection_set(item_id)
        tree.focus(item_id)
        
        record = records_by_id.get(item_id)
        if record:
            render_ppe_details_modal(parent.winfo_toplevel(), record)

    tree.bind("<ButtonRelease-1>", _on_row_click)
