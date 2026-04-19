from collections.abc import Callable
from pathlib import Path
from tkinter import ttk


# ###### ПОБУДОВА ОБРОБНИКА ОНОВЛЕННЯ ЕКРАНА НАЛАШТУВАНЬ / ПОСТРОЕНИЕ ОБРАБОТЧИКА ОБНОВЛЕНИЯ ЭКРАНА НАСТРОЕК ######
def build_settings_screen_refresh_handler(parent: ttk.Frame, database_path: Path) -> Callable[[], None]:
    """Повертає обробник, який оновлює екран налаштувань і сервісних операцій.
    Возвращает обработчик, который обновляет экран настроек и сервисных операций.
    """

    # ###### ОНОВЛЕННЯ ЕКРАНА НАЛАШТУВАНЬ / ОБНОВЛЕНИЕ ЭКРАНА НАСТРОЕК ######
    def refresh_settings_screen() -> None:
        """Перемальовує екран налаштувань після сервісної операції.
        Перерисовывает экран настроек после сервисной операции.
        """

        from osah.ui.desktop.content.settings.render_settings_content import render_settings_content

        for child in parent.winfo_children():
            child.destroy()
        render_settings_content(parent, database_path, refresh_settings_screen)

    return refresh_settings_screen
