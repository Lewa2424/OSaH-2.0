import sqlite3
import tempfile
import unittest
from pathlib import Path

from osah.application.services.create_work_permit_record import create_work_permit_record
from osah.application.services.initialize_application import initialize_application
from osah.application.services.load_work_permit_registry import load_work_permit_registry
from osah.application.services.update_work_permit_record import update_work_permit_record
from osah.domain.entities.work_permit_participant import WorkPermitParticipant
from osah.domain.entities.work_permit_participant_role import WorkPermitParticipantRole
from osah.infrastructure.config.application_paths import build_application_paths
from osah.infrastructure.logging.shutdown_logging import shut_down_logging


class UpdateWorkPermitRecordTests(unittest.TestCase):
    """Тести оновлення наряду-допуску.
    Tests for updating a work permit.
    """

    def test_update_work_permit_record_updates_metadata_participant_role_and_audit_log(self) -> None:
        """Перевіряє оновлення реквізитів, ролі учасника та audit-події.
        Checks permit metadata update, participant role update, and audit event.
        """

        with tempfile.TemporaryDirectory() as temporary_directory:
            application_paths = build_application_paths(Path(temporary_directory))
            context = initialize_application(application_paths)
            create_work_permit_record(
                context.database_path,
                "ND-UT-201",
                "Висотні роботи",
                "Дільниця А",
                "2099-04-10 08:00",
                "2099-04-10 12:00",
                "Майстер",
                "Інспектор",
                "0001",
                "executor",
                "Початковий наряд",
            )
            created_record = next(record for record in load_work_permit_registry(context.database_path) if record.permit_number == "ND-UT-201")

            update_work_permit_record(
                context.database_path,
                int(created_record.record_id),
                "ND-UT-201A",
                "Висотні роботи",
                "Дільниця А",
                "2099-04-10 08:00",
                "2099-04-10 12:00",
                "Старший майстер",
                "Інженер з ОП",
                "0001",
                "team_member",
                "Оновлений наряд",
            )

            updated_record = next(record for record in load_work_permit_registry(context.database_path) if int(record.record_id) == int(created_record.record_id))
            connection = sqlite3.connect(context.database_path)
            audit_events = connection.execute("SELECT event_type FROM audit_log WHERE event_type = 'work_permit.updated';").fetchall()
            connection.close()

            self.assertEqual(updated_record.permit_number, "ND-UT-201A")
            self.assertEqual(updated_record.responsible_person, "Старший майстер")
            self.assertEqual(updated_record.issuer_person, "Інженер з ОП")
            self.assertEqual(updated_record.participants[0].employee_personnel_number, "0001")
            self.assertEqual(updated_record.participants[0].participant_role, WorkPermitParticipantRole.TEAM_MEMBER)
            self.assertEqual(len(audit_events), 1)
            shut_down_logging()

    def test_update_work_permit_record_rejects_term_longer_than_fifteen_days(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            application_paths = build_application_paths(Path(temporary_directory))
            context = initialize_application(application_paths)
            create_work_permit_record(
                context.database_path,
                "ND-UT-202",
                "Висотні роботи",
                "Дільниця А",
                "2099-04-10 08:00",
                "2099-04-10 12:00",
                "Майстер",
                "Інспектор",
                "0001",
                "executor",
                "Початковий наряд",
            )
            created_record = next(record for record in load_work_permit_registry(context.database_path) if record.permit_number == "ND-UT-202")

            with self.assertRaisesRegex(ValueError, "15 календарних днів"):
                update_work_permit_record(
                    context.database_path,
                    int(created_record.record_id),
                    "ND-UT-202",
                    "Висотні роботи",
                    "Дільниця А",
                    "2099-04-10 08:00",
                    "2099-04-26 12:00",
                    "Майстер",
                    "Інспектор",
                    "0001",
                    "executor",
                    "Надто довгий строк",
                )
            shut_down_logging()

    def test_update_work_permit_record_rejects_brigade_composition_change_through_general_edit(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            application_paths = build_application_paths(Path(temporary_directory))
            context = initialize_application(application_paths)
            create_work_permit_record(
                context.database_path,
                "ND-UT-203",
                "Вогневі роботи",
                "Дільниця А",
                "2099-04-10 08:00",
                "2099-04-10 12:00",
                "Майстер",
                "Інспектор",
                "0001",
                "executor",
                "Початковий наряд",
                participants=(
                    WorkPermitParticipant("0001", "Коваль Олена Вікторівна", WorkPermitParticipantRole.EXECUTOR),
                    WorkPermitParticipant("0002", "Іваненко Сергій Петрович", WorkPermitParticipantRole.TEAM_MEMBER),
                ),
            )
            created_record = next(record for record in load_work_permit_registry(context.database_path) if record.permit_number == "ND-UT-203")

            with self.assertRaisesRegex(ValueError, "окремою дією"):
                update_work_permit_record(
                    context.database_path,
                    int(created_record.record_id),
                    "ND-UT-203",
                    "Вогневі роботи",
                    "Дільниця А",
                    "2099-04-10 08:00",
                    "2099-04-10 12:00",
                    "Майстер",
                    "Інспектор",
                    "0001",
                    "executor",
                    "Спроба змінити склад",
                    participants=(
                        WorkPermitParticipant("0001", "Коваль Олена Вікторівна", WorkPermitParticipantRole.EXECUTOR),
                        WorkPermitParticipant("0003", "Петренко Андрій Миколайович", WorkPermitParticipantRole.TEAM_MEMBER),
                    ),
                )
            shut_down_logging()

    def test_update_work_permit_record_rejects_work_kind_or_location_change_through_general_edit(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            application_paths = build_application_paths(Path(temporary_directory))
            context = initialize_application(application_paths)
            create_work_permit_record(
                context.database_path,
                "ND-UT-204",
                "Вогневі роботи",
                "Дільниця А",
                "2099-04-10 08:00",
                "2099-04-10 12:00",
                "Майстер",
                "Інспектор",
                "0001",
                "executor",
                "Початковий наряд",
            )
            created_record = next(record for record in load_work_permit_registry(context.database_path) if record.permit_number == "ND-UT-204")

            with self.assertRaisesRegex(ValueError, "перевипуск"):
                update_work_permit_record(
                    context.database_path,
                    int(created_record.record_id),
                    "ND-UT-204",
                    "Газонебезпечні роботи",
                    "Дільниця Б",
                    "2099-04-10 08:00",
                    "2099-04-10 12:00",
                    "Майстер",
                    "Інспектор",
                    "0001",
                    "executor",
                    "Спроба змінити умови робіт",
                )
            shut_down_logging()


if __name__ == "__main__":
    unittest.main()
