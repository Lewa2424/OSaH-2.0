from osah.domain.entities.access_role import AccessRole


# ###### ФОРМАТУВАННЯ НАЗВИ РОЛІ ДОСТУПУ / ФОРМАТИРОВАНИЕ НАЗВАНИЯ РОЛИ ДОСТУПА ######
def format_access_role_label(access_role: AccessRole) -> str:
    """Повертає україномовну назву ролі доступу для інтерфейсу.
    Возвращает украиноязычное название роли доступа для интерфейса.
    """

    if access_role == AccessRole.INSPECTOR:
        return "Інспектор"
    return "Керівник"
