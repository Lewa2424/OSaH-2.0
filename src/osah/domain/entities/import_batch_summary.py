from dataclasses import dataclass


@dataclass(slots=True)
class ImportBatchSummary:
    """Підсумок партії імпорту для екрана перевірки.
    Итог партии импорта для экрана проверки.
    """

    batch_id: int
    source_name: str
    source_format: str
    entity_scope: str
    draft_total: int
    valid_total: int
    invalid_total: int
    applied_at: str | None
    created_at: str
