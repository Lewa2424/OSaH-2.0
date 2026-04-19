from sqlite3 import Connection

from osah.domain.entities.employee import Employee


# ###### ДОДАВАННЯ АБО ОНОВЛЕННЯ ПРАЦІВНИКА / ДОБАВЛЕНИЕ ИЛИ ОБНОВЛЕНИЕ СОТРУДНИКА ######
def upsert_employee_row(connection: Connection, employee: Employee) -> None:
    """Створює або оновлює працівника за табельним номером.
    Создаёт или обновляет сотрудника по табельному номеру.
    """

    existing_row = connection.execute(
        """
        SELECT 1
        FROM employees
        WHERE personnel_number = ?;
        """,
        (employee.personnel_number,),
    ).fetchone()
    if existing_row is None:
        connection.execute(
            """
            INSERT INTO employees (
                personnel_number,
                full_name,
                position_name,
                department_name,
                employment_status
            )
            VALUES (?, ?, ?, ?, ?);
            """,
            (
                employee.personnel_number,
                employee.full_name,
                employee.position_name,
                employee.department_name,
                employee.employment_status,
            ),
        )
        return

    connection.execute(
        """
        UPDATE employees
        SET
            full_name = ?,
            position_name = ?,
            department_name = ?,
            employment_status = ?
        WHERE personnel_number = ?;
        """,
        (
            employee.full_name,
            employee.position_name,
            employee.department_name,
            employee.employment_status,
            employee.personnel_number,
        ),
    )
