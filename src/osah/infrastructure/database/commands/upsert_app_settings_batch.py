from sqlite3 import Connection

from osah.infrastructure.database.commands.upsert_app_setting import upsert_app_setting


# ###### ПАКЕТНЕ ОНОВЛЕННЯ НАЛАШТУВАНЬ / ПАКЕТНОЕ ОБНОВЛЕНИЕ НАСТРОЕК ######
def upsert_app_settings_batch(connection: Connection, setting_pairs: dict[str, str]) -> None:
    """Зберігає кілька прикладних налаштувань за один службовий виклик.
    Сохраняет несколько прикладных настроек за один служебный вызов.
    """

    for setting_key, setting_value in setting_pairs.items():
        upsert_app_setting(connection, setting_key, setting_value)
