from enum import StrEnum


class AppSection(StrEnum):
    """Розділи основного desktop-інтерфейсу.
    Разделы основного desktop-интерфейса.
    """

    DASHBOARD = "Головна"
    EMPLOYEES = "Працівники"
    TRAININGS = "Інструктажі"
    PPE = "ЗІЗ"
    MEDICAL = "Медицина"
    WORK_PERMITS = "Наряди-допуски"
    CONTRACTORS = "Підрядники"
    ARCHIVE = "Архів"
    REPORTS = "Звіти"
    NEWS_NPA = "Новини / НПА"
    SETTINGS = "Налаштування"
    ABOUT = "Про програму"
