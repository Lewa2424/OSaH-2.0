from osah.domain.entities.work_permit_target_training_status import WorkPermitTargetTrainingStatus
from osah.domain.services.normalize_work_permit_target_training_status import normalize_work_permit_target_training_status


def format_work_permit_target_training_status_label(
    target_training_status: WorkPermitTargetTrainingStatus,
) -> str:
    """Повертає українську мітку стану цільового інструктажу НД.
    Returns a Ukrainian label for a work permit targeted-training state.
    """

    normalized_status = normalize_work_permit_target_training_status(target_training_status)
    return {
        WorkPermitTargetTrainingStatus.LEGACY_NOT_TRACKED: "Не фіксувалось",
        WorkPermitTargetTrainingStatus.NOT_DONE: "Не проведено",
        WorkPermitTargetTrainingStatus.DONE_PASSED: "Проведено, перевірка знань пройдена — допуск",
        WorkPermitTargetTrainingStatus.DONE_FAILED: "Проведено, перевірка знань не пройдена — не допуск",
    }[normalized_status]
