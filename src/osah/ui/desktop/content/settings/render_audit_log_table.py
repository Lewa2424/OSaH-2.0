from tkinter import ttk
import customtkinter as ctk

from osah.domain.entities.audit_log_entry import AuditLogEntry
from osah.ui.desktop.content.ctk_styles import CARD, label_title, label_body


# ###### ВІДОБРАЖЕННЯ ТАБЛИЦІ AUDIT-ЖУРНАЛУ / ОТРИСОВКА ТАБЛИЦЫ AUDIT-ЖУРНАЛА ######
def render_audit_log_table(parent: ctk.CTkFrame, audit_log_entries: tuple[AuditLogEntry, ...]) -> None:
    """Відображає таблицю останніх audit-подій локальної системи.
    Отрисовывает таблицу последних audit-событий локальной системы.
    """

    table_frame = ctk.CTkFrame(parent, **CARD)
    table_frame.pack(fill="both", expand=True, pady=(0, 20))

    label_title(table_frame, "Audit-журнал").pack(anchor="w", padx=20, pady=(18, 0))
    label_body(
        table_frame,
        "Критичні та бізнес-значущі події локальної системи: безпека, імпорт, відновлення, зміни записів.",
        wraplength=640,
    ).pack(anchor="w", padx=20, pady=(8, 12))

    tree = ttk.Treeview(
        table_frame,
        columns=("created", "event", "module", "actor", "result"),
        show="headings",
        height=8,
    )
    tree.heading("created", text="Час")
    tree.heading("event", text="Подія")
    tree.heading("module", text="Модуль")
    tree.heading("actor", text="Хто")
    tree.heading("result", text="Результат")
    tree.column("created", width=150, anchor="w")
    tree.column("event", width=220, anchor="w")
    tree.column("module", width=140, anchor="w")
    tree.column("actor", width=120, anchor="w")
    tree.column("result", width=100, anchor="w")
    tree.pack(fill="both", expand=True, padx=4, pady=(0, 4))

    for audit_log_entry in audit_log_entries:
        tree.insert(
            "",
            "end",
            values=(
                audit_log_entry.created_at_text,
                audit_log_entry.event_type,
                audit_log_entry.module_name,
                audit_log_entry.actor_name,
                audit_log_entry.result_status,
            ),
        )
