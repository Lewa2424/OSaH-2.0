from osah.domain.entities.ppe_status import PpeStatus


# ###### ФОРМАТУВАННЯ СТАТУСУ ЗІЗ / ФОРМАТИРОВАНИЕ СТАТУСА СИЗ ######
def format_ppe_status_label(ppe_status: PpeStatus) -> str:
    """Повертає локалізовану мітку статусу ЗІЗ для UI.
    Возвращает локализованную метку статуса СИЗ для UI.
    """

    if ppe_status == PpeStatus.CURRENT:
        return "Актуально"
    if ppe_status == PpeStatus.WARNING:
        return "Увага"
    if ppe_status == PpeStatus.EXPIRED:
        return "Прострочено"
    return "Не видано"
