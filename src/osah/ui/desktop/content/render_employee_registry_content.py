import customtkinter as ctk
from tkinter import ttk

from osah.domain.entities.employee import Employee
from osah.domain.entities.medical_record import MedicalRecord
from osah.domain.entities.ppe_record import PpeRecord
from osah.domain.entities.training_record import TrainingRecord
from osah.domain.entities.work_permit_record import WorkPermitRecord
from osah.ui.desktop.content.build_employee_selection_handler import build_employee_selection_handler
from osah.ui.desktop.content.format_employment_status_label import format_employment_status_label
from osah.ui.desktop.content.render_employee_details_card import render_employee_details_card
from osah.ui.desktop.content.ctk_styles import CARD, label_muted, label_body, label_content_title
from osah.ui.desktop.security.apply_desktop_theme import STYLE_TOKENS


# ###### ВІДОБРАЖЕННЯ РЕЄСТРУ ПРАЦІВНИКІВ / ОТРИСОВКА РЕЕСТРА СОТРУДНИКОВ ######
def render_employee_registry_content(
    parent,
    employees: tuple[Employee, ...],
    training_records: tuple[TrainingRecord, ...],
    ppe_records: tuple[PpeRecord, ...],
    medical_records: tuple[MedicalRecord, ...],
    work_permit_records: tuple[WorkPermitRecord, ...],
) -> None:
    """Відображає реєстр працівників і картку вибраного запису.
    Отрисовывает реестр сотрудников и карточку выбранной записи.
    """

    label_content_title(parent, "Працівники").pack(anchor="w", padx=24, pady=(24, 8))
    ctk.CTkLabel(
        parent,
        text="Реєстр особового складу з правою карткою швидкого контролю по інструктажах, ЗІЗ, медицині та нарядах-допусках.",
        text_color=STYLE_TOKENS["muted_text"],
        font=("Segoe UI", 11),
        anchor="w",
        wraplength=980,
        justify="left",
    ).pack(anchor="w", padx=24, pady=(0, 16))

    split_frame = ctk.CTkFrame(parent, fg_color="transparent", corner_radius=0)
    split_frame.pack(fill="both", expand=True, padx=24, pady=(0, 24))
    split_frame.grid_columnconfigure(0, weight=3)
    split_frame.grid_columnconfigure(1, weight=2)
    split_frame.grid_rowconfigure(0, weight=1)

    # ---- Реєстр (ttk.Treeview залишається) ----
    registry_frame = ctk.CTkFrame(split_frame, **CARD)
    registry_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 12))

    ctk.CTkLabel(
        registry_frame,
        text="Реєстр працівників",
        text_color=STYLE_TOKENS["strong_text"],
        font=("Segoe UI", 13, "bold"),
        anchor="w",
    ).pack(anchor="w", padx=18, pady=(18, 0))

    label_body(
        registry_frame,
        "Базовий список працівників із табельними номерами, посадами та статусом зайнятості.",
        wraplength=620,
    ).pack(anchor="w", padx=18, pady=(8, 12))

    tree = ttk.Treeview(
        registry_frame,
        columns=("full_name", "personnel_number", "position_name", "department_name", "employment_status"),
        show="headings",
        height=18,
    )
    tree.heading("full_name", text="ПІБ")
    tree.heading("personnel_number", text="Табельний номер")
    tree.heading("position_name", text="Посада")
    tree.heading("department_name", text="Підрозділ")
    tree.heading("employment_status", text="Статус")
    tree.column("full_name", width=260, anchor="w")
    tree.column("personnel_number", width=130, anchor="w")
    tree.column("position_name", width=220, anchor="w")
    tree.column("department_name", width=220, anchor="w")
    tree.column("employment_status", width=110, anchor="w")
    tree.pack(fill="both", expand=True, padx=4, pady=(0, 4))

    # ---- Деталі (CTkFrame) ----
    details_frame = ctk.CTkFrame(split_frame, **CARD)
    details_frame.grid(row=0, column=1, sticky="nsew")

    details_inner = ctk.CTkScrollableFrame(details_frame, fg_color="transparent", corner_radius=0)
    details_inner.pack(fill="both", expand=True, padx=20, pady=20)

    # ---- Групування записів за працівником ----
    training_records_by_employee: dict[str, tuple[TrainingRecord, ...]] = {}
    for training_record in training_records:
        emp_recs = list(training_records_by_employee.get(training_record.employee_personnel_number, ()))
        emp_recs.append(training_record)
        training_records_by_employee[training_record.employee_personnel_number] = tuple(emp_recs)

    ppe_records_by_employee: dict[str, tuple[PpeRecord, ...]] = {}
    for ppe_record in ppe_records:
        emp_recs = list(ppe_records_by_employee.get(ppe_record.employee_personnel_number, ()))
        emp_recs.append(ppe_record)
        ppe_records_by_employee[ppe_record.employee_personnel_number] = tuple(emp_recs)

    medical_records_by_employee: dict[str, tuple[MedicalRecord, ...]] = {}
    for medical_record in medical_records:
        emp_recs = list(medical_records_by_employee.get(medical_record.employee_personnel_number, ()))
        emp_recs.append(medical_record)
        medical_records_by_employee[medical_record.employee_personnel_number] = tuple(emp_recs)

    work_permit_records_by_employee: dict[str, tuple[WorkPermitRecord, ...]] = {}
    for work_permit_record in work_permit_records:
        for participant in work_permit_record.participants:
            emp_recs = list(work_permit_records_by_employee.get(participant.employee_personnel_number, ()))
            emp_recs.append(work_permit_record)
            work_permit_records_by_employee[participant.employee_personnel_number] = tuple(emp_recs)

    employees_by_number = {employee.personnel_number: employee for employee in employees}
    for employee in employees:
        tree.insert(
            "",
            "end",
            iid=employee.personnel_number,
            values=(
                employee.full_name,
                employee.personnel_number,
                employee.position_name,
                employee.department_name,
                format_employment_status_label(employee),
            ),
        )

    if employees:
        tree.selection_set(employees[0].personnel_number)
        render_employee_details_card(
            details_inner,
            employees[0],
            tuple(training_records_by_employee.get(employees[0].personnel_number, ())),
            tuple(ppe_records_by_employee.get(employees[0].personnel_number, ())),
            tuple(medical_records_by_employee.get(employees[0].personnel_number, ())),
            tuple(work_permit_records_by_employee.get(employees[0].personnel_number, ())),
        )

    tree.bind(
        "<<TreeviewSelect>>",
        build_employee_selection_handler(
            tree,
            details_inner,
            employees_by_number,
            training_records_by_employee,
            ppe_records_by_employee,
            medical_records_by_employee,
            work_permit_records_by_employee,
        ),
    )
