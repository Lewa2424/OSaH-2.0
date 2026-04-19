from collections.abc import Callable
from pathlib import Path
from tkinter import ttk


# ###### ПОБУДОВА ОБРОБНИКА ОНОВЛЕННЯ ЕКРАНА МЕДИЦИНИ / ПОСТРОЕНИЕ ОБРАБОТЧИКА ОБНОВЛЕНИЯ ЭКРАНА МЕДИЦИНЫ ######
def build_medical_screen_refresh_handler(parent: ttk.Frame, database_path: Path) -> Callable[[], None]:
    """Повертає обробник, який оновлює екран медицини.
    Возвращает обработчик, который обновляет экран медицины.
    """

    # ###### ОНОВЛЕННЯ ЕКРАНА МЕДИЦИНИ / ОБНОВЛЕНИЕ ЭКРАНА МЕДИЦИНЫ ######
    def refresh_medical_screen() -> None:
        """Перемальовує екран медицини після змін у реєстрі.
        Перерисовывает экран медицины после изменений в реестре.
        """

        from osah.ui.desktop.content.medical.render_medical_content import render_medical_content

        for child in parent.winfo_children():
            child.destroy()
        render_medical_content(parent, database_path, refresh_medical_screen)

    return refresh_medical_screen
