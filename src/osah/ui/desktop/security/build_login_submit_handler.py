from collections.abc import Callable
from pathlib import Path
from tkinter import StringVar, messagebox

from osah.application.services.security.authenticate_program_access import authenticate_program_access
from osah.domain.entities.access_role import AccessRole


# ###### ПОБУДОВА ОБРОБНИКА ВХОДУ / ПОСТРОЕНИЕ ОБРАБОТЧИКА ВХОДА ######
def build_login_submit_handler(
    database_path: Path,
    access_role_var: StringVar,
    password_var: StringVar,
    on_authenticated: Callable[[AccessRole], None],
) -> Callable[[], None]:
    """Повертає обробник входу до локальної програми.
    Возвращает обработчик входа в локальную программу.
    """

    # ###### ВИКОНАННЯ ВХОДУ ДО ПРОГРАМИ / ВЫПОЛНЕНИЕ ВХОДА В ПРОГРАММУ ######
    def submit_login() -> None:
        """Перевіряє пароль вибраної ролі і запускає shell при успіху.
        Проверяет пароль выбранной роли и запускает shell при успехе.
        """

        access_role = AccessRole(access_role_var.get())
        authentication_result = authenticate_program_access(database_path, access_role, password_var.get())
        if not authentication_result.is_authenticated or authentication_result.access_role is None:
            messagebox.showerror("Помилка входу", authentication_result.message_text)
            return
        on_authenticated(authentication_result.access_role)

    return submit_login
