from osah.domain.entities.employee import Employee
from osah.domain.entities.notification_item import NotificationItem
from osah.domain.entities.notification_kind import NotificationKind
from osah.domain.entities.notification_level import NotificationLevel
from osah.domain.entities.ppe_compliance_check_state import PpeComplianceCheckState
from osah.domain.entities.ppe_record import PpeRecord
from osah.domain.entities.ppe_status import PpeStatus


# ###### ПОСТРОЕНИЕ УВЕДОМЛЕНИЙ СИЗ / BUILD PPE NOTIFICATIONS ######
def build_ppe_notifications(
    employees: tuple[Employee, ...],
    ppe_records: tuple[PpeRecord, ...],
) -> tuple[NotificationItem, ...]:
    """Возвращает активные уведомления по модулю СИЗ.
    Returns active notifications for the PPE module.
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
                        message_text=f"ЗІЗ '{ppe_record.ppe_name}' належить працівнику, але не виданий.",
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

            if ppe_record.compliance_check_state == PpeComplianceCheckState.NOT_CHECKED:
                notifications.append(
                    NotificationItem(
                        notification_kind=NotificationKind.CONTROL,
                        notification_level=NotificationLevel.WARNING,
                        source_module="ppe.registry",
                        title_text="Відповідність ЗІЗ не підтверджена",
                        message_text=f"Для '{ppe_record.ppe_name}' не зафіксована перевірка відповідності умовам роботи.",
                        employee_personnel_number=employee.personnel_number,
                        employee_full_name=employee.full_name,
                    )
                )

    return tuple(notifications)
