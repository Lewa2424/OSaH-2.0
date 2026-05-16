from osah.domain.entities.work_permit_participant import WorkPermitParticipant


def validate_work_permit_participant_change(
    previous_participants: tuple[WorkPermitParticipant, ...],
    updated_participants: tuple[WorkPermitParticipant, ...],
) -> None:
    """Проверяет допустимость изменения состава бригады наряда-допуска.
    Validates whether a work-permit brigade change is allowed.
    """

    if not updated_participants:
        raise ValueError("У наряді-допуску має залишатися щонайменше один учасник.")

    updated_numbers = [
        participant.employee_personnel_number.strip()
        for participant in updated_participants
    ]
    if any(not personnel_number for personnel_number in updated_numbers):
        raise ValueError("Кожен учасник наряду-допуску повинен мати табельний номер.")
    if len(set(updated_numbers)) != len(updated_numbers):
        raise ValueError("Склад бригади не може містити дубльованих учасників.")

    previous_numbers = {
        participant.employee_personnel_number.strip()
        for participant in previous_participants
        if participant.employee_personnel_number.strip()
    }
    if not previous_numbers:
        return

    removed_count = len(previous_numbers - set(updated_numbers))
    if removed_count / len(previous_numbers) > 0.5:
        raise ValueError(
            "Змінено більше 50% складу бригади. Потрібно оформити новий наряд-допуск."
        )
