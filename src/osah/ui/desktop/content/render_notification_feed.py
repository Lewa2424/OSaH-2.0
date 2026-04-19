import customtkinter as ctk

from osah.domain.entities.notification_item import NotificationItem
from osah.ui.desktop.content.build_notification_level_style import build_notification_level_fg_color
from osah.ui.desktop.content.format_notification_level_label import format_notification_level_label
from osah.ui.desktop.content.ctk_styles import CARD, INSET, label_title, label_body, label_muted, pill_label
from osah.ui.desktop.security.apply_desktop_theme import STYLE_TOKENS


# ###### ВІДОБРАЖЕННЯ СТРІЧКИ СПОВІЩЕНЬ / ОТРИСОВКА ЛЕНТЫ УВЕДОМЛЕНИЙ ######
def render_notification_feed(parent, notifications: tuple[NotificationItem, ...]) -> None:
    """Відображає активні системні сповіщення на головному екрані.
    Отрисовывает активные системные уведомления на главном экране.
    """

    feed_frame = ctk.CTkFrame(parent, **CARD)
    feed_frame.pack(fill="both", expand=True, padx=24, pady=(0, 20))

    label_title(feed_frame, "Активні сповіщення").pack(anchor="w", padx=24, pady=(20, 0))
    ctk.CTkLabel(
        feed_frame,
        text="Система тримає у фокусі тільки актуальні проблеми. Після усунення причини сповіщення зникає автоматично.",
        text_color=STYLE_TOKENS["muted_text"],
        font=("Segoe UI", 10),
        anchor="w",
        wraplength=980,
        justify="left",
    ).pack(anchor="w", padx=24, pady=(8, 0))

    if not notifications:
        label_muted(feed_frame, "Активних системних сигналів зараз немає.").pack(anchor="w", padx=24, pady=(14, 20))
        return

    for notification in notifications[:6]:
        subject_label = notification.employee_full_name or notification.employee_personnel_number or "Система"
        fg_color, text_color = build_notification_level_fg_color(notification.notification_level)

        line_frame = ctk.CTkFrame(feed_frame, **INSET)
        line_frame.pack(fill="x", padx=24, pady=(12, 0))

        pill_label(line_frame, format_notification_level_label(notification.notification_level), fg_color, text_color).pack(
            anchor="w", padx=16, pady=(14, 0)
        )
        label_title(line_frame, notification.title_text).pack(anchor="w", padx=16, pady=(10, 0))
        label_body(
            line_frame,
            f"{subject_label}: {notification.message_text}",
            wraplength=920,
        ).pack(anchor="w", padx=16, pady=(6, 14))

    ctk.CTkFrame(feed_frame, fg_color="transparent", height=8).pack()
