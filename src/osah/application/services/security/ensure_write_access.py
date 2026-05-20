from osah.domain.entities.access_role import AccessRole
from osah.domain.errors.access_denied_error import AccessDeniedError


def ensure_write_access(access_role: AccessRole, operation_name: str) -> None:
    """Rejects mutating operations for the manager role."""

    if access_role == AccessRole.MANAGER:
        raise AccessDeniedError(f"Доступ заборонено: роль MANAGER не може виконувати '{operation_name}'.")
