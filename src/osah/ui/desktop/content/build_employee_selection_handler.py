from collections.abc import Callable
from tkinter import ttk

from osah.domain.entities.employee import Employee
from osah.domain.entities.medical_record import MedicalRecord
from osah.domain.entities.ppe_record import PpeRecord
from osah.domain.entities.training_record import TrainingRecord
from osah.domain.entities.work_permit_record import WorkPermitRecord
from osah.ui.desktop.content.render_employee_details_card import render_employee_details_card


# ###### ПОБУДОВА ОБРОБНИКА ВИБОРУ ПРАЦІВНИКА / ПОСТРОЕНИЕ ОБРАБОТЧИКА ВЫБОРА СОТРУДНИКА ######
def build_employee_selection_handler(
    tree: ttk.Treeview,
    details_frame: ttk.Frame,
    employees_by_number: dict[str, Employee],
    training_records_by_employee: dict[str, tuple[TrainingRecord, ...] | list[TrainingRecord]],
    ppe_records_by_employee: dict[str, tuple[PpeRecord, ...] | list[PpeRecord]],
    medical_records_by_employee: dict[str, tuple[MedicalRecord, ...] | list[MedicalRecord]],
    work_permit_records_by_employee: dict[str, tuple[WorkPermitRecord, ...] | list[WorkPermitRecord]],
) -> Callable[[object], None]:
    """Створює обробник вибору рядка реєстру працівників.
    Создаёт обработчик выбора строки реестра сотрудников.
    """

    # ###### ОБРОБКА ВИБОРУ ПРАЦІВНИКА / ОБРАБОТКА ВЫБОРА СОТРУДНИКА ######
    def handle_employee_selection(_: object) -> None:
        """Перемальовує картку за вибраним записом реєстру.
        Перерисовывает карточку по выбранной записи реестра.
        """

        selected_items = tree.selection()
        if not selected_items:
            return

        selected_employee = employees_by_number[selected_items[0]]
        for child in details_frame.winfo_children():
            child.destroy()
        render_employee_details_card(
            details_frame,
            selected_employee,
            tuple(training_records_by_employee.get(selected_employee.personnel_number, ())),
            tuple(ppe_records_by_employee.get(selected_employee.personnel_number, ())),
            tuple(medical_records_by_employee.get(selected_employee.personnel_number, ())),
            tuple(work_permit_records_by_employee.get(selected_employee.personnel_number, ())),
        )

    return handle_employee_selection
