from collections.abc import Callable
from tkinter import StringVar, messagebox

from osah.application.services.create_training_record import create_training_record
from osah.ui.desktop.content.trainings.extract_personnel_number import extract_personnel_number
from osah.ui.desktop.content.trainings.extract_training_type_value import extract_training_type_value


# ###### ПОБУДОВА ОБРОБНИКА ЗБЕРЕЖЕННЯ ІНСТРУКТАЖУ / ПОСТРОЕНИЕ ОБРАБОТЧИКА СОХРАНЕНИЯ ИНСТРУКТАЖА ######
def build_training_submit_handler(
    database_path: str,
    selected_employee_var: StringVar,
    training_type_var: StringVar,
    event_date_var: StringVar,
    next_control_date_var: StringVar,
    conducted_by_var: StringVar,
    note_var: StringVar,
    on_success: Callable[[], None],
) -> Callable[[], None]:
    """Повертає обробник збереження запису інструктажу.
    Возвращает обработчик сохранения записи инструктажа.
    """

    # ###### ЗБЕРЕЖЕННЯ ІНСТРУКТАЖУ / СОХРАНЕНИЕ ИНСТРУКТАЖА ######
    def save_training() -> None:
        """Створює запис інструктажу та оновлює поточний екран.
        Создаёт запись инструктажа и обновляет текущий экран.
        """

        try:
            create_training_record(
                database_path=database_path,
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

        messagebox.showinfo("Інструктаж збережено", "Новий запис інструктажу успішно додано.")
        on_success()

    return save_training
