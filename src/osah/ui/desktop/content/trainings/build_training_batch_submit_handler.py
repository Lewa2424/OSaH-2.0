from collections.abc import Callable
import tkinter as tk
from tkinter import StringVar, messagebox

from osah.application.services.create_training_records_batch import create_training_records_batch
from osah.ui.desktop.content.trainings.extract_selected_personnel_numbers import extract_selected_personnel_numbers
from osah.ui.desktop.content.trainings.extract_training_type_value import extract_training_type_value


# ###### ПОБУДОВА ОБРОБНИКА МАСОВОГО ЗБЕРЕЖЕННЯ ІНСТРУКТАЖУ / ПОСТРОЕНИЕ ОБРАБОТЧИКА МАССОВОГО СОХРАНЕНИЯ ИНСТРУКТАЖА ######
def build_training_batch_submit_handler(
    database_path: str,
    employees_listbox: tk.Listbox,
    training_type_var: StringVar,
    event_date_var: StringVar,
    next_control_date_var: StringVar,
    conducted_by_var: StringVar,
    note_var: StringVar,
    on_success: Callable[[], None],
) -> Callable[[], None]:
    """Повертає обробник масового створення записів інструктажу.
    Возвращает обработчик массового создания записей инструктажа.
    """

    # ###### МАСОВЕ ЗБЕРЕЖЕННЯ ІНСТРУКТАЖУ / МАССОВОЕ СОХРАНЕНИЕ ИНСТРУКТАЖА ######
    def save_training_batch() -> None:
        """Створює записи інструктажу для кількох працівників.
        Создаёт записи инструктажа для нескольких сотрудников.
        """

        try:
            create_training_records_batch(
                database_path=database_path,
                employee_personnel_numbers=extract_selected_personnel_numbers(employees_listbox),
                training_type=extract_training_type_value(training_type_var.get()),
                event_date_text=event_date_var.get(),
                next_control_date_text=next_control_date_var.get(),
                conducted_by=conducted_by_var.get(),
                note_text=note_var.get(),
            )
        except ValueError as error:
            messagebox.showerror("Помилка валідації", str(error))
            return

        messagebox.showinfo("Масовий запис завершено", "Записи інструктажу для вибраних працівників успішно створено.")
        on_success()

    return save_training_batch
