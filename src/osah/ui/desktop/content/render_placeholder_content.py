import customtkinter as ctk

from osah.domain.entities.app_section import AppSection
from osah.ui.desktop.content.ctk_styles import label_body


# ###### ВІДОБРАЖЕННЯ ЗАГЛУШКИ РОЗДІЛУ / ОТРИСОВКА ЗАГЛУШКИ РАЗДЕЛА ######
def render_placeholder_content(parent, section: AppSection) -> None:
    """Показує архітектурну заглушку для ще не реалізованого розділу.
    Показывает архитектурную заглушку для ещё не реализованного раздела.
    """

    label_body(
        parent,
        f"Розділ '{section.value}' виділено в архітектурі та буде реалізовано окремим модулем.",
        wraplength=880,
    ).pack(anchor="w", padx=24, pady=(0, 8))

    label_body(
        parent,
        "У поточному зрізі тут немає бізнес-логіки, щоб не створювати хибну функціональність.",
        wraplength=880,
    ).pack(anchor="w", padx=24, pady=(0, 24))
