from sqlite3 import Connection


# ###### ПІДРАХУНОК ПРАЦІВНИКІВ / ПОДСЧЁТ СОТРУДНИКОВ ######
def count_employees(connection: Connection) -> int:
    """Повертає кількість активних та архівних карток працівників.
    Возвращает количество активных и архивных карточек сотрудников.
    """

    row = connection.execute("SELECT COUNT(*) AS employee_total FROM employees;").fetchone()
    return int(row["employee_total"])
