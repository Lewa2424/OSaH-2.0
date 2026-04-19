from enum import StrEnum


class EmployeeImportDraftStatus(StrEnum):
    """Статуси чернетки імпорту працівника.
    Статусы черновика импорта сотрудника.
    """

    NEW = "new"
    UPDATE = "update"
    UNCHANGED = "unchanged"
    INVALID = "invalid"
