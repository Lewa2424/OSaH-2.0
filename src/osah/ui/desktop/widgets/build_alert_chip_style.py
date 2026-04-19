from osah.domain.entities.notification_level import NotificationLevel
from osah.ui.desktop.security.apply_desktop_theme import STYLE_TOKENS


# ###### ВИБІР КОЛЬОРУ ALERT-CHIP / ВЫБОР ЦВЕТА ALERT-CHIP ######
def build_alert_chip_fg_color(notification_level: NotificationLevel | None) -> tuple[str, str]:
    """Повертає (fg_color, text_color) chip-мітки для рівня візуальної тривоги.
    Возвращает (fg_color, text_color) chip-метки для уровня визуальной тревоги.
    """

    if notification_level == NotificationLevel.CRITICAL:
        return STYLE_TOKENS["critical_background"], "#FFFFFF"
    if notification_level == NotificationLevel.WARNING:
        return STYLE_TOKENS["warning_background"], "#FFFFFF"
    return STYLE_TOKENS["info_background"], "#FFFFFF"


# ###### ЗВОРОТНА СУМІСНІСТЬ / ОБРАТНАЯ СОВМЕСТИМОСТЬ ######
def build_alert_chip_style(notification_level: NotificationLevel | None) -> str:
    """Зворотна сумісність: повертає ttk-стиль для контекстів, де CTk ще не застосовано.
    Обратная совместимость: возвращает ttk-стиль для контекстов, где CTk ещё не применён.
    """

    if notification_level == NotificationLevel.CRITICAL:
        return "CriticalPill.TLabel"
    if notification_level == NotificationLevel.WARNING:
        return "WarningPill.TLabel"
    return "InfoPill.TLabel"
