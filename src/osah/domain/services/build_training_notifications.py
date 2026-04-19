from osah.domain.entities.employee import Employee
from osah.domain.entities.notification_item import NotificationItem
from osah.domain.entities.notification_kind import NotificationKind
from osah.domain.entities.notification_level import NotificationLevel
from osah.domain.entities.training_record import TrainingRecord
from osah.domain.entities.training_status import TrainingStatus
from osah.domain.services.format_training_type_label import format_training_type_label


# ###### ПОБУДОВА СПОВІЩЕНЬ ІНСТРУКТАЖІВ / ПОСТРОЕНИЕ УВЕДОМЛЕНИЙ ИНСТРУКТАЖЕЙ ######
def build_training_notifications(
    employees: tuple[Employee, ...],
    training_records: tuple[TrainingRecord, ...],
) -> tuple[NotificationItem, ...]:
    """Повертає активні сповіщення за модулем інструктажів.
    Возвращает активные уведомления по модулю инструктажей.
    """

    notifications: list[NotificationItem] = []
    records_by_employee: dict[str, list[TrainingRecord]] = {}
    for training_record in training_records:
        records_by_employee.setdefault(training_record.employee_personnel_number, []).append(training_record)

    for employee in employees:
        if employee.employment_status.strip().lower() != "active":
            continue

        employee_records = records_by_employee.get(employee.personnel_number, [])
        if not employee_records:
            notifications.append(
                NotificationItem(
                    notification_kind=NotificationKind.CONTROL,
                    notification_level=NotificationLevel.CRITICAL,
                    source_module="trainings.registry",
                    title_text="Відсутні записи інструктажів",
                    message_text="Для працівника немає жодного запису інструктажу. Потрібно внести первинні дані.",
                    employee_personnel_number=employee.personnel_number,
                    employee_full_name=employee.full_name,
                )
            )
            continue

        for training_record in employee_records:
            if training_record.status == TrainingStatus.OVERDUE:
                notifications.append(
                    NotificationItem(
                        notification_kind=NotificationKind.CONTROL,
                        notification_level=NotificationLevel.CRITICAL,
                        source_module="trainings.registry",
                        title_text="Прострочений інструктаж",
                        message_text=f"Інструктаж '{format_training_type_label(training_record.training_type)}' прострочений відносно дати контролю {training_record.next_control_date}.",
                        employee_personnel_number=employee.personnel_number,
                        employee_full_name=employee.full_name,
                    )
                )
            elif training_record.status == TrainingStatus.WARNING:
                notifications.append(
                    NotificationItem(
                        notification_kind=NotificationKind.CONTROL,
                        notification_level=NotificationLevel.WARNING,
                        source_module="trainings.registry",
                        title_text="Наближається строк інструктажу",
                        message_text=f"Інструктаж '{format_training_type_label(training_record.training_type)}' потребує уваги до {training_record.next_control_date}.",
                        employee_personnel_number=employee.personnel_number,
                        employee_full_name=employee.full_name,
                    )
                )

    return tuple(notifications)
