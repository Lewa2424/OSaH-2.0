from collections.abc import Callable
from pathlib import Path
from tkinter import ttk

from osah.domain.entities.access_role import AccessRole
from osah.domain.entities.training_registry_filter import TrainingRegistryFilter


# ###### ПОБУДОВА ОБРОБНИКА ОНОВЛЕННЯ ЕКРАНА ІНСТРУКТАЖІВ / ПОСТРОЕНИЕ ОБРАБОТЧИКА ОБНОВЛЕНИЯ ЭКРАНА ИНСТРУКТАЖЕЙ ######
def build_trainings_screen_refresh_handler(
    parent: ttk.Frame,
    database_path: Path,
    selected_filter: TrainingRegistryFilter,
    access_role: AccessRole,
) -> Callable[[], None]:
    """Повертає обробник, який оновлює екран інструктажів із поточним фільтром.
    Возвращает обработчик, который обновляет экран инструктажей с текущим фильтром.
    """

    # ###### ОНОВЛЕННЯ ЕКРАНА ІНСТРУКТАЖІВ / ОБНОВЛЕНИЕ ЭКРАНА ИНСТРУКТАЖЕЙ ######
    def refresh_trainings_screen() -> None:
        """Перемальовує екран інструктажів зі збереженням фільтра і ролі доступу.
        Перерисовывает экран инструктажей с сохранением фильтра и роли доступа.
        """

        from osah.ui.desktop.content.trainings.render_trainings_content import render_trainings_content

        for child in parent.winfo_children():
            child.destroy()
        render_trainings_content(parent, database_path, refresh_trainings_screen, selected_filter, access_role)

    return refresh_trainings_screen
