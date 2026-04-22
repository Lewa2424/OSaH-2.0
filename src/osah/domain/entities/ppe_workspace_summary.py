from dataclasses import dataclass


@dataclass(slots=True)
class PpeWorkspaceSummary:
    """Короткі лічильники стану модуля ЗІЗ.
    Compact state counters for the PPE module.
    """

    total_rows: int
    current_total: int
    warning_total: int
    critical_total: int
    not_issued_total: int
