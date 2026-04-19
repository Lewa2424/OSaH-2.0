from enum import StrEnum


class AccessRole(StrEnum):
    """Ролі доступу до локальної програми.
    Роли доступа к локальной программе.
    """

    INSPECTOR = "inspector"
    MANAGER = "manager"
