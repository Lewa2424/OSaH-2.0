from osah.domain.entities.notification_item import NotificationItem


# ###### ПОБУДОВА ЗВЕДЕННЯ ДЖЕРЕЛ СПОВІЩЕНЬ / ПОСТРОЕНИЕ СВОДКИ ИСТОЧНИКОВ УВЕДОМЛЕНИЙ ######
def build_notification_source_summary(notifications: tuple[NotificationItem, ...]) -> tuple[str, ...]:
    """Повертає короткі рядки з кількістю проблем по основних джерелах сповіщень.
    Возвращает короткие строки с количеством проблем по основным источникам уведомлений.
    """

    source_counts: dict[str, int] = {}
    for notification in notifications:
        source_key = _normalize_notification_source(notification.source_module)
        source_counts[source_key] = source_counts.get(source_key, 0) + 1

    ordered_sources = ("trainings", "ppe", "medical", "work_permits", "registry")
    return tuple(
        f"{_format_notification_source_label(source_key)}: {source_counts[source_key]}"
        for source_key in ordered_sources
        if source_key in source_counts
    )


# ###### НОРМАЛІЗАЦІЯ ДЖЕРЕЛА СПОВІЩЕННЯ / НОРМАЛИЗАЦИЯ ИСТОЧНИКА УВЕДОМЛЕНИЯ ######
def _normalize_notification_source(source_module: str) -> str:
    """Повертає верхньорівневий ключ модуля за технічним джерелом сповіщення.
    Возвращает верхнеуровневый ключ модуля по техническому источнику уведомления.
    """

    return source_module.split(".", maxsplit=1)[0].strip()


# ###### ФОРМАТУВАННЯ МІТКИ ДЖЕРЕЛА СПОВІЩЕННЯ / ФОРМАТИРОВАНИЕ МЕТКИ ИСТОЧНИКА УВЕДОМЛЕНИЯ ######
def _format_notification_source_label(source_key: str) -> str:
    """Повертає локалізовану мітку джерела сповіщень для звіту.
    Возвращает локализованную метку источника уведомлений для отчёта.
    """

    if source_key == "trainings":
        return "Інструктажі"
    if source_key == "ppe":
        return "ЗІЗ"
    if source_key == "medical":
        return "Медицина"
    if source_key == "work_permits":
        return "Наряди-допуски"
    return "Картки працівників"
