from enum import StrEnum


class BackupKind(StrEnum):
    """Типи резервних копій локальної системи.
    Типы резервных копий локальной системы.
    """

    MANUAL = "manual"
    AUTO = "auto"
    SAFETY = "safety"
