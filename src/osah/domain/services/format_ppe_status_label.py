from osah.domain.entities.ppe_status import PpeStatus


# ###### ФОРМАТУВАННЯ СТАТУСУ ЗІЗ / FORMAT PPE STATUS ######
def format_ppe_status_label(status: PpeStatus) -> str:
    """Повертає україномовну назву статусу ЗІЗ.
    Returns a Ukrainian PPE status label.
    """

    if status == PpeStatus.CURRENT:
        return "Актуально"
    if status == PpeStatus.WARNING:
        return "Увага"
    if status == PpeStatus.EXPIRED:
        return "Критично"
    return "Не видано"
