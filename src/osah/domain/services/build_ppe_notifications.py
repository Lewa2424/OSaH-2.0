from osah.domain.entities.employee import Employee
from osah.domain.entities.notification_item import NotificationItem
from osah.domain.entities.notification_kind import NotificationKind
from osah.domain.entities.notification_level import NotificationLevel
from osah.domain.entities.ppe_record import PpeRecord
from osah.domain.entities.ppe_status import PpeStatus


# ###### ПОБУДОВА СПОВІЩЕНЬ ЗІЗ / ПОСТРОЕНИЕ УВЕДОМЛЕНИЙ СИЗ ######
def build_ppe_notifications(
    employees: tuple[Employee, ...],
    ppe_records: tuple[PpeRecord, ...],
) -> tuple[NotificationItem, ...]:
    """Повертає активні сповіщення за модулем ЗІЗ.
    Возвращает активные уведомления по модулю СИЗ.
    """

    notifications: list[NotificationItem] = []
    records_by_employee: dict[str, list[PpeRecord]] = {}
    for ppe_record in ppe_records:
        records_by_employee.setdefault(ppe_record.employee_personnel_number, []).append(ppe_record)

    for employee in employees:
        if employee.employment_status.strip().lower() != "active":
            continue

        for ppe_record in records_by_employee.get(employee.personnel_number, []):
            if ppe_record.status == PpeStatus.NOT_ISSUED:
                notifications.append(
                    NotificationItem(
                        notification_kind=NotificationKind.CONTROL,
                        notification_level=NotificationLevel.CRITICAL,
                        source_module="ppe.registry",
                        title_text="Обов'язковий ЗІЗ не видано",
                        message_text=f"ЗІЗ '{ppe_record.ppe_name}' обов'язковий, але позначений як не виданий.",
                        employee_personnel_number=employee.personnel_number,
                        employee_full_name=employee.full_name,
                    )
                )
            elif ppe_record.status == PpeStatus.EXPIRED:
                notifications.append(
                    NotificationItem(
                        notification_kind=NotificationKind.CONTROL,
                        notification_level=NotificationLevel.CRITICAL,
                        source_module="ppe.registry",
                        title_text="ЗІЗ потребує заміни",
                        message_text=f"ЗІЗ '{ppe_record.ppe_name}' прострочений відносно дати заміни {ppe_record.replacement_date}.",
                        employee_personnel_number=employee.personnel_number,
                        employee_full_name=employee.full_name,
                    )
                )
            elif ppe_record.status == PpeStatus.WARNING:
                notifications.append(
                    NotificationItem(
                        notification_kind=NotificationKind.CONTROL,
                        notification_level=NotificationLevel.WARNING,
                        source_module="ppe.registry",
                        title_text="Наближається строк заміни ЗІЗ",
                        message_text=f"ЗІЗ '{ppe_record.ppe_name}' потребує уваги до {ppe_record.replacement_date}.",
                        employee_personnel_number=employee.personnel_number,
                        employee_full_name=employee.full_name,
                    )
                )

    return tuple(notifications)
