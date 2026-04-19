from sqlite3 import Connection

from osah.domain.entities.employee import Employee


# ###### ЧИТАННЯ СПИСКУ ПРАЦІВНИКІВ / ЧТЕНИЕ СПИСКА СОТРУДНИКОВ ######
def list_employees(connection: Connection) -> tuple[Employee, ...]:
    """Повертає працівників у стабільному порядку для екранів реєстру.
    Возвращает сотрудников в стабильном порядке для экранов реестра.
    """

    rows = connection.execute(
        """
        SELECT
            personnel_number,
            full_name,
            position_name,
            department_name,
            employment_status
        FROM employees
        ORDER BY full_name ASC;
        """
    ).fetchall()
    return tuple(
        Employee(
            personnel_number=row["personnel_number"],
            full_name=row["full_name"],
            position_name=row["position_name"],
            department_name=row["department_name"],
            employment_status=row["employment_status"],
        )
        for row in rows
    )
