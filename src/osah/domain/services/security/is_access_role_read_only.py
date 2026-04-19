from osah.domain.entities.access_role import AccessRole


# ###### ПЕРЕВІРКА РЕЖИМУ ЛИШЕ ПЕРЕГЛЯДУ / ПРОВЕРКА РЕЖИМА ТОЛЬКО ПРОСМОТРА ######
def is_access_role_read_only(access_role: AccessRole) -> bool:
    """Повертає ознаку режиму лише перегляду для поточної ролі.
    Возвращает признак режима только просмотра для текущей роли.
    """

    return access_role == AccessRole.MANAGER
