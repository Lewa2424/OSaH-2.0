from collections.abc import Callable
from pathlib import Path
from tkinter import ttk


# ###### ПОБУДОВА ОБРОБНИКА ОНОВЛЕННЯ ЕКРАНА ЗВІТІВ / ПОСТРОЕНИЕ ОБРАБОТЧИКА ОБНОВЛЕНИЯ ЭКРАНА ОТЧЁТОВ ######
def build_reports_screen_refresh_handler(parent: ttk.Frame, database_path: Path) -> Callable[[], None]:
    """Повертає обробник, який оновлює екран звітів та пошти.
    Возвращает обработчик, который обновляет экран отчётов и почты.
    """

    # ###### ОНОВЛЕННЯ ЕКРАНА ЗВІТІВ / ОБНОВЛЕНИЕ ЭКРАНА ОТЧЁТОВ ######
    def refresh_reports_screen() -> None:
        """Перемальовує екран звітів після зміни налаштувань або відправки.
        Перерисовывает экран отчётов после изменения настроек или отправки.
        """

        from osah.ui.desktop.content.reports.render_reports_content import render_reports_content

        for child in parent.winfo_children():
            child.destroy()
        render_reports_content(parent, database_path, refresh_reports_screen)

    return refresh_reports_screen
