import customtkinter as ctk

from osah.domain.entities.employee import Employee
from osah.domain.entities.medical_record import MedicalRecord
from osah.domain.entities.ppe_record import PpeRecord
from osah.domain.entities.training_record import TrainingRecord
from osah.domain.entities.work_permit_record import WorkPermitRecord
from osah.domain.services.build_medical_summary import build_medical_summary
from osah.domain.services.build_ppe_summary import build_ppe_summary
from osah.domain.services.build_work_permit_summary import build_work_permit_summary
from osah.ui.desktop.content.build_employee_training_summary import build_employee_training_summary
from osah.ui.desktop.content.format_employment_status_label import format_employment_status_label
from osah.ui.desktop.content.render_employee_summary_block import render_employee_summary_block
from osah.ui.desktop.content.ctk_styles import INSET, label_muted, label_body, pill_label
from osah.ui.desktop.security.apply_desktop_theme import STYLE_TOKENS


# ###### ВІДОБРАЖЕННЯ КАРТКИ ПРАЦІВНИКА / ОТРИСОВКА КАРТОЧКИ СОТРУДНИКА ######
def render_employee_details_card(
    parent,
    employee: Employee,
    training_records: tuple[TrainingRecord, ...],
    ppe_records: tuple[PpeRecord, ...],
    medical_records: tuple[MedicalRecord, ...],
    work_permit_records: tuple[WorkPermitRecord, ...],
) -> None:
    """Відображає картку вибраного працівника в правій панелі.
    Отрисовывает карточку выбранного сотрудника в правой панели.
    """

    for child in parent.winfo_children():
        child.destroy()

    label_muted(parent, "Картка працівника").pack(anchor="w", padx=0, pady=(0, 4))

    ctk.CTkLabel(
        parent,
        text=employee.full_name,
        text_color=STYLE_TOKENS["strong_text"],
        font=("Segoe UI", 20, "bold"),
        anchor="w",
    ).pack(anchor="w", pady=(4, 8))

    pill_label(parent, format_employment_status_label(employee), STYLE_TOKENS["info_background"]).pack(anchor="w", pady=(0, 16))

    # ---- Ідентифікатори ----
    identity_frame = ctk.CTkFrame(parent, **INSET)
    identity_frame.pack(fill="x")
    identity_frame.grid_columnconfigure(1, weight=1)

    fields = (
        ("Табельний номер", employee.personnel_number),
        ("Посада", employee.position_name),
        ("Підрозділ", employee.department_name),
        ("Статус зайнятості", format_employment_status_label(employee)),
    )
    for row_index, (field_name, field_value) in enumerate(fields):
        pad_top = (16, 0) if row_index == 0 else (10, 0)
        label_muted(identity_frame, field_name).grid(row=row_index, column=0, sticky="w", padx=16, pady=pad_top)
        label_body(identity_frame, field_value).grid(row=row_index, column=1, sticky="w", padx=(14, 16), pady=pad_top)

    # Нижній відступ у identity_frame
    ctk.CTkFrame(identity_frame, fg_color="transparent", height=12).grid(row=len(fields), column=0, columnspan=2)

    render_employee_summary_block(parent, "Інструктажі", build_employee_training_summary(training_records))
    render_employee_summary_block(parent, "ЗІЗ", build_ppe_summary(ppe_records))
    render_employee_summary_block(parent, "Медицина", build_medical_summary(medical_records))
    render_employee_summary_block(parent, "Наряди-допуски", build_work_permit_summary(work_permit_records))
