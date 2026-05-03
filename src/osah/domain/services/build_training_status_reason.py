from datetime import date

from osah.domain.entities.training_next_control_basis import TrainingNextControlBasis
from osah.domain.entities.training_registry_filter import TrainingRegistryFilter
from osah.domain.entities.training_status import TrainingStatus
from osah.domain.entities.training_type import TrainingType
from osah.domain.services.format_ui_date import format_ui_date


# ###### ПРИЧИНА СТАТУСА ИНСТРУКТАЖА / BUILD TRAINING STATUS REASON ######
def build_training_status_reason(
    status: TrainingStatus | TrainingRegistryFilter,
    training_type: TrainingType | None,
    next_control_date: str,
    next_control_basis: TrainingNextControlBasis = TrainingNextControlBasis.MANUAL,
    today: date | None = None,
) -> str:
    """Поясняет, почему инструктаж имеет конкретный статус.
    Explains why a training record has a specific status.
    """

    if status in {TrainingStatus.MISSING, TrainingRegistryFilter.MISSING}:
        return "Критично - відсутній первинний інструктаж"

    if status == TrainingStatus.NOT_REQUIRED and training_type == TrainingType.INTRODUCTORY:
        return "Вступний інструктаж зафіксовано. Первинний у системі підприємства не потрібен"
    if status == TrainingStatus.CLOSED_BY_PRIMARY and training_type == TrainingType.INTRODUCTORY:
        return "Закрито первинним інструктажем на робочому місці"

    if next_control_basis == TrainingNextControlBasis.REQUIRES_PRIMARY_AFTER_INTRODUCTORY:
        if status == TrainingStatus.OVERDUE:
            return "Критично - прострочено первинний після вступного"
        return "Після вступного потрібен первинний інструктаж на робочому місці"

    if not next_control_date.strip() or next_control_date == "-":
        return "Актуально - запис не переносить повторний контроль"

    current_date = today or date.today()
    remaining_days = (date.fromisoformat(next_control_date) - current_date).days
    if status in {TrainingStatus.OVERDUE, TrainingRegistryFilter.OVERDUE}:
        return "Критично - прострочено повторний інструктаж"
    if status in {TrainingStatus.WARNING, TrainingRegistryFilter.WARNING}:
        return f"Увага - через {remaining_days} дн. спливає строк повторного інструктажу"
    return f"Актуально - повторний контроль до {format_ui_date(next_control_date)}"
