import customtkinter as ctk

from osah.ui.desktop.content.ctk_styles import (
    CARD, INSET, BTN,
    label_content_title, label_body, label_title, label_body as _lb, label_muted, label_metric_value, pill_label,
)
from osah.ui.desktop.security.apply_desktop_theme import STYLE_TOKENS
from osah.domain.entities.dashboard_snapshot import DashboardSnapshot
from osah.ui.desktop.content.render_news_preview_feed import render_news_preview_feed
from osah.ui.desktop.content.render_notification_feed import render_notification_feed


# ###### ВІДОБРАЖЕННЯ ГОЛОВНОГО ЕКРАНА / ОТРИСОВКА ГЛАВНОГО ЭКРАНА ######
def render_dashboard_content(parent, snapshot: DashboardSnapshot) -> None:
    """Відображає управлінське зведення, фокус дня і стрічки сигналів на головному екрані.
    Отрисовывает управленческую сводку, фокус дня и ленты сигналов на главном экране.
    """

    label_content_title(parent, "Головна").pack(anchor="w", padx=24, pady=(24, 8))
    label_body(
        parent,
        "Операційний зріз по локальному контуру: працівники, контрольні сигнали, focus of the day і зовнішній блок Новини / НПА.",
        wraplength=980,
    ).pack(anchor="w", padx=24, pady=(0, 16))

    # ---- Картка "Фокус дня" ----
    focus_frame = ctk.CTkFrame(parent, **CARD)
    focus_frame.pack(fill="x", padx=24, pady=(0, 16))
    label_title(focus_frame, "Фокус дня").pack(anchor="w", padx=24, pady=(20, 0))
    label_body(focus_frame, snapshot.focus_of_the_day, wraplength=980).pack(anchor="w", padx=24, pady=(10, 20))

    # ---- Метрики ----
    cards_outer = ctk.CTkFrame(parent, fg_color="transparent", corner_radius=0)
    cards_outer.pack(fill="x", padx=24, pady=(0, 20))
    for column_index in range(4):
        cards_outer.grid_columnconfigure(column_index, weight=1)

    metric_specs = (
        ("Працівники", str(snapshot.employee_total), "Активний кадровий контур у локальній БД.", STYLE_TOKENS["info_background"]),
        ("Критичні проблеми", str(snapshot.critical_items), "Недопуски, прострочки і критичні сигнали.", STYLE_TOKENS["critical_background"]),
        ("Потребують уваги", str(snapshot.warning_items), "Події, що наближаються до порогу ризику.", STYLE_TOKENS["warning_background"]),
        ("Нові матеріали", str(snapshot.unread_news_total), "Непрочитані новини і зміни НПА.", "#8B5CF6"),
    )
    for column_index, (title_text, value_text, note_text, accent_color) in enumerate(metric_specs):
        card = ctk.CTkFrame(
            cards_outer,
            fg_color=STYLE_TOKENS["surface_background"],
            corner_radius=20,
            border_width=3,
            border_color=accent_color,
        )
        card.grid(row=0, column=column_index, sticky="nsew", padx=(0 if column_index == 0 else 12, 0))

        label_muted(card, title_text).pack(anchor="w", padx=20, pady=(20, 0))
        label_metric_value(card, value_text).pack(anchor="w", padx=20, pady=(8, 4))
        ctk.CTkLabel(
            card,
            text=note_text,
            text_color=STYLE_TOKENS["muted_text"],
            font=("Segoe UI", 9),
            anchor="w",
            wraplength=180,
            justify="left",
        ).pack(anchor="w", padx=20, pady=(0, 20))

    render_notification_feed(parent, snapshot.active_notifications)
    render_news_preview_feed(parent, snapshot.unread_news_total, snapshot.latest_news_items)
