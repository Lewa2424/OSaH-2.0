from tkinter import ttk
import customtkinter as ctk

from osah.domain.entities.backup_snapshot import BackupSnapshot
from osah.ui.desktop.content.settings.format_backup_kind_label import format_backup_kind_label
from osah.ui.desktop.content.ctk_styles import CARD, label_title, label_body


# ###### ВІДОБРАЖЕННЯ ТАБЛИЦІ РЕЗЕРВНИХ КОПІЙ / ОТРИСОВКА ТАБЛИЦЫ РЕЗЕРВНЫХ КОПИЙ ######
def render_backup_registry_table(parent: ctk.CTkFrame, backup_snapshots: tuple[BackupSnapshot, ...]) -> None:
    """Відображає таблицю доступних резервних копій локальної системи.
    Отрисовывает таблицу доступных резервных копий локальной системы.
    """

    table_frame = ctk.CTkFrame(parent, **CARD)
    table_frame.pack(fill="both", expand=True, pady=(0, 24))

    label_title(table_frame, "Список резервних копій").pack(anchor="w", padx=20, pady=(18, 0))
    label_body(
        table_frame,
        "Повний перелік ручних, автоматичних і страховочних копій локальної установки.",
        wraplength=640,
    ).pack(anchor="w", padx=20, pady=(8, 12))

    tree = ttk.Treeview(
        table_frame,
        columns=("file_name", "backup_kind", "created_at_text", "size_bytes"),
        show="headings",
        height=12,
    )
    tree.heading("file_name", text="Файл")
    tree.heading("backup_kind", text="Тип")
    tree.heading("created_at_text", text="Створено")
    tree.heading("size_bytes", text="Розмір, байт")
    tree.column("file_name", width=280, anchor="w")
    tree.column("backup_kind", width=110, anchor="w")
    tree.column("created_at_text", width=170, anchor="w")
    tree.column("size_bytes", width=120, anchor="w")
    tree.pack(fill="both", expand=True, padx=4, pady=(0, 4))

    for backup_snapshot in backup_snapshots:
        tree.insert(
            "",
            "end",
            iid=backup_snapshot.file_name,
            values=(
                backup_snapshot.file_name,
                format_backup_kind_label(backup_snapshot.backup_kind),
                backup_snapshot.created_at_text,
                backup_snapshot.size_bytes,
            ),
        )
