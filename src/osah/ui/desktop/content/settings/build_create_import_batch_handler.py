from collections.abc import Callable
from pathlib import Path
from tkinter import filedialog, messagebox

from osah.application.services.create_employee_import_batch_from_file import create_employee_import_batch_from_file


# ###### ПОБУДОВА ОБРОБНИКА СТВОРЕННЯ ЧЕРНЕТОК ІМПОРТУ / ПОСТРОЕНИЕ ОБРАБОТЧИКА СОЗДАНИЯ ЧЕРНОВИКОВ ИМПОРТА ######
def build_create_import_batch_handler(database_path: Path, on_success: Callable[[], None]) -> Callable[[], None]:
    """Повертає обробник вибору файлу й створення чернеток імпорту працівників.
    Возвращает обработчик выбора файла и создания черновиков импорта сотрудников.
    """

    # ###### СТВОРЕННЯ ЧЕРНЕТОК ІМПОРТУ / СОЗДАНИЕ ЧЕРНОВИКОВ ИМПОРТА ######
    def create_import_batch() -> None:
        """Вибирає файл імпорту та формує нову партію чернеток.
        Выбирает файл импорта и формирует новую партию черновиков.
        """

        selected_file_path = filedialog.askopenfilename(
            title="Обрати файл імпорту працівників",
            filetypes=(
                ("Підтримувані файли", "*.json *.xlsx"),
                ("JSON", "*.json"),
                ("Excel XLSX", "*.xlsx"),
            ),
        )
        if not selected_file_path:
            return

        try:
            batch_id = create_employee_import_batch_from_file(database_path, Path(selected_file_path))
        except (ValueError, OSError) as error:
            messagebox.showerror("Помилка імпорту", str(error))
            return

        messagebox.showinfo("Чернетки імпорту створено", f"Партію імпорту #{batch_id} успішно підготовлено.")
        on_success()

    return create_import_batch
