from dataclasses import dataclass


@dataclass(slots=True)
class PortShiftAnalyticsSummary:
    """Зведення журналу оцінок змін ПОРТ-Р за період (для блоку аналітики).
    Summary of the PORT-R shift assessment log over a period (for the analytics block).
    """

    assessments_count: int
    green_count: int
    yellow_count: int
    red_count: int
    stop_count: int
    avg_r_dyn: float | None
