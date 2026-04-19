from collections.abc import Callable
from pathlib import Path
from tkinter import StringVar, messagebox

from osah.application.services.security.reset_program_access_with_recovery_code import (
    reset_program_access_with_recovery_code,
)


# ###### ПОБУДОВА ОБРОБНИКА RECOVERY-СКИДАННЯ / ПОСТРОЕНИЕ ОБРАБОТЧИКА RECOVERY-СБРОСА ######
def build_recovery_reset_submit_handler(
    database_path: Path,
    recovery_code_var: StringVar,
    inspector_password_var: StringVar,
    manager_password_var: StringVar,
    on_reset: Callable[[], None],
) -> Callable[[], None]:
    """Повертає обробник скидання паролів через recovery-код.
    Возвращает обработчик сброса паролей через recovery-код.
    """

    # ###### СКИДАННЯ ПАРОЛІВ ЧЕРЕЗ RECOVERY-КОД / СБРОС ПАРОЛЕЙ ЧЕРЕЗ RECOVERY-КОД ######
    def submit_recovery_reset() -> None:
        """Перевіряє recovery-код, перевипускає паролі і повертає до входу.
        Проверяет recovery-код, перевыпускает пароли и возвращает ко входу.
        """

        try:
            reset_result = reset_program_access_with_recovery_code(
                database_path=database_path,
                recovery_code=recovery_code_var.get(),
                new_inspector_password=inspector_password_var.get(),
                new_manager_password=manager_password_var.get(),
            )
        except ValueError as error:
            messagebox.showerror("Помилка відновлення", str(error))
            return

        messagebox.showinfo(
            "Доступ відновлено",
            f"Паролі оновлено через recovery-код.\n\nНовий recovery-код: {reset_result.recovery_code}\n"
            f"Recovery-файл: {reset_result.recovery_file_path}",
        )
        on_reset()

    return submit_recovery_reset
