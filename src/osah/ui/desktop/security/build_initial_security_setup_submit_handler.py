from collections.abc import Callable
from pathlib import Path
from tkinter import StringVar, messagebox

from osah.application.services.security.configure_program_access import configure_program_access


# ###### ПОБУДОВА ОБРОБНИКА ПЕРВИННОГО НАЛАШТУВАННЯ / ПОСТРОЕНИЕ ОБРАБОТЧИКА ПЕРВИЧНОЙ НАСТРОЙКИ ######
def build_initial_security_setup_submit_handler(
    database_path: Path,
    inspector_password_var: StringVar,
    manager_password_var: StringVar,
    on_configured: Callable[[], None],
) -> Callable[[], None]:
    """Повертає обробник первинного налаштування паролів доступу.
    Возвращает обработчик первичной настройки паролей доступа.
    """

    # ###### ЗАСТОСУВАННЯ ПЕРВИННОГО НАЛАШТУВАННЯ / ПРИМЕНЕНИЕ ПЕРВИЧНОЙ НАСТРОЙКИ ######
    def submit_initial_security_setup() -> None:
        """Зберігає паролі ролей, генерує recovery-файл і повертає до входу.
        Сохраняет пароли ролей, генерирует recovery-файл и возвращает ко входу.
        """

        try:
            reset_result = configure_program_access(
                database_path=database_path,
                inspector_password=inspector_password_var.get(),
                manager_password=manager_password_var.get(),
            )
        except ValueError as error:
            messagebox.showerror("Помилка налаштування", str(error))
            return

        messagebox.showinfo(
            "Доступ налаштовано",
            f"Первинне налаштування завершено.\n\nНовий recovery-код: {reset_result.recovery_code}\n"
            f"Recovery-файл: {reset_result.recovery_file_path}",
        )
        on_configured()

    return submit_initial_security_setup
