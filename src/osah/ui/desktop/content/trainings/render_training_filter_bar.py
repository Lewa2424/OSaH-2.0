from collections.abc import Callable
from pathlib import Path
import customtkinter as ctk

from osah.domain.entities.access_role import AccessRole
from osah.domain.entities.training_registry_filter import TrainingRegistryFilter
from osah.ui.desktop.content.trainings.build_training_filter_select_handler import build_training_filter_select_handler
from osah.ui.desktop.content.trainings.format_training_registry_filter_label import format_training_registry_filter_label
from osah.ui.desktop.content.ctk_styles import CARD, BTN, BTN_SEC, label_title, label_body


# ###### ВІДОБРАЖЕННЯ ПАНЕЛІ ФІЛЬТРІВ ІНСТРУКТАЖІВ / ОТРИСОВКА ПАНЕЛИ ФИЛЬТРОВ ИНСТРУКТАЖЕЙ ######
def render_training_filter_bar(
    parent: ctk.CTkFrame,
    database_path: Path,
    on_refresh: Callable[[], None],
    selected_filter: TrainingRegistryFilter,
    access_role: AccessRole,
) -> None:
    """Відображає панель швидких фільтрів для реєстру інструктажів.
    Отрисовывает панель быстрых фильтров для реестра инструктажей.
    """

    filter_frame = ctk.CTkFrame(parent, **CARD)
    filter_frame.pack(fill="x", pady=(0, 20))

    label_title(filter_frame, "Фільтри реєстру").pack(anchor="w", padx=20, pady=(18, 0))
    label_body(
        filter_frame,
        "Швидкі зрізи по наявності, актуальності та простроченню інструктажів.",
        wraplength=420,
    ).pack(anchor="w", padx=20, pady=(8, 0))

    buttons_frame = ctk.CTkFrame(filter_frame, fg_color="transparent")
    buttons_frame.pack(anchor="w", padx=20, pady=(14, 20))

    for registry_filter in TrainingRegistryFilter:
        button_text = format_training_registry_filter_label(registry_filter)
        is_selected = registry_filter == selected_filter
        
        style = BTN if is_selected else BTN_SEC
        
        ctk.CTkButton(
            buttons_frame,
            text=button_text,
            command=build_training_filter_select_handler(
                parent,
                database_path,
                on_refresh,
                registry_filter,
                access_role,
            ),
            **style,
        ).pack(side="left", padx=(0, 8))
