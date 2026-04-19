import customtkinter as ctk
from collections.abc import Callable, Iterable
from tkinter import Misc

from osah.domain.entities.access_role import AccessRole
from osah.domain.entities.app_section import AppSection
from osah.domain.entities.notification_level import NotificationLevel
from osah.domain.services.security.format_access_role_label import format_access_role_label
from osah.ui.desktop.security.apply_desktop_theme import STYLE_TOKENS
from osah.ui.desktop.widgets.format_navigation_button_text import format_navigation_button_text


# ###### СТВОРЕННЯ ЛІВОЇ НАВІГАЦІЇ / СОЗДАНИЕ ЛЕВОЙ НАВИГАЦИИ ######
def build_navigation_frame(
    parent: Misc,
    sections: Iterable[AppSection],
    selected_section: AppSection,
    access_role: AccessRole,
    section_levels: dict[AppSection, NotificationLevel],
    on_select: Callable[[AppSection], None],
) -> ctk.CTkFrame:
    """Створює ліву навігаційну панель з активним пунктом і службовим блоком ролі.
    Создает левую навигационную панель с активным пунктом и служебным блоком роли.
    """

    font_family = "Segoe UI"
    nav_bg = STYLE_TOKENS["nav_background"]
    strong_text = STYLE_TOKENS["strong_text"]
    muted_text = STYLE_TOKENS["muted_text"]

    navigation_frame = ctk.CTkFrame(
        parent,
        fg_color=nav_bg,
        corner_radius=15,
        border_width=1,
        border_color=STYLE_TOKENS["border_color"],
    )

    pad_frame = ctk.CTkFrame(navigation_frame, fg_color="transparent")
    pad_frame.pack(fill="both", expand=True, padx=18, pady=22)

    # ---- Логотип ----
    ctk.CTkLabel(
        pad_frame,
        text="OSaH 2.0 🚀",
        text_color=STYLE_TOKENS["accent_background"],
        font=(font_family, 20, "bold"),
    ).pack(anchor="w")

    ctk.CTkLabel(
        pad_frame,
        text="Локальний пульт інспектора з охорони праці для контролю строків, допусків і критичних сигналів.",
        text_color=muted_text,
        font=(font_family, 11),
        wraplength=230,
        justify="left",
    ).pack(anchor="w", pady=(8, 18))

    # ---- Картка ролі ----
    role_card = ctk.CTkFrame(
        pad_frame,
        fg_color=STYLE_TOKENS["role_card_background"],
        corner_radius=12,
        border_width=1,
        border_color=STYLE_TOKENS["border_color"],
    )
    role_card.pack(fill="x", pady=(0, 14))

    ctk.CTkLabel(
        role_card,
        text="Активна роль",
        text_color=muted_text,
        font=(font_family, 10),
    ).pack(anchor="w", padx=12, pady=(8, 0))

    role_tag_frame = ctk.CTkFrame(
        role_card,
        fg_color=STYLE_TOKENS["role_tag_background"],
        corner_radius=8,
    )
    role_tag_frame.pack(anchor="w", padx=12, pady=(6, 8))

    ctk.CTkLabel(
        role_tag_frame,
        text=format_access_role_label(access_role),
        text_color=STYLE_TOKENS["role_tag_text"],
        font=(font_family, 11, "bold"),
    ).pack(anchor="w", padx=10, pady=4)

    # Перший розділ "службової" групи — перед ним буде separator
    _SECONDARY_SECTIONS_START = AppSection.CONTRACTORS

    # ---- Кнопки навігації ----
    for section in sections:
        is_selected = section == selected_section
        alert_level = section_levels.get(section)

        # Розділювач між основними і службовими розділами
        if section == _SECONDARY_SECTIONS_START:
            ctk.CTkFrame(
                pad_frame,
                fg_color=STYLE_TOKENS["border_color"],
                height=1,
                corner_radius=0,
            ).pack(fill="x", pady=(6, 2))

        # Вычисляем стиль кнопки / Розраховуємо стиль кнопки
        if is_selected:
            fg_color = STYLE_TOKENS["accent_background"]
            text_color = "#FFFFFF"
            hover_color = STYLE_TOKENS["accent_hover_background"]
            border_width = 0
            border_color = STYLE_TOKENS["accent_background"]
        else:
            if alert_level == NotificationLevel.CRITICAL:
                # Чіткий критичний сигнал: жирна рамка + блідо-червоний фон
                fg_color = "#FEF2F2"
                hover_color = "#FEE2E2"
                border_width = 2
                border_color = STYLE_TOKENS["critical_background"]
                text_color = STYLE_TOKENS["strong_text"]
            elif alert_level == NotificationLevel.WARNING:
                # Попередження: звичайна рамка помаранчева
                fg_color = "#FFFBEB"
                hover_color = "#FEF3C7"
                border_width = 1
                border_color = STYLE_TOKENS["warning_background"]
                text_color = STYLE_TOKENS["strong_text"]
            else:
                fg_color = "transparent"
                hover_color = STYLE_TOKENS["nav_surface_hover"]
                border_width = 1
                border_color = STYLE_TOKENS["border_color"]
                text_color = STYLE_TOKENS["strong_text"]

        btn = ctk.CTkButton(
            pad_frame,
            text=format_navigation_button_text(section),
            corner_radius=15,
            fg_color=fg_color,
            text_color=text_color,
            hover_color=hover_color,
            border_width=border_width,
            border_color=border_color,
            font=(font_family, 12, "bold"),
            height=38,
            anchor="center",
            command=lambda s=section: on_select(s),
        )
        btn.pack(fill="x", pady=4)


    # ---- Підвал ----
    footer_frame = ctk.CTkFrame(pad_frame, fg_color="transparent")
    footer_frame.pack(side="bottom", anchor="w", fill="x", pady=(18, 0))
    ctk.CTkLabel(
        footer_frame,
        text="Локальна база, зовнішній контур новин і резервне відновлення працюють без окремого сервера.",
        text_color=STYLE_TOKENS["nav_footer_text"],
        font=(font_family, 11),
        wraplength=220,
        justify="left",
    ).pack(anchor="w", padx=(2, 0))

    return navigation_frame
