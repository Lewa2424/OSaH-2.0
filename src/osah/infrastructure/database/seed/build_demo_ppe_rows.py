from datetime import date, timedelta


# ###### ПОБУДОВА ДЕМО-ЗАПИСІВ ЗІЗ / ПОСТРОЕНИЕ ДЕМО-ЗАПИСЕЙ СИЗ ######
def build_demo_ppe_rows(employee_rows: list[tuple[str, str, str, str, str]]) -> list[tuple[str, str, int, int, str, str, int, str]]:
    """Повертає демонстраційні записи ЗІЗ з актуальними, простроченими та проблемними станами.
    Возвращает демонстрационные записи СИЗ с актуальными, просроченными и проблемными состояниями.
    """

    today = date.today()
    ppe_catalog = ("Каска захисна", "Окуляри захисні", "Рукавиці комбіновані", "Черевики захисні", "Костюм робочий")
    rows: list[tuple[str, str, int, int, str, str, int, str]] = []

    for index, employee_row in enumerate(row for row in employee_rows if row[4] == "active"):
        personnel_number = employee_row[0]
        for ppe_index, ppe_name in enumerate(ppe_catalog[: 3 + (index % 2)]):
            issue_date = today - timedelta(days=160 + (index * 3 + ppe_index * 11) % 240)
            replacement_date = issue_date + timedelta(days=180 + ppe_index * 40)
            is_issued = 0 if (index + ppe_index) % 13 == 0 else 1
            rows.append(
                (
                    personnel_number,
                    ppe_name,
                    1,
                    is_issued,
                    issue_date.isoformat(),
                    replacement_date.isoformat(),
                    1 if ppe_name != "Рукавиці комбіновані" else 2,
                    "Норма видачі за посадою та виробничою дільницею.",
                )
            )

    return rows
