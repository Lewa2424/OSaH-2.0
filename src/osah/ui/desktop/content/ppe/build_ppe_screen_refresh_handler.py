from collections.abc import Callable
from pathlib import Path
from tkinter import ttk


# ###### ПОБУДОВА ОБРОБНИКА ОНОВЛЕННЯ ЕКРАНА ЗІЗ / ПОСТРОЕНИЕ ОБРАБОТЧИКА ОБНОВЛЕНИЯ ЭКРАНА СИЗ ######
def build_ppe_screen_refresh_handler(parent: ttk.Frame, database_path: Path) -> Callable[[], None]:
    """Повертає обробник, який оновлює екран ЗІЗ.
    Возвращает обработчик, который обновляет экран СИЗ.
    """

    # ###### ОНОВЛЕННЯ ЕКРАНА ЗІЗ / ОБНОВЛЕНИЕ ЭКРАНА СИЗ ######
    def refresh_ppe_screen() -> None:
        """Перемальовує екран ЗІЗ після змін у реєстрі.
        Перерисовывает экран СИЗ после изменений в реестре.
        """

        from osah.ui.desktop.content.ppe.render_ppe_content import render_ppe_content

        for child in parent.winfo_children():
            child.destroy()
        render_ppe_content(parent, database_path, refresh_ppe_screen)

    return refresh_ppe_screen
