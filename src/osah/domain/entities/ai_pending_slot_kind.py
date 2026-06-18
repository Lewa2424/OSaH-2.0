from enum import StrEnum


class AiPendingSlotKind(StrEnum):
    """Недостаючий слот AI-команди, що очікує уточнення.
    Missing AI command slot awaiting user clarification.
    """

    EMPLOYEE = "employee"
    WORK_RISK_CATEGORY = "work_risk_category"
    PPE_ITEM = "ppe_item"
    BULK_AUDIENCE = "bulk_audience"
    ISSUE_DATE = "issue_date"
    TRAINING_TYPE = "training_type"
