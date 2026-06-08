from dataclasses import dataclass


@dataclass(slots=True)
class SectionNavFillBuckets:
    """Уніфіковані лічильники для діаграми nav-кнопки.
    Unified counters for a nav-button fill diagram.
    """

    total: int
    critical: int
    warning: int
    restricted: int
    ok: int
