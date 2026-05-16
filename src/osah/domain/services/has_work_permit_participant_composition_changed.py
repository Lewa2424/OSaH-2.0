from osah.domain.entities.work_permit_participant import WorkPermitParticipant


def has_work_permit_participant_composition_changed(
    previous_participants: tuple[WorkPermitParticipant, ...],
    updated_participants: tuple[WorkPermitParticipant, ...],
) -> bool:
    """Проверяет, изменился ли состав бригады по табельным номерам.
    Checks whether the brigade composition changed by personnel numbers.
    """

    previous_numbers = sorted(
        participant.employee_personnel_number.strip()
        for participant in previous_participants
    )
    updated_numbers = sorted(
        participant.employee_personnel_number.strip()
        for participant in updated_participants
    )
    return previous_numbers != updated_numbers
