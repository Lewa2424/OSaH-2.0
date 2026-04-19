from collections.abc import Callable
from pathlib import Path
from tkinter import ttk

from osah.domain.entities.access_role import AccessRole
from osah.domain.entities.training_registry_filter import TrainingRegistryFilter


# ###### ПОБУДОВА ОБРОБНИКА ВИБОРУ ФІЛЬТРА ІНСТРУКТАЖІВ / ПОСТРОЕНИЕ ОБРАБОТЧИКА ВЫБОРА ФИЛЬТРА ИНСТРУКТАЖЕЙ ######
def build_training_filter_select_handler(
    parent: ttk.Frame,
    database_path: Path,
    on_refresh: Callable[[], None],
    registry_filter: TrainingRegistryFilter,
    access_role: AccessRole,
) -> Callable[[], None]:
    """Повертає обробник, який перемальовує екран інструктажів із новим фільтром.
    Возвращает обработчик, который перерисовывает экран инструктажей с новым фильтром.
    """

    # ###### ЗМІНА ФІЛЬТРА ІНСТРУКТАЖІВ / СМЕНА ФИЛЬТРА ИНСТРУКТАЖЕЙ ######
    def select_training_filter() -> None:
        """Перемальовує екран інструктажів із вибраним фільтром і роллю доступу.
        Перерисовывает экран инструктажей с выбранным фильтром и ролью доступа.
        """

        from osah.ui.desktop.content.trainings.render_trainings_content import render_trainings_content

        for child in parent.winfo_children():
            child.destroy()
        render_trainings_content(parent, database_path, on_refresh, registry_filter, access_role)

    return select_training_filter
