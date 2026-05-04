from enum import StrEnum


class TrainingKnowledgeCheckResult(StrEnum):
    """Результат проверки знаний по инструктажу.
    Knowledge-check result for a training record.
    """

    SATISFACTORY = "satisfactory"
    UNSATISFACTORY = "unsatisfactory"
    NOT_APPLICABLE = "not_applicable"
    LEGACY_NOT_TRACKED = "legacy_not_tracked"
