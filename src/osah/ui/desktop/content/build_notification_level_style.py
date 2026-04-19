from osah.domain.entities.notification_level import NotificationLevel
from osah.ui.desktop.security.apply_desktop_theme import STYLE_TOKENS


# ###### ВИБІР КОЛЬОРУ РІВНЯ СПОВІЩЕННЯ / ВЫБОР ЦВЕТА УРОВНЯ УВЕДОМЛЕНИЯ ######
def build_notification_level_fg_color(notification_level: NotificationLevel) -> tuple[str, str]:
    """Повертає (fg_color, text_color) для CTkLabel конкретного рівня сповіщення.
    Возвращает (fg_color, text_color) для CTkLabel конкретного уровня уведомления.
    """

    if notification_level == NotificationLevel.CRITICAL:
        return STYLE_TOKENS["critical_background"], "#FFFFFF"
    if notification_level == NotificationLevel.WARNING:
        return STYLE_TOKENS["warning_background"], "#FFFFFF"
    return STYLE_TOKENS["info_background"], "#FFFFFF"


# ###### ЗВОРОТНА СУМІСНІСТЬ / ОБРАТНАЯ СОВМЕСТИМОСТЬ ######
def build_notification_level_style(notification_level: NotificationLevel) -> str:
    """Зворотна сумісність: повертає ttk-стиль для конкретного рівня.
    Обратная совместимость: возвращает ttk-стиль для конкретного уровня.
    """

    if notification_level == NotificationLevel.CRITICAL:
        return "CriticalPill.TLabel"
    if notification_level == NotificationLevel.WARNING:
        return "WarningPill.TLabel"
    return "InfoPill.TLabel"
