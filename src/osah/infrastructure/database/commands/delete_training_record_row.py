from sqlite3 import Connection


# ###### ВИДАЛЕННЯ ЗАПИСУ ІНСТРУКТАЖУ / УДАЛЕНИЕ ЗАПИСИ ИНСТРУКТАЖА ######
def delete_training_record_row(connection: Connection, record_id: int) -> None:
    """Видаляє запис інструктажу з локальної бази.
    Удаляет запись инструктажа из локальной базы.
    """

    connection.execute("DELETE FROM trainings WHERE id = ?;", (record_id,))
