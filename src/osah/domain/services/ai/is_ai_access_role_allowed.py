from osah.domain.entities.access_role import AccessRole


def is_ai_access_role_allowed(access_role: AccessRole) -> bool:
    """Перевіряє, чи дозволено користувачу AI-команди.
    Checks whether the current role may use AI commands.
    """

    return access_role == AccessRole.INSPECTOR
