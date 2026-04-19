from collections.abc import Callable
from tkinter import BooleanVar, StringVar, messagebox

from osah.application.services.create_ppe_record import create_ppe_record
from osah.ui.desktop.content.ppe.extract_ppe_employee_number import extract_ppe_employee_number


# ###### ПОБУДОВА ОБРОБНИКА ЗБЕРЕЖЕННЯ ЗІЗ / ПОСТРОЕНИЕ ОБРАБОТЧИКА СОХРАНЕНИЯ СИЗ ######
def build_ppe_submit_handler(
    database_path: str,
    selected_employee_var: StringVar,
    ppe_name_var: StringVar,
    is_required_var: BooleanVar,
    is_issued_var: BooleanVar,
    issue_date_var: StringVar,
    replacement_date_var: StringVar,
    quantity_var: StringVar,
    note_var: StringVar,
    on_success: Callable[[], None],
) -> Callable[[], None]:
    """Повертає обробник збереження запису ЗІЗ.
    Возвращает обработчик сохранения записи СИЗ.
    """

    # ###### ЗБЕРЕЖЕННЯ ЗІЗ / СОХРАНЕНИЕ СИЗ ######
    def save_ppe_record() -> None:
        """Створює запис ЗІЗ та оновлює поточний екран.
        Создаёт запись СИЗ и обновляет текущий экран.
        """

        try:
            create_ppe_record(
                database_path=database_path,
                employee_personnel_number=extract_ppe_employee_number(selected_employee_var),
                ppe_name=ppe_name_var.get(),
                is_required=is_required_var.get(),
                is_issued=is_issued_var.get(),
                issue_date_text=issue_date_var.get(),
                replacement_date_text=replacement_date_var.get(),
                quantity_text=quantity_var.get(),
                note_text=note_var.get(),
            )
        except ValueError as error:
            messagebox.showerror("Помилка валідації", str(error))
            return

        messagebox.showinfo("Запис ЗІЗ збережено", "Новий запис по ЗІЗ успішно додано.")
        on_success()

    return save_ppe_record
