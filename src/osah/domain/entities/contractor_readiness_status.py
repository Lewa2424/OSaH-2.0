from enum import StrEnum


class ContractorReadinessStatus(StrEnum):
    """Підсумковий статус готовності підрядника.
    Aggregate contractor readiness status.
    """

    READY = "ready"
    WARNING = "warning"
    BLOCKED = "blocked"
    FINISHED = "finished"
    ARCHIVED = "archived"
