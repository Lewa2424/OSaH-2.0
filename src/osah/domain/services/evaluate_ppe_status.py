from datetime import date

from osah.domain.entities.ppe_provision_status import PpeProvisionStatus
from osah.domain.entities.ppe_record import PpeRecord
from osah.domain.entities.ppe_status import PpeStatus


# ###### ОЦЕНКА СТАТУСА СИЗ / EVALUATE PPE STATUS ######
def evaluate_ppe_status(
    ppe_record: PpeRecord,
    today: date | None = None,
    warning_days: int = 7,
) -> PpeStatus:
    """Возвращает статус записи СИЗ по новому provision_status и сроку замены.
    Returns PPE status using the new provision status and replacement date.
    """

    effective_provision_status = ppe_record.provision_status
    if effective_provision_status == PpeProvisionStatus.LEGACY_NOT_TRACKED:
        if ppe_record.is_required and not ppe_record.is_issued:
            effective_provision_status = PpeProvisionStatus.REQUIRED_NOT_ISSUED
        elif not ppe_record.is_required:
            effective_provision_status = PpeProvisionStatus.NOT_REQUIRED
        else:
            effective_provision_status = PpeProvisionStatus.ISSUED

    if effective_provision_status == PpeProvisionStatus.REQUIRED_NOT_ISSUED:
        return PpeStatus.NOT_ISSUED
    if effective_provision_status in {
        PpeProvisionStatus.NOT_REQUIRED,
        PpeProvisionStatus.LEGACY_NOT_TRACKED,
    }:
        return PpeStatus.CURRENT

    current_date = today or date.today()
    replacement_date = date.fromisoformat(ppe_record.replacement_date)
    remaining_days = (replacement_date - current_date).days
    if remaining_days < 0:
        return PpeStatus.EXPIRED
    if remaining_days <= warning_days:
        return PpeStatus.WARNING
    return PpeStatus.CURRENT
