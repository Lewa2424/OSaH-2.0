from enum import StrEnum


class NavFillSegmentKind(StrEnum):
    """Категорія сегмента діаграми nav-кнопки.
    Category of a nav-button diagram segment.
    """

    CRITICAL = "critical"
    WARNING = "warning"
    RESTRICTED = "restricted"
    OK = "ok"
    NEUTRAL = "neutral"
