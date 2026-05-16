import tempfile
import unittest
from pathlib import Path

from osah.application.services.apply_work_permit_participant_change import apply_work_permit_participant_change
from osah.application.services.create_work_permit_record import create_work_permit_record
from osah.application.services.initialize_application import initialize_application
from osah.application.services.load_work_permit_registry import load_work_permit_registry
from osah.domain.entities.work_permit_participant import WorkPermitParticipant
from osah.domain.entities.work_permit_participant_role import WorkPermitParticipantRole
from osah.domain.entities.work_permit_status import WorkPermitStatus
from osah.infrastructure.config.application_paths import build_application_paths
from osah.infrastructure.logging.shutdown_logging import shut_down_logging


class ApplyWorkPermitParticipantChangeTests(unittest.TestCase):
    """Тести оркестрації зміни складу бригади наряду-допуску.
    Tests for orchestrating work-permit brigade-composition changes.
    """

    def test_apply_work_permit_participant_change_reissues_permit_when_more_than_half_is_replaced(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            application_paths = build_application_paths(Path(temporary_directory))
            context = initialize_application(application_paths)
            create_work_permit_record(
                context.database_path,
                "ND-APPLY-001",
                "Вогневі роботи",
                "Дільниця А",
                "2099-04-10 08:00",
                "2099-04-20 18:00",
                "Майстер",
                "",
                "",
                "",
                "Початковий склад бригади",
                participants=(
                    WorkPermitParticipant("0001", "Коваль Олена", WorkPermitParticipantRole.EXECUTOR),
                    WorkPermitParticipant("0002", "Іваненко Сергій", WorkPermitParticipantRole.TEAM_MEMBER),
                    WorkPermitParticipant("0003", "Петренко Андрій", WorkPermitParticipantRole.TEAM_MEMBER),
                ),
            )
            source_record = next(
                record for record in load_work_permit_registry(context.database_path) if record.permit_number == "ND-APPLY-001"
            )

            outcome = apply_work_permit_participant_change(
                context.database_path,
                int(source_record.record_id),
                (
                    WorkPermitParticipant("0001", "Коваль Олена", WorkPermitParticipantRole.EXECUTOR),
                    WorkPermitParticipant("0004", "Шевченко Михайло", WorkPermitParticipantRole.TEAM_MEMBER),
                    WorkPermitParticipant("0005", "Бондар Тетяна", WorkPermitParticipantRole.OBSERVER),
                ),
            )

            records = load_work_permit_registry(context.database_path)
            original_record = next(record for record in records if int(record.record_id) == int(source_record.record_id))
            new_record = next(record for record in records if int(record.record_id) == int(outcome.applied_record_id))

            self.assertTrue(outcome.reissued)
            self.assertNotEqual(outcome.applied_record_id, int(source_record.record_id))
            self.assertEqual(original_record.status, WorkPermitStatus.CANCELED)
            self.assertEqual(
                tuple(participant.employee_personnel_number for participant in new_record.participants),
                ("0001", "0004", "0005"),
            )
            shut_down_logging()

    def test_apply_work_permit_participant_change_rejects_auto_reissue_for_expired_permit(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            application_paths = build_application_paths(Path(temporary_directory))
            context = initialize_application(application_paths)
            create_work_permit_record(
                context.database_path,
                "ND-APPLY-002",
                "Вогневі роботи",
                "Дільниця Б",
                "2000-04-10 08:00",
                "2000-04-20 18:00",
                "Майстер",
                "",
                "",
                "",
                "Прострочений наряд",
                participants=(
                    WorkPermitParticipant("0001", "Коваль Олена", WorkPermitParticipantRole.EXECUTOR),
                    WorkPermitParticipant("0002", "Іваненко Сергій", WorkPermitParticipantRole.TEAM_MEMBER),
                    WorkPermitParticipant("0003", "Петренко Андрій", WorkPermitParticipantRole.TEAM_MEMBER),
                ),
            )
            source_record = next(
                record for record in load_work_permit_registry(context.database_path) if record.permit_number == "ND-APPLY-002"
            )

            with self.assertRaisesRegex(ValueError, "Строк дії наряду вже сплив"):
                apply_work_permit_participant_change(
                    context.database_path,
                    int(source_record.record_id),
                    (
                        WorkPermitParticipant("0001", "Коваль Олена", WorkPermitParticipantRole.EXECUTOR),
                        WorkPermitParticipant("0004", "Шевченко Михайло", WorkPermitParticipantRole.TEAM_MEMBER),
                        WorkPermitParticipant("0005", "Бондар Тетяна", WorkPermitParticipantRole.OBSERVER),
                    ),
                )
            shut_down_logging()


if __name__ == "__main__":
    unittest.main()
