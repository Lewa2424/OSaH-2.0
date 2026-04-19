from collections.abc import Callable
from pathlib import Path
from tkinter import messagebox

from osah.application.services.save_daily_report_document_copy import save_daily_report_document_copy


# ###### ПОБУДОВА ОБРОБНИКА ЗБЕРЕЖЕННЯ КОПІЇ ЗВІТУ / ПОСТРОЕНИЕ ОБРАБОТЧИКА СОХРАНЕНИЯ КОПИИ ОТЧЁТА ######
def build_save_daily_report_copy_handler(database_path: Path, on_success: Callable[[], None]) -> Callable[[], None]:
    """Повертає обробник збереження локальної копії щоденного звіту.
    Возвращает обработчик сохранения локальной копии ежедневного отчёта.
    """

    # ###### ЗБЕРЕЖЕННЯ КОПІЇ ЗВІТУ / СОХРАНЕНИЕ КОПИИ ОТЧЁТА ######
    def save_daily_report_copy_now() -> None:
        """Генерує звіт і зберігає його текстову копію.
        Генерирует отчёт и сохраняет его текстовую копию.
        """

        report_copy_path = save_daily_report_document_copy(database_path)
        messagebox.showinfo("Копію звіту збережено", f"Файл збережено: {report_copy_path}")
        on_success()

    return save_daily_report_copy_now
