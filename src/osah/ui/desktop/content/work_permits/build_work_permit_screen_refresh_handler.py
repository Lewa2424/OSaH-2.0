from collections.abc import Callable
from pathlib import Path
from tkinter import ttk


# ###### ПОБУДОВА ОБРОБНИКА ОНОВЛЕННЯ ЕКРАНА НАРЯДІВ / ПОСТРОЕНИЕ ОБРАБОТЧИКА ОБНОВЛЕНИЯ ЭКРАНА НАРЯДОВ ######
def build_work_permit_screen_refresh_handler(parent: ttk.Frame, database_path: Path) -> Callable[[], None]:
    """Повертає обробник, який оновлює екран нарядів-допусків.
    Возвращает обработчик, который обновляет экран нарядов-допусков.
    """

    # ###### ОНОВЛЕННЯ ЕКРАНА НАРЯДІВ / ОБНОВЛЕНИЕ ЭКРАНА НАРЯДОВ ######
    def refresh_work_permit_screen() -> None:
        """Перемальовує екран нарядів-допусків після змін у реєстрі.
        Перерисовывает экран нарядов-допусков после изменений в реестре.
        """

        from osah.ui.desktop.content.work_permits.render_work_permit_content import render_work_permit_content

        for child in parent.winfo_children():
            child.destroy()
        render_work_permit_content(parent, database_path, refresh_work_permit_screen)

    return refresh_work_permit_screen
