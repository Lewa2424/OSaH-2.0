from osah.domain.entities.training_next_control_basis import TrainingNextControlBasis
from osah.domain.entities.training_record import TrainingRecord
from osah.domain.entities.training_type import TrainingType


# ###### КОНФЛИКТ ХРОНОЛОГИИ ИНСТРУКТАЖЕЙ / TRAINING CHRONOLOGY CONFLICT ######
def find_training_chronology_conflict_reason(
    training_record: TrainingRecord,
    related_training_records: tuple[TrainingRecord, ...],
) -> str | None:
    """Возвращает причину конфликта дат в последовательности инструктажей.
    Returns a date-sequence conflict reason for trainings when chronology is invalid.
    """

    if training_record.training_type == TrainingType.INTRODUCTORY:
        return None

    if training_record.training_type == TrainingType.PRIMARY:
        if _find_introductory_record_before(training_record, related_training_records) is None:
            return "Порушена послідовність інструктажів: первинний інструктаж не може передувати вступному."
        return None

    if not _requires_previous_cycle_record(training_record):
        return None

    if _find_previous_cycle_record(training_record, related_training_records) is None:
        return (
            "Порушена послідовність інструктажів: цей запис не може бути раніше первинного "
            "або попереднього інструктажу циклу повторного контролю."
        )
    return None


def _find_introductory_record_before(
    training_record: TrainingRecord,
    related_training_records: tuple[TrainingRecord, ...],
) -> TrainingRecord | None:
    introductory_records = tuple(
        related_record
        for related_record in related_training_records
        if related_record.training_type == TrainingType.INTRODUCTORY
        and _is_not_same_record(training_record, related_record)
        and related_record.event_date <= training_record.event_date
    )
    if not introductory_records:
        return None
    return max(introductory_records, key=lambda record: (record.event_date, record.record_id or 0))


def _find_previous_cycle_record(
    training_record: TrainingRecord,
    related_training_records: tuple[TrainingRecord, ...],
) -> TrainingRecord | None:
    previous_cycle_records = tuple(
        related_record
        for related_record in related_training_records
        if _is_repeated_cycle_record(related_record)
        and _is_not_same_record(training_record, related_record)
        and related_record.event_date <= training_record.event_date
    )
    if not previous_cycle_records:
        return None
    return max(previous_cycle_records, key=lambda record: (record.event_date, record.record_id or 0))


def _requires_previous_cycle_record(training_record: TrainingRecord) -> bool:
    if training_record.training_type == TrainingType.REPEATED:
        return True
    if training_record.training_type not in {TrainingType.UNSCHEDULED, TrainingType.TARGETED}:
        return False
    return _changes_repeated_control(training_record)


def _is_repeated_cycle_record(training_record: TrainingRecord) -> bool:
    if training_record.training_type in {TrainingType.PRIMARY, TrainingType.REPEATED}:
        return True
    if training_record.training_type not in {TrainingType.UNSCHEDULED, TrainingType.TARGETED}:
        return False
    return _changes_repeated_control(training_record)


def _changes_repeated_control(training_record: TrainingRecord) -> bool:
    return (
        bool(training_record.next_control_date.strip())
        and training_record.next_control_basis != TrainingNextControlBasis.DOES_NOT_CHANGE_REPEATED_CONTROL
    )


def _is_not_same_record(training_record: TrainingRecord, related_record: TrainingRecord) -> bool:
    if training_record.record_id is None or related_record.record_id is None:
        return True
    return training_record.record_id != related_record.record_id
