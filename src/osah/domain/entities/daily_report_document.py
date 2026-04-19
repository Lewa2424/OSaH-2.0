from dataclasses import dataclass


@dataclass(slots=True)
class DailyReportDocument:
    """Згенерований щоденний управлінський звіт.
    Сгенерированный ежедневный управленческий отчёт.
    """

    created_at_text: str
    subject_text: str
    body_text: str
