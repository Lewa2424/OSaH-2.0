from dataclasses import dataclass


@dataclass(slots=True)
class TrainingWorkspaceSummary:
    """Короткі лічильники стану модуля інструктажів.
    Compact state counters for the trainings module.
    """

    total_rows: int
    current_total: int
    warning_total: int
    critical_total: int
    missing_total: int
