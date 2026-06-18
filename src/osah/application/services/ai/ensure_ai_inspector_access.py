from osah.domain.entities.access_role import AccessRole
from osah.domain.errors.access_denied_error import AccessDeniedError
from osah.domain.services.ai.is_ai_access_role_allowed import is_ai_access_role_allowed


def ensure_ai_inspector_access(access_role: AccessRole) -> None:
    """Дозволяє AI-команди лише для ролі інспектора.
    Allows AI commands only for the inspector role.
    """

    if is_ai_access_role_allowed(access_role):
        return
    raise AccessDeniedError("AI-команди доступні лише для ролі інспектора.")
