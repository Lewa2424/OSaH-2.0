from osah.domain.entities.employee import Employee
from osah.domain.entities.notification_item import NotificationItem
from osah.domain.entities.notification_kind import NotificationKind
from osah.domain.entities.notification_level import NotificationLevel
from osah.domain.entities.training_record import TrainingRecord
from osah.domain.entities.training_status import TrainingStatus
from osah.domain.entities.training_type import TrainingType
from osah.domain.services.build_training_status_reason import build_training_status_reason


# ###### ПОСТРОЕНИЕ УВЕДОМЛЕНИЙ ИНСТРУКТАЖЕЙ / BUILD TRAINING NOTIFICATIONS ######
def build_training_notifications(
    employees: tuple[Employee, ...],
    training_records: tuple[TrainingRecord, ...],
) -> tuple[NotificationItem, ...]:
    """Возвращает активные контрольные уведомления по модулю инструктажей.
    Returns active control notifications for the trainings module.
    """

    notifications: list[NotificationItem] = []
    records_by_employee: dict[str, tuple[TrainingRecord, ...]] = {}
    for training_record in training_records:
        records_by_employee.setdefault(training_record.employee_personnel_number, tuple())
        records_by_employee[training_record.employee_personnel_number] = (
            *records_by_employee[training_record.employee_personnel_number],
            training_record,
        )

    for employee in employees:
        if employee.employment_status.strip().lower() != "active":
            continue

        employee_records = records_by_employee.get(employee.personnel_number, ())
        if _should_raise_missing_primary(employee_records):
            notifications.append(
                NotificationItem(
                    notification_kind=NotificationKind.CONTROL,
                    notification_level=NotificationLevel.CRITICAL,
                    source_module="trainings.registry",
                    title_text="Відсутній первинний інструктаж",
                    message_text="Для працівника відсутній обов'язковий первинний інструктаж.",
                    employee_personnel_number=employee.personnel_number,
                    employee_full_name=employee.full_name,
                )
            )

        for training_record in employee_records:
            if training_record.status == TrainingStatus.OVERDUE:
                notifications.append(
                    NotificationItem(
                        notification_kind=NotificationKind.CONTROL,
                        notification_level=NotificationLevel.CRITICAL,
                        source_module="trainings.registry",
                        title_text=_build_notification_title(training_record, is_warning=False),
                        message_text=build_training_status_reason(
                            training_record.status,
                            training_record.training_type,
                            training_record.next_control_date,
                            training_record.next_control_basis,
                        ),
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
                        title_text=_build_notification_title(training_record, is_warning=True),
                        message_text=build_training_status_reason(
                            training_record.status,
                            training_record.training_type,
                            training_record.next_control_date,
                            training_record.next_control_basis,
                        ),
                        employee_personnel_number=employee.personnel_number,
                        employee_full_name=employee.full_name,
                    )
                )

    return tuple(notifications)


def _should_raise_missing_primary(employee_records: tuple[TrainingRecord, ...]) -> bool:
    """Определяет, нужно ли поднимать отдельную проблему отсутствующего первичного.
    Determines whether a dedicated missing-primary problem must be raised.
    """

    if not employee_records:
        return True

    latest_introductory = max(
        (record for record in employee_records if record.training_type == TrainingType.INTRODUCTORY),
        key=lambda record: record.event_date,
        default=None,
    )
    if latest_introductory is not None:
        return False

    return not any(record.training_type == TrainingType.PRIMARY for record in employee_records)


def _build_notification_title(training_record: TrainingRecord, is_warning: bool) -> str:
    """Возвращает короткий заголовок уведомления по типу проблемы инструктажа.
    Returns a short notification title based on the training problem type.
    """

    if training_record.training_type == TrainingType.INTRODUCTORY:
        return "Потрібен первинний після вступного" if is_warning else "Прострочено первинний після вступного"
    return "Скоро спливає строк повторного інструктажу" if is_warning else "Прострочено повторний інструктаж"
