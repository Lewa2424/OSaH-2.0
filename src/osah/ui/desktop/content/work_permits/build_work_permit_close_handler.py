from collections.abc import Callable
from tkinter import StringVar, messagebox

from osah.application.services.close_work_permit_record import close_work_permit_record
from osah.ui.desktop.content.work_permits.extract_work_permit_record_id import extract_work_permit_record_id


# ###### ПОБУДОВА ОБРОБНИКА ЗАКРИТТЯ НАРЯДУ / ПОСТРОЕНИЕ ОБРАБОТЧИКА ЗАКРЫТИЯ НАРЯДА ######
def build_work_permit_close_handler(
    database_path: str,
    selected_record_var: StringVar,
    on_success: Callable[[], None],
) -> Callable[[], None]:
    """Повертає обробник ручного закриття наряду-допуску.
    Возвращает обработчик ручного закрытия наряда-допуска.
    """

    # ###### ЗАКРИТТЯ НАРЯДУ / ЗАКРЫТИЕ НАРЯДА ######
    def close_selected_work_permit_record() -> None:
        """Закриває обраний наряд-допуск та оновлює поточний екран.
        Закрывает выбранный наряд-допуск и обновляет текущий экран.
        """

        record_id = extract_work_permit_record_id(selected_record_var)
        if record_id is None:
            messagebox.showerror("Помилка валідації", "Потрібно вибрати наряд-допуск для закриття.")
            return
        try:
            close_work_permit_record(database_path, record_id)
        except ValueError as error:
            messagebox.showerror("Помилка закриття", str(error))
            return

        messagebox.showinfo("Наряд-допуск закрито", "Обраний наряд-допуск успішно закрито вручну.")
        on_success()

    return close_selected_work_permit_record
