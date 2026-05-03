from datetime import date

from osah.domain.entities.training_next_control_basis import TrainingNextControlBasis
from osah.domain.entities.training_person_category import TrainingPersonCategory
from osah.domain.entities.training_type import TrainingType
from osah.domain.entities.training_work_risk_category import TrainingWorkRiskCategory
from osah.domain.services.calculate_next_training_control_date import calculate_next_training_control_date
from osah.domain.services.does_training_context_require_primary import does_training_context_require_primary


# ###### ОПРЕДЕЛЕНИЕ КОНТРОЛЬНОЙ ДАТЫ ИНСТРУКТАЖА / RESOLVE TRAINING CONTROL DATE ######
def resolve_training_next_control_date(
    training_type: TrainingType,
    event_date: date,
    person_category: TrainingPersonCategory,
    requires_primary_on_workplace: bool,
    work_risk_category: TrainingWorkRiskCategory,
    manual_next_control_date: date | None,
    should_update_repeated_control: bool,
    use_manual_next_control_date: bool,
) -> tuple[str, TrainingNextControlBasis, TrainingWorkRiskCategory]:
    """Возвращает контрольную дату, основание расчёта и категорию работ для записи инструктажа.
    Returns the control date, calculation basis, and work category for a training record.
    """

    if training_type == TrainingType.INTRODUCTORY:
        if does_training_context_require_primary(person_category, requires_primary_on_workplace):
            return (
                event_date.isoformat(),
                TrainingNextControlBasis.REQUIRES_PRIMARY_AFTER_INTRODUCTORY,
                TrainingWorkRiskCategory.NOT_APPLICABLE,
            )
        return (
            "",
            TrainingNextControlBasis.INTRODUCTORY_PRIMARY_NOT_REQUIRED,
            TrainingWorkRiskCategory.NOT_APPLICABLE,
        )

    if use_manual_next_control_date or (
        manual_next_control_date is not None
        and work_risk_category == TrainingWorkRiskCategory.NOT_APPLICABLE
    ):
        return _resolve_manual_next_control_date(manual_next_control_date, work_risk_category)

    if training_type == TrainingType.PRIMARY:
        return _resolve_calculated_next_control_date(
            event_date,
            work_risk_category,
            TrainingNextControlBasis.CALCULATED_AFTER_PRIMARY_3M,
            TrainingNextControlBasis.CALCULATED_AFTER_PRIMARY_6M,
        )
    if training_type == TrainingType.REPEATED:
        return _resolve_calculated_next_control_date(
            event_date,
            work_risk_category,
            TrainingNextControlBasis.CALCULATED_AFTER_REPEATED_3M,
            TrainingNextControlBasis.CALCULATED_AFTER_REPEATED_6M,
        )

    if not should_update_repeated_control:
        return (
            "",
            TrainingNextControlBasis.DOES_NOT_CHANGE_REPEATED_CONTROL,
            TrainingWorkRiskCategory.NOT_APPLICABLE,
        )

    if training_type == TrainingType.UNSCHEDULED:
        return _resolve_calculated_next_control_date(
            event_date,
            work_risk_category,
            TrainingNextControlBasis.RECALCULATED_AFTER_UNSCHEDULED_3M,
            TrainingNextControlBasis.RECALCULATED_AFTER_UNSCHEDULED_6M,
        )
    return _resolve_calculated_next_control_date(
        event_date,
        work_risk_category,
        TrainingNextControlBasis.RECALCULATED_AFTER_TARGETED_3M,
        TrainingNextControlBasis.RECALCULATED_AFTER_TARGETED_6M,
    )


def _resolve_manual_next_control_date(
    manual_next_control_date: date | None,
    work_risk_category: TrainingWorkRiskCategory,
) -> tuple[str, TrainingNextControlBasis, TrainingWorkRiskCategory]:
    """Возвращает вручную заданную контрольную дату инструктажа.
    Returns a manually provided training control date.
    """

    if manual_next_control_date is None:
        raise ValueError("Потрібно вказати дату наступного контролю.")
    return (
        manual_next_control_date.isoformat(),
        TrainingNextControlBasis.MANUAL,
        work_risk_category,
    )


def _resolve_calculated_next_control_date(
    event_date: date,
    work_risk_category: TrainingWorkRiskCategory,
    high_risk_basis: TrainingNextControlBasis,
    regular_basis: TrainingNextControlBasis,
) -> tuple[str, TrainingNextControlBasis, TrainingWorkRiskCategory]:
    """Возвращает автоматически рассчитанную контрольную дату инструктажа.
    Returns an automatically calculated training control date.
    """

    next_control_date = calculate_next_training_control_date(event_date, work_risk_category)
    basis = high_risk_basis if work_risk_category == TrainingWorkRiskCategory.HIGH_RISK else regular_basis
    return next_control_date.isoformat(), basis, work_risk_category
