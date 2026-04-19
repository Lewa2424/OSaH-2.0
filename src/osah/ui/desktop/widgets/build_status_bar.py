import customtkinter as ctk
import tkinter as tk
from pathlib import Path

from osah.domain.entities.access_role import AccessRole
from osah.domain.services.security.format_access_role_label import format_access_role_label
from osah.ui.desktop.security.apply_desktop_theme import STYLE_TOKENS


# ###### СТВОРЕННЯ РЯДКА СТАНУ / СОЗДАНИЕ СТРОКИ СОСТОЯНИЯ ######
def build_status_bar(parent: tk.Misc, database_path: Path, access_role: AccessRole) -> ctk.CTkFrame:
    """Створює нижній рядок стану з технічним контекстом локальної установки.
    Создаёт нижнюю строку состояния с техническим контекстом локальной установки.
    """

    status_bar = ctk.CTkFrame(
        parent,
        fg_color=STYLE_TOKENS["surface_background"],
        corner_radius=12,
        border_width=1,
        border_color=STYLE_TOKENS["border_color"],
    )
    ctk.CTkLabel(
        status_bar,
        text=(
            f"Локальна БД: {database_path.name} | "
            f"Каталог: {database_path.parent.name} | "
            f"Роль: {format_access_role_label(access_role)}"
        ),
        text_color=STYLE_TOKENS["muted_text"],
        font=("Segoe UI", 10),
        anchor="w",
    ).pack(anchor="w", padx=18, pady=10)
    return status_bar
