from collections.abc import Callable
from pathlib import Path
from tkinter import StringVar, messagebox

from osah.application.services.security.reset_program_access_with_service_code import (
    reset_program_access_with_service_code,
)


# ###### ПОБУДОВА ОБРОБНИКА СЕРВІСНОГО СКИДАННЯ / ПОСТРОЕНИЕ ОБРАБОТЧИКА СЕРВИСНОГО СБРОСА ######
def build_service_reset_submit_handler(
    database_path: Path,
    service_code_var: StringVar,
    inspector_password_var: StringVar,
    manager_password_var: StringVar,
    on_reset: Callable[[], None],
) -> Callable[[], None]:
    """Повертає обробник скидання паролів через сервісний код.
    Возвращает обработчик сброса паролей через сервисный код.
    """

    # ###### СКИДАННЯ ПАРОЛІВ ЧЕРЕЗ СЕРВІСНИЙ КОД / СБРОС ПАРОЛЕЙ ЧЕРЕЗ СЕРВИСНЫЙ КОД ######
    def submit_service_reset() -> None:
        """Перевіряє сервісний код, оновлює доступ і повертає до входу.
        Проверяет сервисный код, обновляет доступ и возвращает ко входу.
        """

        try:
            reset_result = reset_program_access_with_service_code(
                database_path=database_path,
                service_code=service_code_var.get(),
                new_inspector_password=inspector_password_var.get(),
                new_manager_password=manager_password_var.get(),
            )
        except ValueError as error:
            messagebox.showerror("Помилка сервісного скидання", str(error))
            return

        messagebox.showinfo(
            "Доступ відновлено",
            f"Паролі оновлено через сервісний код.\n\nНовий recovery-код: {reset_result.recovery_code}\n"
            f"Recovery-файл: {reset_result.recovery_file_path}",
        )
        on_reset()

    return submit_service_reset
