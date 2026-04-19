import customtkinter as ctk

from osah.ui.desktop.content.ctk_styles import CARD, label_title, label_body, pill_label
from osah.ui.desktop.security.apply_desktop_theme import STYLE_TOKENS


# ###### ВІДОБРАЖЕННЯ КАРТКИ READ-ONLY ПОВІДОМЛЕННЯ / ОТРИСОВКА КАРТОЧКИ READ-ONLY СООБЩЕНИЯ ######
def render_read_only_notice_card(parent, title_text: str, message_text: str) -> None:
    """Показує повідомлення про доступ лише для перегляду.
    Показывает сообщение о доступе только для просмотра.
    """

    notice_frame = ctk.CTkFrame(parent, **CARD)
    notice_frame.pack(fill="x", padx=24, pady=(0, 20))

    pill_label(notice_frame, title_text, STYLE_TOKENS["warning_background"]).pack(anchor="w", padx=20, pady=(18, 0))
    label_title(notice_frame, "Режим перегляду").pack(anchor="w", padx=20, pady=(10, 0))
    label_body(notice_frame, message_text, wraplength=900).pack(anchor="w", padx=20, pady=(8, 18))
