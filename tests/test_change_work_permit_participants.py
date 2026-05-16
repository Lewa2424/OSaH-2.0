import sqlite3
import tempfile
import unittest
from pathlib import Path

from osah.application.services.change_work_permit_participants import change_work_permit_participants
from osah.application.services.create_work_permit_record import create_work_permit_record
from osah.application.services.initialize_application import initialize_application
from osah.application.services.load_work_permit_registry import load_work_permit_registry
from osah.domain.entities.work_permit_participant import WorkPermitParticipant
from osah.domain.entities.work_permit_participant_role import WorkPermitParticipantRole
from osah.infrastructure.config.application_paths import build_application_paths
from osah.infrastructure.logging.shutdown_logging import shut_down_logging


class ChangeWorkPermitParticipantsTests(unittest.TestCase):
    """Тести контролю зміни складу бригади наряду-допуску.
    Tests for controlled work-permit brigade changes.
    """

    def test_change_work_permit_participants_allows_replacing_no_more_than_half(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            application_paths = build_application_paths(Path(temporary_directory))
            context = initialize_application(application_paths)
            create_work_permit_record(
                context.database_path,
                "ND-TEAM-001",
                "Вогневі роботи",
                "Дільниця А",
                "2099-04-10 08:00",
                "2099-04-20 18:00",
                "Майстер",
                "Інспектор",
                "0001",
                "executor",
                "Початковий склад бригади",
                participants=(
                    WorkPermitParticipant("0001", "Коваль Олена Вікторівна", WorkPermitParticipantRole.EXECUTOR),
                    WorkPermitParticipant("0002", "Іваненко Сергій Петрович", WorkPermitParticipantRole.TEAM_MEMBER),
                    WorkPermitParticipant("0003", "Петренко Андрій Миколайович", WorkPermitParticipantRole.TEAM_MEMBER),
                    WorkPermitParticipant("0004", "Шевченко Михайло Олексійович", WorkPermitParticipantRole.TEAM_MEMBER),
                ),
            )
            created_record = next(
                record for record in load_work_permit_registry(context.database_path) if record.permit_number == "ND-TEAM-001"
            )

            change_work_permit_participants(
                context.database_path,
                int(created_record.record_id),
                (
                    WorkPermitParticipant("0001", "Коваль Олена Вікторівна", WorkPermitParticipantRole.EXECUTOR),
                    WorkPermitParticipant("0002", "Іваненко Сергій Петрович", WorkPermitParticipantRole.TEAM_MEMBER),
                    WorkPermitParticipant("0005", "Бондар Тетяна Юріївна", WorkPermitParticipantRole.TEAM_MEMBER),
                    WorkPermitParticipant("0006", "Кравченко Олег Васильович", WorkPermitParticipantRole.OBSERVER),
                ),
            )

            updated_record = next(
                record for record in load_work_permit_registry(context.database_path) if int(record.record_id) == int(created_record.record_id)
            )
            connection = sqlite3.connect(context.database_path)
            audit_events = connection.execute(
                "SELECT event_type FROM audit_log WHERE event_type = 'work_permit.participants_changed';"
            ).fetchall()
            connection.close()

            self.assertEqual(
                tuple(participant.employee_personnel_number for participant in updated_record.participants),
                ("0001", "0002", "0005", "0006"),
            )
            self.assertEqual(len(audit_events), 1)
            shut_down_logging()

    def test_change_work_permit_participants_rejects_replacing_more_than_half(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            application_paths = build_application_paths(Path(temporary_directory))
            context = initialize_application(application_paths)
            create_work_permit_record(
                context.database_path,
                "ND-TEAM-002",
                "Вогневі роботи",
                "Дільниця Б",
                "2099-04-10 08:00",
                "2099-04-20 18:00",
                "Майстер",
                "Інспектор",
                "0001",
                "executor",
                "Початковий склад бригади",
                participants=(
                    WorkPermitParticipant("0001", "Коваль Олена Вікторівна", WorkPermitParticipantRole.EXECUTOR),
                    WorkPermitParticipant("0002", "Іваненко Сергій Петрович", WorkPermitParticipantRole.TEAM_MEMBER),
                    WorkPermitParticipant("0003", "Петренко Андрій Миколайович", WorkPermitParticipantRole.TEAM_MEMBER),
                ),
            )
            created_record = next(
                record for record in load_work_permit_registry(context.database_path) if record.permit_number == "ND-TEAM-002"
            )

            with self.assertRaisesRegex(ValueError, "50% складу бригади"):
                change_work_permit_participants(
                    context.database_path,
                    int(created_record.record_id),
                    (
                        WorkPermitParticipant("0001", "Коваль Олена Вікторівна", WorkPermitParticipantRole.EXECUTOR),
                        WorkPermitParticipant("0004", "Шевченко Михайло Олексійович", WorkPermitParticipantRole.TEAM_MEMBER),
                        WorkPermitParticipant("0005", "Бондар Тетяна Юріївна", WorkPermitParticipantRole.OBSERVER),
                    ),
                )
            shut_down_logging()


if __name__ == "__main__":
    unittest.main()
