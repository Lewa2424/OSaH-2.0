from tkinter import ttk
import customtkinter as ctk

from osah.domain.entities.work_permit_record import WorkPermitRecord
from osah.ui.desktop.content.work_permits.format_work_permit_status_label import format_work_permit_status_label
from osah.ui.desktop.content.work_permits.render_work_permit_details_modal import render_work_permit_details_modal
from osah.ui.desktop.content.ctk_styles import CARD, label_title, label_body


# ###### ВІДОБРАЖЕННЯ РЕЄСТРУ НАРЯДІВ / ОТРИСОВКА РЕЕСТРА НАРЯДОВ ######
def render_work_permit_registry_table(parent: ctk.CTkFrame, work_permit_records: tuple[WorkPermitRecord, ...]) -> None:
    """Відображає таблицю реєстру нарядів-допусків без колонки Учасників (Master-Detail).
    Отрисовывает таблицу реестра нарядов-допусков без колонки Участников (Master-Detail).
    """

    table_frame = ctk.CTkFrame(parent, **CARD)
    table_frame.pack(fill="both", expand=True, pady=(0, 24))

    label_title(table_frame, "Реєстр нарядів-допусків").pack(anchor="w", padx=20, pady=(18, 0))
    label_body(
        table_frame,
        "Клікніть по наряду, щоб відкрити його повні деталі (список бригади, ролі, дати).",
        wraplength=640,
    ).pack(anchor="w", padx=20, pady=(8, 12))

    tree = ttk.Treeview(
        table_frame,
        columns=(
            "permit_number",
            "work_kind",
            "work_location",
            "starts_at",
            "ends_at",
            "status",
        ),
        show="headings",
        height=18,
    )
    tree.heading("permit_number", text="Номер")
    tree.heading("work_kind", text="Вид робіт")
    tree.heading("work_location", text="Місце")
    tree.heading("starts_at", text="Початок")
    tree.heading("ends_at", text="Завершення")
    tree.heading("status", text="Статус")
    
    # Даємо багато місця видам робіт і розширюємо інші тепер, коли немає Учасників
    tree.column("permit_number", width=120, anchor="w")
    tree.column("work_kind", width=300, anchor="w")
    tree.column("work_location", width=250, anchor="w")
    tree.column("starts_at", width=160, anchor="w")
    tree.column("ends_at", width=160, anchor="w")
    tree.column("status", width=120, anchor="w")
    
    tree.pack(fill="both", expand=True, padx=4, pady=(0, 4))

    records_by_id: dict[str, WorkPermitRecord] = {}

    for work_permit_record in work_permit_records:
        record_id_str = str(work_permit_record.record_id)
        records_by_id[record_id_str] = work_permit_record
        tree.insert(
            "",
            "end",
            iid=record_id_str,
            values=(
                work_permit_record.permit_number,
                work_permit_record.work_kind,
                work_permit_record.work_location,
                work_permit_record.starts_at,
                work_permit_record.ends_at,
                format_work_permit_status_label(work_permit_record.status),
            ),
        )

    def _on_row_click(event) -> None:
        """Відкриває детальну інформацію про наряд у спливаючому вікні при кліку."""
        item_id = tree.identify_row(event.y)
        if not item_id:
            return
            
        tree.selection_set(item_id)
        tree.focus(item_id)
        
        record = records_by_id.get(item_id)
        if record:
            render_work_permit_details_modal(parent.winfo_toplevel(), record)

    tree.bind("<ButtonRelease-1>", _on_row_click)
