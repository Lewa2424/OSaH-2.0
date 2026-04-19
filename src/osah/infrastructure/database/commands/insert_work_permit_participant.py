from sqlite3 import Connection

from osah.domain.entities.work_permit_participant import WorkPermitParticipant


# ###### ДОДАВАННЯ УЧАСНИКА НАРЯДУ / ДОБАВЛЕНИЕ УЧАСТНИКА НАРЯДА ######
def insert_work_permit_participant(
    connection: Connection,
    work_permit_id: int,
    work_permit_participant: WorkPermitParticipant,
) -> None:
    """Зберігає учасника наряду-допуску в локальній базі.
    Сохраняет участника наряда-допуска в локальной базе.
    """

    connection.execute(
        """
        INSERT INTO work_permit_participants (
            work_permit_id,
            employee_personnel_number,
            participant_role
        )
        VALUES (?, ?, ?);
        """,
        (
            work_permit_id,
            work_permit_participant.employee_personnel_number,
            work_permit_participant.participant_role.value,
        ),
    )
