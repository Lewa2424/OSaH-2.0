from datetime import date

from osah.domain.entities.training_next_control_basis import TrainingNextControlBasis
from osah.domain.entities.training_record import TrainingRecord
from osah.domain.entities.training_status import TrainingStatus
from osah.domain.entities.training_type import TrainingType


# ###### ОЦЕНКА СТАТУСА ИНСТРУКТАЖА / EVALUATE TRAINING STATUS ######
def evaluate_training_status(
    training_record: TrainingRecord,
    related_training_records: tuple[TrainingRecord, ...] = (),
    today: date | None = None,
    warning_days: int = 30,
) -> TrainingStatus:
    """Возвращает статус записи инструктажа по дате контроля и связанным записям.
    Returns the status of a training record using its control date and related records.
    """

    current_date = today or date.today()
    related_records = related_training_records or (training_record,)

    if training_record.training_type == TrainingType.INTRODUCTORY:
        if training_record.next_control_basis == TrainingNextControlBasis.INTRODUCTORY_PRIMARY_NOT_REQUIRED:
            return TrainingStatus.NOT_REQUIRED
        if training_record.next_control_basis == TrainingNextControlBasis.REQUIRES_PRIMARY_AFTER_INTRODUCTORY:
            introductory_date = date.fromisoformat(training_record.event_date)
            if any(
                related_record.training_type == TrainingType.PRIMARY
                and date.fromisoformat(related_record.event_date) >= introductory_date
                for related_record in related_records
                if related_record.record_id != training_record.record_id
            ):
                return TrainingStatus.CLOSED_BY_PRIMARY

    if (
        not training_record.next_control_date.strip()
        or training_record.next_control_basis == TrainingNextControlBasis.DOES_NOT_CHANGE_REPEATED_CONTROL
    ):
        return TrainingStatus.CURRENT

    next_control = date.fromisoformat(training_record.next_control_date)
    remaining_days = (next_control - current_date).days
    if remaining_days < 0:
        return TrainingStatus.OVERDUE
    if remaining_days <= warning_days:
        return TrainingStatus.WARNING
    return TrainingStatus.CURRENT
