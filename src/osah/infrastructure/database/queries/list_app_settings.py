from sqlite3 import Connection


# ###### ЧИТАННЯ ПРИКЛАДНИХ НАЛАШТУВАНЬ / ЧТЕНИЕ ПРИКЛАДНЫХ НАСТРОЕК ######
def list_app_settings(connection: Connection) -> dict[str, str]:
    """Повертає всі прикладні налаштування у вигляді словника ключ-значення.
    Возвращает все прикладные настройки в виде словаря ключ-значение.
    """

    rows = connection.execute(
        """
        SELECT setting_key, setting_value
        FROM app_settings;
        """
    ).fetchall()
    return {row["setting_key"]: row["setting_value"] for row in rows}
