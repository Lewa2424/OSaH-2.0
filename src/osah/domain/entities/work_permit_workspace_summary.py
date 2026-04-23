from dataclasses import dataclass


@dataclass(slots=True)
class WorkPermitWorkspaceSummary:
    """Короткі лічильники стану модуля нарядів-допусків.
    Compact state counters for the work permits module.
    """

    total_rows: int
    active_total: int
    warning_total: int
    expired_total: int
    closed_total: int
    canceled_total: int
    conflict_total: int
    active_participants_total: int
