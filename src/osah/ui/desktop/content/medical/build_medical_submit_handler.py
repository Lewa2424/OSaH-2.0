from collections.abc import Callable
from tkinter import StringVar, messagebox

from osah.application.services.create_medical_record import create_medical_record
from osah.ui.desktop.content.medical.extract_medical_decision_value import extract_medical_decision_value
from osah.ui.desktop.content.medical.extract_medical_employee_number import extract_medical_employee_number


# ###### ПОБУДОВА ОБРОБНИКА ЗБЕРЕЖЕННЯ МЕДИЦИНИ / ПОСТРОЕНИЕ ОБРАБОТЧИКА СОХРАНЕНИЯ МЕДИЦИНЫ ######
def build_medical_submit_handler(
    database_path: str,
    selected_employee_var: StringVar,
    valid_from_var: StringVar,
    valid_until_var: StringVar,
    medical_decision_var: StringVar,
    restriction_note_var: StringVar,
    on_success: Callable[[], None],
) -> Callable[[], None]:
    """Повертає обробник збереження медичного запису.
    Возвращает обработчик сохранения медицинской записи.
    """

    # ###### ЗБЕРЕЖЕННЯ МЕДИЦИНИ / СОХРАНЕНИЕ МЕДИЦИНЫ ######
    def save_medical_record() -> None:
        """Створює медичний запис та оновлює поточний екран.
        Создаёт медицинскую запись и обновляет текущий экран.
        """

        try:
            create_medical_record(
                database_path=database_path,
                employee_personnel_number=extract_medical_employee_number(selected_employee_var),
                valid_from_text=valid_from_var.get(),
                valid_until_text=valid_until_var.get(),
                medical_decision=extract_medical_decision_value(medical_decision_var.get()),
                restriction_note=restriction_note_var.get(),
            )
        except ValueError as error:
            messagebox.showerror("Помилка валідації", str(error))
            return

        messagebox.showinfo("Медичний запис збережено", "Новий медичний запис успішно додано.")
        on_success()

    return save_medical_record
