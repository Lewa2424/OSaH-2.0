from dataclasses import dataclass


@dataclass(slots=True)
class MedicalWorkspaceSummary:
    """Короткі лічильники стану модуля медицини.
    Compact state counters for the medical module.
    """

    total_rows: int
    current_total: int
    warning_total: int
    restricted_total: int
    critical_total: int
