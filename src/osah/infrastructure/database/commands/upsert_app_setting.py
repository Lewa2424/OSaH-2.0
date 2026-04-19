from sqlite3 import Connection


# ###### ДОДАВАННЯ АБО ОНОВЛЕННЯ НАЛАШТУВАННЯ / ДОБАВЛЕНИЕ ИЛИ ОБНОВЛЕНИЕ НАСТРОЙКИ ######
def upsert_app_setting(connection: Connection, setting_key: str, setting_value: str) -> None:
    """Зберігає значення прикладного налаштування за ключем.
    Сохраняет значение прикладной настройки по ключу.
    """

    connection.execute(
        """
        INSERT INTO app_settings (setting_key, setting_value, updated_at)
        VALUES (?, ?, CURRENT_TIMESTAMP)
        ON CONFLICT(setting_key)
        DO UPDATE SET
            setting_value = excluded.setting_value,
            updated_at = CURRENT_TIMESTAMP;
        """,
        (setting_key, setting_value),
    )
