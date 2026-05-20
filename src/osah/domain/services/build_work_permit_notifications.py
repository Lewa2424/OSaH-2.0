from datetime import datetime

from osah.domain.entities.employee import Employee
from osah.domain.entities.notification_item import NotificationItem
from osah.domain.entities.notification_kind import NotificationKind
from osah.domain.entities.notification_level import NotificationLevel
from osah.domain.entities.work_permit_record import WorkPermitRecord
from osah.domain.entities.work_permit_status import WorkPermitStatus
from osah.domain.entities.work_permit_target_training_status import WorkPermitTargetTrainingStatus
from osah.domain.services.normalize_work_permit_target_training_status import normalize_work_permit_target_training_status
from osah.domain.services.parse_storage_datetime_text import parse_storage_datetime_text


def build_work_permit_notifications(
    employees: tuple[Employee, ...],
    work_permit_records: tuple[WorkPermitRecord, ...],
) -> tuple[NotificationItem, ...]:
    """Повертає контрольні сповіщення по нарядах.
    Returns control notifications for work permits.
    """

    active_employee_numbers = {
        employee.personnel_number
        for employee in employees
        if employee.employment_status.strip().lower() == "active"
    }

    notifications: list[NotificationItem] = []
    for work_permit_record in work_permit_records:
        if work_permit_record.status in {WorkPermitStatus.CLOSED, WorkPermitStatus.CANCELED, WorkPermitStatus.REISSUED}:
            continue

        normalized_target_training_status = normalize_work_permit_target_training_status(
            work_permit_record.target_training_status
        )
        for personnel_number, full_name in _build_notification_targets(work_permit_record, active_employee_numbers):
            if work_permit_record.status in {WorkPermitStatus.EXPIRED, WorkPermitStatus.INVALID}:
                notifications.append(
                    NotificationItem(
                        notification_kind=NotificationKind.CONTROL,
                        notification_level=NotificationLevel.CRITICAL,
                        source_module="work_permits.registry",
                        title_text="Наряд-допуск проблемний або прострочений",
                        message_text=(
                            f"Наряд {work_permit_record.permit_number} вимагає уваги через статус "
                            f"{work_permit_record.status.value}."
                        ),
                        employee_personnel_number=personnel_number,
                        employee_full_name=full_name,
                    )
                )
            elif work_permit_record.status == WorkPermitStatus.WARNING:
                notifications.append(
                    NotificationItem(
                        notification_kind=NotificationKind.CONTROL,
                        notification_level=NotificationLevel.WARNING,
                        source_module="work_permits.registry",
                        title_text="Наближається завершення наряду-допуску",
                        message_text=f"Наряд {work_permit_record.permit_number} потребує уваги до {work_permit_record.ends_at}.",
                        employee_personnel_number=personnel_number,
                        employee_full_name=full_name,
                    )
                )

            if not personnel_number:
                continue
            if normalized_target_training_status == WorkPermitTargetTrainingStatus.NOT_DONE:
                try:
                    starts_at = parse_storage_datetime_text(work_permit_record.starts_at)
                    has_started = datetime.now() >= starts_at
                except ValueError:
                    has_started = True
                notifications.append(
                    NotificationItem(
                        notification_kind=NotificationKind.CONTROL,
                        notification_level=NotificationLevel.CRITICAL if has_started else NotificationLevel.WARNING,
                        source_module="work_permits.registry",
                        title_text="Не зафіксовано цільовий інструктаж",
                        message_text=f"Для наряду {work_permit_record.permit_number} цільовий інструктаж не проведено.",
                        employee_personnel_number=personnel_number,
                        employee_full_name=full_name,
                    )
                )
            elif normalized_target_training_status == WorkPermitTargetTrainingStatus.DONE_FAILED:
                notifications.append(
                    NotificationItem(
                        notification_kind=NotificationKind.CONTROL,
                        notification_level=NotificationLevel.CRITICAL,
                        source_module="work_permits.registry",
                        title_text="Цільовий інструктаж не пройдено",
                        message_text=(
                            f"За нарядом {work_permit_record.permit_number} цільовий інструктаж проведено, "
                            "але перевірка знань не пройдена. Допуск до робіт заборонено."
                        ),
                        employee_personnel_number=personnel_number,
                        employee_full_name=full_name,
                    )
                )

    return tuple(notifications)


def _build_notification_targets(
    work_permit_record: WorkPermitRecord,
    active_employee_numbers: set[str],
) -> tuple[tuple[str | None, str | None], ...]:
    targets = tuple(
        (participant.employee_personnel_number, participant.employee_full_name)
        for participant in work_permit_record.participants
        if participant.employee_personnel_number in active_employee_numbers
    )
    if targets:
        return targets
    return ((None, None),)
