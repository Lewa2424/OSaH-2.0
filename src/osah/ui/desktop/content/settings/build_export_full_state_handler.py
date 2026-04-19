from collections.abc import Callable
from pathlib import Path
from tkinter import messagebox

from osah.application.services.export_full_system_state import export_full_system_state


# ###### ПОБУДОВА ОБРОБНИКА ПОВНОГО ЕКСПОРТУ / ПОСТРОЕНИЕ ОБРАБОТЧИКА ПОЛНОГО ЭКСПОРТА ######
def build_export_full_state_handler(database_path: Path, on_success: Callable[[], None]) -> Callable[[], None]:
    """Повертає обробник повного експорту стану системи у JSON.
    Возвращает обработчик полного экспорта состояния системы в JSON.
    """

    # ###### ПОВНИЙ ЕКСПОРТ СИСТЕМИ / ПОЛНЫЙ ЭКСПОРТ СИСТЕМЫ ######
    def export_full_state() -> None:
        """Створює повний JSON-експорт локальної системи.
        Создаёт полный JSON-экспорт локальной системы.
        """

        try:
            export_file_path = export_full_system_state(database_path)
        except OSError as error:
            messagebox.showerror("Помилка експорту", str(error))
            return

        messagebox.showinfo("Експорт завершено", f"Файл експорту збережено: {export_file_path}")
        on_success()

    return export_full_state
