from datetime import date

from osah.domain.entities.training_registry_filter import TrainingRegistryFilter
from osah.domain.entities.training_status import TrainingStatus
from osah.domain.entities.training_type import TrainingType
from osah.domain.services.format_training_type_label import format_training_type_label
from osah.domain.services.format_ui_date import format_ui_date


# ###### ПРИЧИНА СТАТУСУ ІНСТРУКТАЖУ / BUILD TRAINING STATUS REASON ######
def build_training_status_reason(
    status: TrainingStatus | TrainingRegistryFilter,
    training_type: TrainingType | None,
    next_control_date: str,
    today: date | None = None,
) -> str:
    """Пояснює, чому інструктаж має конкретний статус.
    Explains why a training record has a specific status.
    """

    type_label = format_training_type_label(training_type) if training_type else "обов'язковий"
    if status == TrainingRegistryFilter.MISSING:
        return f"Критично - {type_label} інструктаж відсутній"
    if not next_control_date.strip() or next_control_date == "-":
        return "Актуально - запис не переносить план повторного інструктажу"

    current_date = today or date.today()
    remaining_days = (date.fromisoformat(next_control_date) - current_date).days
    if status == TrainingStatus.OVERDUE or status == TrainingRegistryFilter.OVERDUE:
        return f"Критично - {type_label} інструктаж прострочено"
    if status == TrainingStatus.WARNING or status == TrainingRegistryFilter.WARNING:
        return f"Увага - через {remaining_days} дн. спливає строк"
    return f"Актуально - контроль до {format_ui_date(next_control_date)}"
