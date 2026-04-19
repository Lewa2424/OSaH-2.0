from collections.abc import Callable
from tkinter import StringVar, messagebox

from osah.application.services.delete_training_record import delete_training_record
from osah.ui.desktop.content.trainings.extract_training_record_id import extract_training_record_id


# ###### ПОБУДОВА ОБРОБНИКА ВИДАЛЕННЯ ІНСТРУКТАЖУ / ПОСТРОЕНИЕ ОБРАБОТЧИКА УДАЛЕНИЯ ИНСТРУКТАЖА ######
def build_training_delete_handler(
    database_path: str,
    selected_record_var: StringVar,
    on_success: Callable[[], None],
) -> Callable[[], None]:
    """Повертає обробник видалення існуючого запису інструктажу.
    Возвращает обработчик удаления существующей записи инструктажа.
    """

    # ###### ВИДАЛЕННЯ ІНСТРУКТАЖУ / УДАЛЕНИЕ ИНСТРУКТАЖА ######
    def delete_training() -> None:
        """Видаляє вибраний запис інструктажу після підтвердження.
        Удаляет выбранную запись инструктажа после подтверждения.
        """

        record_id = extract_training_record_id(selected_record_var)
        if record_id is None:
            messagebox.showerror("Помилка валідації", "Потрібно вибрати існуючий запис інструктажу.")
            return

        if not messagebox.askyesno("Підтвердження видалення", "Видалити вибраний запис інструктажу?"):
            return

        try:
            delete_training_record(database_path=database_path, record_id=record_id)
        except ValueError as error:
            messagebox.showerror("Помилка операції", str(error))
            return

        messagebox.showinfo("Інструктаж видалено", "Запис інструктажу успішно видалено.")
        on_success()

    return delete_training
