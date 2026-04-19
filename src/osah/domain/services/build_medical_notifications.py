from osah.domain.entities.employee import Employee
from osah.domain.entities.medical_record import MedicalRecord
from osah.domain.entities.medical_status import MedicalStatus
from osah.domain.entities.notification_item import NotificationItem
from osah.domain.entities.notification_kind import NotificationKind
from osah.domain.entities.notification_level import NotificationLevel


# ###### ПОБУДОВА СПОВІЩЕНЬ МЕДИЦИНИ / ПОСТРОЕНИЕ УВЕДОМЛЕНИЙ МЕДИЦИНЫ ######
def build_medical_notifications(
    employees: tuple[Employee, ...],
    medical_records: tuple[MedicalRecord, ...],
) -> tuple[NotificationItem, ...]:
    """Повертає активні сповіщення за модулем медицини.
    Возвращает активные уведомления по модулю медицины.
    """

    notifications: list[NotificationItem] = []
    records_by_employee: dict[str, list[MedicalRecord]] = {}
    for medical_record in medical_records:
        records_by_employee.setdefault(medical_record.employee_personnel_number, []).append(medical_record)

    for employee in employees:
        if employee.employment_status.strip().lower() != "active":
            continue

        for medical_record in records_by_employee.get(employee.personnel_number, []):
            if medical_record.status == MedicalStatus.EXPIRED:
                notifications.append(
                    NotificationItem(
                        notification_kind=NotificationKind.CONTROL,
                        notification_level=NotificationLevel.CRITICAL,
                        source_module="medical.registry",
                        title_text="Строк меддопуску минув",
                        message_text=f"Меддопуск працівника прострочений відносно дати {medical_record.valid_until}.",
                        employee_personnel_number=employee.personnel_number,
                        employee_full_name=employee.full_name,
                    )
                )
            elif medical_record.status == MedicalStatus.NOT_FIT:
                notifications.append(
                    NotificationItem(
                        notification_kind=NotificationKind.CONTROL,
                        notification_level=NotificationLevel.CRITICAL,
                        source_module="medical.registry",
                        title_text="Працівник не допущений за медичним рішенням",
                        message_text="Поточне медичне рішення забороняє допуск працівника до робіт.",
                        employee_personnel_number=employee.personnel_number,
                        employee_full_name=employee.full_name,
                    )
                )
            elif medical_record.status == MedicalStatus.RESTRICTED:
                notifications.append(
                    NotificationItem(
                        notification_kind=NotificationKind.CONTROL,
                        notification_level=NotificationLevel.WARNING,
                        source_module="medical.registry",
                        title_text="Є медичні обмеження",
                        message_text=f"Для працівника зафіксовані обмеження: {medical_record.restriction_note or 'потрібно перевірити деталі'}.",
                        employee_personnel_number=employee.personnel_number,
                        employee_full_name=employee.full_name,
                    )
                )
            elif medical_record.status == MedicalStatus.WARNING:
                notifications.append(
                    NotificationItem(
                        notification_kind=NotificationKind.CONTROL,
                        notification_level=NotificationLevel.WARNING,
                        source_module="medical.registry",
                        title_text="Наближається строк меддопуску",
                        message_text=f"Меддопуск потребує уваги до {medical_record.valid_until}.",
                        employee_personnel_number=employee.personnel_number,
                        employee_full_name=employee.full_name,
                    )
                )

    return tuple(notifications)
