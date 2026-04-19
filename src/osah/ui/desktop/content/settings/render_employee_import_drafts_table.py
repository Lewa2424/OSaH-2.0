from tkinter import ttk
import customtkinter as ctk

from osah.domain.entities.employee_import_draft import EmployeeImportDraft
from osah.ui.desktop.content.settings.format_employee_import_draft_status_label import (
    format_employee_import_draft_status_label,
)
from osah.ui.desktop.content.ctk_styles import CARD, label_title, label_body


# ###### ВІДОБРАЖЕННЯ ТАБЛИЦІ ЧЕРНЕТОК ІМПОРТУ / ОТРИСОВКА ТАБЛИЦЫ ЧЕРНОВИКОВ ИМПОРТА ######
def render_employee_import_drafts_table(parent: ctk.CTkFrame, employee_import_drafts: tuple[EmployeeImportDraft, ...]) -> None:
    """Відображає таблицю чернеток імпорту працівників для перевірки.
    Отрисовывает таблицу черновиков импорта сотрудников для проверки.
    """

    table_frame = ctk.CTkFrame(parent, **CARD)
    table_frame.pack(fill="both", expand=True, pady=(0, 24))

    label_title(table_frame, "Чернетки імпорту працівників").pack(anchor="w", padx=20, pady=(18, 0))
    label_body(
        table_frame,
        "Проміжний контур перевірки імпортованих рядків перед застосуванням до бойових записів.",
        wraplength=640,
    ).pack(anchor="w", padx=20, pady=(8, 12))

    tree = ttk.Treeview(
        table_frame,
        columns=(
            "source_row_number",
            "personnel_number",
            "full_name",
            "position_name",
            "department_name",
            "employment_status",
            "resolution_status",
            "issue_text",
        ),
        show="headings",
        height=18,
    )
    tree.heading("source_row_number", text="Рядок")
    tree.heading("personnel_number", text="Табельний номер")
    tree.heading("full_name", text="ПІБ")
    tree.heading("position_name", text="Посада")
    tree.heading("department_name", text="Підрозділ")
    tree.heading("employment_status", text="Статус")
    tree.heading("resolution_status", text="Результат")
    tree.heading("issue_text", text="Коментар")
    tree.column("source_row_number", width=70, anchor="w")
    tree.column("personnel_number", width=130, anchor="w")
    tree.column("full_name", width=220, anchor="w")
    tree.column("position_name", width=180, anchor="w")
    tree.column("department_name", width=180, anchor="w")
    tree.column("employment_status", width=100, anchor="w")
    tree.column("resolution_status", width=110, anchor="w")
    tree.column("issue_text", width=260, anchor="w")
    tree.pack(fill="both", expand=True, padx=4, pady=(0, 4))

    for employee_import_draft in employee_import_drafts:
        tree.insert(
            "",
            "end",
            iid=str(employee_import_draft.draft_id),
            values=(
                employee_import_draft.source_row_number,
                employee_import_draft.personnel_number,
                employee_import_draft.full_name,
                employee_import_draft.position_name,
                employee_import_draft.department_name,
                employee_import_draft.employment_status,
                format_employee_import_draft_status_label(employee_import_draft.resolution_status),
                employee_import_draft.issue_text,
            ),
        )
