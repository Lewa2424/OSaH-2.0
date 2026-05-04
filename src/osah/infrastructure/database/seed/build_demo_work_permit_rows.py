from datetime import datetime, timedelta


# ###### ПОБУДОВА ДЕМО-НАРЯДІВ-ДОПУСКІВ / BUILD DEMO WORK PERMIT ROWS ######
def build_demo_work_permit_rows(
    employee_rows: list[tuple[str, str, str, str, str]],
) -> tuple[list[tuple[str, str, str, str, str, str, str, str, str | None, str, str, str, str, str, str]], list[tuple[str, str, str]]]:
    """Возвращает демонстрационные наряды-допуски и участников на новой схеме.
    Returns demo work permits and participants using the new schema.
    """

    active_employees = [row for row in employee_rows if row[4] == "active"]
    now = datetime.now().replace(microsecond=0, second=0)
    permit_rows: list[tuple[str, str, str, str, str, str, str, str, str | None, str, str, str, str, str, str]] = []
    participant_rows: list[tuple[str, str, str]] = []
    work_kinds = (
        ("ND-2026-001", "Ремонт електрошафи 0,4 кВ", "Енергетична служба / щитова №2"),
        ("ND-2026-002", "Газополум'яні роботи на трубопроводі", "Зварювальна дільниця"),
        ("ND-2026-003", "Роботи на висоті при ревізії кран-балки", "Механоcкладальний цех"),
        ("ND-2026-004", "Очищення резервуара після промивки", "Склад і логістика"),
        ("ND-2026-005", "Заміна кабелю живлення компресора", "Енергетична служба"),
        ("ND-2026-006", "Зварювання опорної рами", "Зварювальна дільниця"),
        ("ND-2026-007", "Ремонт транспортера подачі", "Ремонтна служба"),
        ("ND-2026-008", "Діагностика вентиляції", "Лабораторія контролю якості"),
    )

    for index, (permit_number, work_kind, work_location) in enumerate(work_kinds):
        starts_at = now - timedelta(hours=12 * index)
        ends_at = starts_at + timedelta(hours=18 + index)
        closed_at = None if index < 5 else (ends_at + timedelta(hours=2)).isoformat(sep=" ")
        permit_rows.append(
            (
                permit_number,
                work_kind,
                work_location,
                starts_at.isoformat(sep=" "),
                ends_at.isoformat(sep=" "),
                "Іваненко Сергій Петрович",
                "Коваль Олена Вікторівна",
                "Контрольований демонстраційний наряд-допуск для типової виробничої ситуації.",
                closed_at,
                "required_not_done" if index < 3 else "done",
                starts_at.date().isoformat() if index >= 3 else "",
                "Старший виробник робіт" if index >= 3 else "",
                "Відмітка про цільовий інструктаж у наряді." if index >= 3 else "",
                "Наряд-допуск підприємства",
                "",
            )
        )
        for offset in range(3):
            employee_row = active_employees[(index * 3 + offset + 2) % len(active_employees)]
            participant_role = "executor" if offset == 0 else "team_member" if offset == 1 else "observer"
            participant_rows.append((permit_number, employee_row[0], participant_role))

    return permit_rows, participant_rows
