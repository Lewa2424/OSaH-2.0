from collections.abc import Callable
from tkinter import StringVar, messagebox

from osah.application.services.create_work_permit_record import create_work_permit_record
from osah.ui.desktop.content.work_permits.extract_work_permit_employee_number import extract_work_permit_employee_number
from osah.ui.desktop.content.work_permits.extract_work_permit_participant_role_value import (
    extract_work_permit_participant_role_value,
)


# ###### ПОБУДОВА ОБРОБНИКА ЗБЕРЕЖЕННЯ НАРЯДУ / ПОСТРОЕНИЕ ОБРАБОТЧИКА СОХРАНЕНИЯ НАРЯДА ######
def build_work_permit_submit_handler(
    database_path: str,
    permit_number_var: StringVar,
    work_kind_var: StringVar,
    work_location_var: StringVar,
    starts_at_var: StringVar,
    ends_at_var: StringVar,
    responsible_person_var: StringVar,
    issuer_person_var: StringVar,
    selected_employee_var: StringVar,
    participant_role_var: StringVar,
    note_var: StringVar,
    on_success: Callable[[], None],
) -> Callable[[], None]:
    """Повертає обробник збереження нового наряду-допуску.
    Возвращает обработчик сохранения нового наряда-допуска.
    """

    # ###### ЗБЕРЕЖЕННЯ НАРЯДУ / СОХРАНЕНИЕ НАРЯДА ######
    def save_work_permit_record() -> None:
        """Створює наряд-допуск та оновлює поточний екран.
        Создаёт наряд-допуск и обновляет текущий экран.
        """

        try:
            create_work_permit_record(
                database_path=database_path,
                permit_number=permit_number_var.get(),
                work_kind=work_kind_var.get(),
                work_location=work_location_var.get(),
                starts_at_text=starts_at_var.get(),
                ends_at_text=ends_at_var.get(),
                responsible_person=responsible_person_var.get(),
                issuer_person=issuer_person_var.get(),
                employee_personnel_number=extract_work_permit_employee_number(selected_employee_var),
                participant_role=extract_work_permit_participant_role_value(participant_role_var.get()),
                note_text=note_var.get(),
            )
        except ValueError as error:
            messagebox.showerror("Помилка валідації", str(error))
            return

        messagebox.showinfo("Наряд-допуск збережено", "Новий наряд-допуск успішно додано.")
        on_success()

    return save_work_permit_record
