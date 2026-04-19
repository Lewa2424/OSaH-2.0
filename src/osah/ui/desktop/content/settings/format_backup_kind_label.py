from osah.domain.entities.backup_kind import BackupKind


# ###### ФОРМАТУВАННЯ ТИПУ РЕЗЕРВНОЇ КОПІЇ / ФОРМАТИРОВАНИЕ ТИПА РЕЗЕРВНОЙ КОПИИ ######
def format_backup_kind_label(backup_kind: BackupKind) -> str:
    """Повертає локалізовану мітку типу резервної копії.
    Возвращает локализованную метку типа резервной копии.
    """

    if backup_kind == BackupKind.MANUAL:
        return "Ручна"
    if backup_kind == BackupKind.AUTO:
        return "Авто"
    return "Страховочна"
