from osah.domain.entities.employee import Employee
from osah.domain.entities.notification_item import NotificationItem
from osah.domain.entities.notification_kind import NotificationKind
from osah.domain.entities.notification_level import NotificationLevel
from osah.domain.entities.work_permit_record import WorkPermitRecord
from osah.domain.entities.work_permit_status import WorkPermitStatus


# ###### ПОБУДОВА СПОВІЩЕНЬ НАРЯДІВ-ДОПУСКІВ / ПОСТРОЕНИЕ УВЕДОМЛЕНИЙ НАРЯДОВ-ДОПУСКОВ ######
def build_work_permit_notifications(
    employees: tuple[Employee, ...],
    work_permit_records: tuple[WorkPermitRecord, ...],
) -> tuple[NotificationItem, ...]:
    """Повертає активні контрольні сповіщення за модулем нарядів-допусків.
    Возвращает активные контрольные уведомления по модулю нарядов-допусков.
    """

    active_employee_numbers = {
        employee.personnel_number
        for employee in employees
        if employee.employment_status.strip().lower() == "active"
    }

    notifications: list[NotificationItem] = []
    for work_permit_record in work_permit_records:
        if work_permit_record.status == WorkPermitStatus.CLOSED:
            continue

        for participant in work_permit_record.participants:
            if participant.employee_personnel_number not in active_employee_numbers:
                continue

            if work_permit_record.status == WorkPermitStatus.EXPIRED:
                notifications.append(
                    NotificationItem(
                        notification_kind=NotificationKind.CONTROL,
                        notification_level=NotificationLevel.CRITICAL,
                        source_module="work_permits.registry",
                        title_text="Наряд-допуск прострочено",
                        message_text=(
                            f"Наряд {work_permit_record.permit_number} завершився {work_permit_record.ends_at}, "
                            f"але не був закритий вручну."
                        ),
                        employee_personnel_number=participant.employee_personnel_number,
                        employee_full_name=participant.employee_full_name,
                    )
                )
            elif work_permit_record.status == WorkPermitStatus.WARNING:
                notifications.append(
                    NotificationItem(
                        notification_kind=NotificationKind.CONTROL,
                        notification_level=NotificationLevel.WARNING,
                        source_module="work_permits.registry",
                        title_text="Наближається завершення наряду-допуску",
                        message_text=(
                            f"Наряд {work_permit_record.permit_number} потребує уваги до {work_permit_record.ends_at}."
                        ),
                        employee_personnel_number=participant.employee_personnel_number,
                        employee_full_name=participant.employee_full_name,
                    )
                )

    return tuple(notifications)
