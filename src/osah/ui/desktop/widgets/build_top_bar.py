import customtkinter as ctk
import tkinter as tk

from osah.domain.entities.access_role import AccessRole
from osah.domain.entities.app_section import AppSection
from osah.domain.entities.notification_level import NotificationLevel
from osah.domain.services.security.format_access_role_label import format_access_role_label
from osah.ui.desktop.security.apply_desktop_theme import STYLE_TOKENS
from osah.ui.desktop.widgets.build_alert_chip_style import build_alert_chip_fg_color
from osah.ui.desktop.widgets.format_alert_chip_text import format_alert_chip_text


# ###### СТВОРЕННЯ ВЕРХНЬОЇ ПАНЕЛІ / СОЗДАНИЕ ВЕРХНЕЙ ПАНЕЛИ ######
def build_top_bar(
    parent: tk.Misc,
    access_role: AccessRole,
    selected_section: AppSection,
    selected_section_level: NotificationLevel | None,
) -> ctk.CTkFrame:
    """Створює верхню службову панель з контекстом активного розділу і ролі.
    Создаёт верхнюю служебную панель с контекстом активного раздела и роли.
    """

    top_bar = ctk.CTkFrame(
        parent,
        fg_color=STYLE_TOKENS["surface_background"],
        corner_radius=16,
        border_width=1,
        border_color=STYLE_TOKENS["border_color"],
    )
    top_bar.grid_columnconfigure(0, weight=1)

    left_frame = ctk.CTkFrame(top_bar, fg_color="transparent")
    left_frame.grid(row=0, column=0, sticky="w", padx=24, pady=18)

    ctk.CTkLabel(
        left_frame,
        text="Робочий контур",
        text_color=STYLE_TOKENS["muted_text"],
        font=("Segoe UI", 9, "bold"),
        anchor="w",
    ).pack(anchor="w")

    ctk.CTkLabel(
        left_frame,
        text=selected_section.value,
        text_color=STYLE_TOKENS["strong_text"],
        font=("Segoe UI", 20, "bold"),
        anchor="w",
    ).pack(anchor="w", pady=(2, 0))

    ctk.CTkLabel(
        left_frame,
        text="Світлий industrial shell з локальним зберіганням, контрольними сигналами і відокремленими доменними модулями.",
        text_color=STYLE_TOKENS["muted_text"],
        font=("Segoe UI", 10),
        anchor="w",
        wraplength=760,
        justify="left",
    ).pack(anchor="w", pady=(6, 0))

    right_frame = ctk.CTkFrame(top_bar, fg_color="transparent")
    right_frame.grid(row=0, column=1, sticky="e", padx=24, pady=18)

    ctk.CTkLabel(
        right_frame,
        text="Стан розділу",
        text_color=STYLE_TOKENS["muted_text"],
        font=("Segoe UI", 9, "bold"),
        anchor="e",
    ).pack(anchor="e")

    chip_fg, chip_text_color = build_alert_chip_fg_color(selected_section_level)
    ctk.CTkLabel(
        right_frame,
        text=format_alert_chip_text(selected_section_level),
        fg_color=chip_fg,
        text_color=chip_text_color,
        corner_radius=12,
        font=("Segoe UI", 9, "bold"),
        padx=10,
        pady=4,
        anchor="e",
    ).pack(anchor="e", pady=(6, 8))

    ctk.CTkLabel(
        right_frame,
        text="Роль доступу",
        text_color=STYLE_TOKENS["muted_text"],
        font=("Segoe UI", 9, "bold"),
        anchor="e",
    ).pack(anchor="e")

    ctk.CTkLabel(
        right_frame,
        text=format_access_role_label(access_role),
        fg_color="#DBEAFE",
        text_color="#1E40AF",
        corner_radius=12,
        font=("Segoe UI", 9, "bold"),
        padx=10,
        pady=4,
        anchor="e",
    ).pack(anchor="e", pady=(6, 0))

    return top_bar
