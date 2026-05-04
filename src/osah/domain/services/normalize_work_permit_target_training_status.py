from osah.domain.entities.work_permit_target_training_status import WorkPermitTargetTrainingStatus


def normalize_work_permit_target_training_status(
    target_training_status: WorkPermitTargetTrainingStatus,
) -> WorkPermitTargetTrainingStatus:
    """Нормалізує старі та нові значення стану цільового інструктажу НД.
    Normalizes legacy and current targeted-training states for a work permit.
    """

    if target_training_status == WorkPermitTargetTrainingStatus.REQUIRED_NOT_DONE:
        return WorkPermitTargetTrainingStatus.NOT_DONE
    if target_training_status == WorkPermitTargetTrainingStatus.DONE:
        return WorkPermitTargetTrainingStatus.DONE_PASSED
    if target_training_status in {
        WorkPermitTargetTrainingStatus.UNKNOWN,
        WorkPermitTargetTrainingStatus.NOT_REQUIRED,
    }:
        return WorkPermitTargetTrainingStatus.LEGACY_NOT_TRACKED
    return target_training_status
