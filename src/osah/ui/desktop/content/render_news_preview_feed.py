import customtkinter as ctk

from osah.domain.entities.news_item import NewsItem
from osah.domain.services.format_news_source_kind_label import format_news_source_kind_label
from osah.ui.desktop.content.ctk_styles import CARD, INSET, label_title, label_body, label_muted, pill_label
from osah.ui.desktop.security.apply_desktop_theme import STYLE_TOKENS


# ###### ВІДОБРАЖЕННЯ ПРЕВ'Ю НОВИН НА ГОЛОВНІЙ / ОТРИСОВКА ПРЕВЬЮ НОВОСТЕЙ НА ГЛАВНОЙ ######
def render_news_preview_feed(parent, unread_news_total: int, latest_news_items: tuple[NewsItem, ...]) -> None:
    """Відображає нижній блок непрочитаних новин і матеріалів НПА на дашборді.
    Отрисовывает нижний блок непрочитанных новостей и материалов НПА на дашборде.
    """

    preview_frame = ctk.CTkFrame(parent, **CARD)
    preview_frame.pack(fill="x", padx=24, pady=(0, 24))

    label_title(preview_frame, "Новини / НПА").pack(anchor="w", padx=24, pady=(20, 0))
    label_body(
        preview_frame,
        f"Непрочитаних матеріалів у локальному кеші: {unread_news_total}",
    ).pack(anchor="w", padx=24, pady=(8, 0))

    if not latest_news_items:
        label_muted(preview_frame, "У локальному кеші ще немає нових матеріалів зовнішнього контуру.").pack(
            anchor="w", padx=24, pady=(14, 20)
        )
        return

    for news_item in latest_news_items:
        item_frame = ctk.CTkFrame(preview_frame, **INSET)
        item_frame.pack(fill="x", padx=24, pady=(12, 0))

        pill_label(item_frame, format_news_source_kind_label(news_item.source_kind), STYLE_TOKENS["info_background"]).pack(
            anchor="w", padx=16, pady=(14, 0)
        )
        label_title(item_frame, news_item.title_text, wraplength=920).pack(anchor="w", padx=16, pady=(10, 0))
        label_body(
            item_frame,
            f"{news_item.source_name} | {news_item.published_at_text or '-'}",
            wraplength=920,
        ).pack(anchor="w", padx=16, pady=(6, 14))

    ctk.CTkFrame(preview_frame, fg_color="transparent", height=8).pack()
