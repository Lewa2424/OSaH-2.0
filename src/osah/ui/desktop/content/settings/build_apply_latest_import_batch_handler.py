from collections.abc import Callable
from pathlib import Path
from tkinter import messagebox

from osah.application.services.apply_employee_import_batch import apply_employee_import_batch
from osah.application.services.load_latest_employee_import_review import load_latest_employee_import_review


# ###### ПОБУДОВА ОБРОБНИКА ЗАСТОСУВАННЯ ОСТАННЬОЇ ПАРТІЇ ІМПОРТУ / ПОСТРОЕНИЕ ОБРАБОТЧИКА ПРИМЕНЕНИЯ ПОСЛЕДНЕЙ ПАРТИИ ИМПОРТА ######
def build_apply_latest_import_batch_handler(database_path: Path, on_success: Callable[[], None]) -> Callable[[], None]:
    """Повертає обробник застосування останньої партії імпорту працівників.
    Возвращает обработчик применения последней партии импорта сотрудников.
    """

    # ###### ЗАСТОСУВАННЯ ОСТАННЬОЇ ПАРТІЇ ІМПОРТУ / ПРИМЕНЕНИЕ ПОСЛЕДНЕЙ ПАРТИИ ИМПОРТА ######
    def apply_latest_import_batch() -> None:
        """Застосовує останню доступну партію чернеток імпорту працівників.
        Применяет последнюю доступную партию черновиков импорта сотрудников.
        """

        latest_batch_summary, _ = load_latest_employee_import_review(database_path)
        if latest_batch_summary is None:
            messagebox.showerror("Немає партії імпорту", "Спочатку потрібно створити чернетки імпорту.")
            return
        if latest_batch_summary.applied_at:
            messagebox.showerror("Партію вже застосовано", "Останню партію імпорту вже було застосовано.")
            return

        try:
            apply_employee_import_batch(database_path, latest_batch_summary.batch_id)
        except ValueError as error:
            messagebox.showerror("Помилка застосування", str(error))
            return

        messagebox.showinfo("Імпорт застосовано", "Останню партію імпорту працівників успішно застосовано.")
        on_success()

    return apply_latest_import_batch
