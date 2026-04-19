from sqlite3 import Connection


# ###### ЧИТАННЯ НАЗВ ТАБЛИЦЬ КОРИСТУВАЦЬКИХ ДАНИХ / ЧТЕНИЕ НАЗВАНИЙ ТАБЛИЦ ПОЛЬЗОВАТЕЛЬСКИХ ДАННЫХ ######
def list_user_table_names(connection: Connection) -> tuple[str, ...]:
    """Повертає назви всіх прикладних таблиць без службових sqlite-таблиць.
    Возвращает названия всех прикладных таблиц без служебных sqlite-таблиц.
    """

    rows = connection.execute(
        """
        SELECT name
        FROM sqlite_master
        WHERE type = 'table'
            AND name NOT LIKE 'sqlite_%'
        ORDER BY name ASC;
        """
    ).fetchall()
    return tuple(row["name"] for row in rows)
