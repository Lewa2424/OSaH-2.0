from osah.domain.entities.access_role import AccessRole
from osah.domain.entities.app_section import AppSection


# ###### ПОБУДОВА ДОСТУПНИХ РОЗДІЛІВ ДЛЯ РОЛІ / ПОСТРОЕНИЕ ДОСТУПНЫХ РАЗДЕЛОВ ДЛЯ РОЛИ ######
def build_available_sections_for_role(access_role: AccessRole) -> tuple[AppSection, ...]:
    """Повертає список розділів, доступних для поточної ролі.
    Возвращает список разделов, доступных для текущей роли.
    """

    if access_role == AccessRole.INSPECTOR:
        return tuple(AppSection)
    return tuple(section for section in AppSection if section != AppSection.SETTINGS)
