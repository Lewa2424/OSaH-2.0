from collections.abc import Callable
from tkinter import StringVar, messagebox

from osah.application.services.update_training_record import update_training_record
from osah.ui.desktop.content.trainings.extract_personnel_number import extract_personnel_number
from osah.ui.desktop.content.trainings.extract_training_record_id import extract_training_record_id
from osah.ui.desktop.content.trainings.extract_training_type_value import extract_training_type_value


# ###### ПОБУДОВА ОБРОБНИКА ОНОВЛЕННЯ ІНСТРУКТАЖУ / ПОСТРОЕНИЕ ОБРАБОТЧИКА ОБНОВЛЕНИЯ ИНСТРУКТАЖА ######
def build_training_update_submit_handler(
    database_path: str,
    selected_record_var: StringVar,
    selected_employee_var: StringVar,
    training_type_var: StringVar,
    event_date_var: StringVar,
    next_control_date_var: StringVar,
    conducted_by_var: StringVar,
    note_var: StringVar,
    on_success: Callable[[], None],
) -> Callable[[], None]:
    """Повертає обробник оновлення існуючого запису інструктажу.
    Возвращает обработчик обновления существующей записи инструктажа.
    """

    # ###### ОНОВЛЕННЯ ІНСТРУКТАЖУ / ОБНОВЛЕНИЕ ИНСТРУКТАЖА ######
    def update_training() -> None:
        """Оновлює вибраний запис інструктажу.
        Обновляет выбранную запись инструктажа.
        """

        record_id = extract_training_record_id(selected_record_var)
        if record_id is None:
            messagebox.showerror("Помилка валідації", "Потрібно вибрати існуючий запис інструктажу.")
            return

        try:
            update_training_record(
                database_path=database_path,
                record_id=record_id,
                employee_personnel_number=extract_personnel_number(selected_employee_var),
                training_type=extract_training_type_value(training_type_var.get()),
                event_date_text=event_date_var.get(),
                next_control_date_text=next_control_date_var.get(),
                conducted_by=conducted_by_var.get(),
                note_text=note_var.get(),
            )
        except ValueError as error:
            messagebox.showerror("Помилка валідації", str(error))
            return

        messagebox.showinfo("Інструктаж оновлено", "Запис інструктажу успішно оновлено.")
        on_success()

    return update_training
