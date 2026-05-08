import sqlite3
import tempfile
import unittest
from pathlib import Path

from osah.application.services.create_work_permit_record import create_work_permit_record
from osah.application.services.initialize_application import initialize_application
from osah.application.services.load_training_registry import load_training_registry
from osah.application.services.load_work_permit_registry import load_work_permit_registry
from osah.application.services.update_work_permit_record import update_work_permit_record
from osah.domain.entities.work_permit_participant import WorkPermitParticipant
from osah.domain.entities.work_permit_participant_role import WorkPermitParticipantRole
from osah.infrastructure.config.application_paths import build_application_paths
from osah.infrastructure.database.create_database_connection import create_database_connection
from osah.infrastructure.logging.shutdown_logging import shut_down_logging


class WorkPermitTargetTrainingTests(unittest.TestCase):
    """Тести цільового інструктажу в нарядах-допусках.
    Tests for targeted training synchronization from work permits.
    """

    def test_done_passed_creates_targeted_training_record_and_audit(self) -> None:
        """Створює цільовий інструктаж і audit для статусу done_passed.
        Creates a targeted training and audit entry for done_passed status.
        """

        with tempfile.TemporaryDirectory() as temporary_directory:
            context = initialize_application(build_application_paths(Path(temporary_directory)))
            try:
                permit_number = "AUTO-WP-PASSED-001"
                create_work_permit_record(
                    context.database_path,
                    permit_number,
                    "Вогневі роботи",
                    "Дільниця А",
                    "10.05.2026 08:00",
                    "10.05.2026 12:00",
                    "Майстер",
                    "Інженер з ОП",
                    "0001",
                    "executor",
                    "Плановий наряд",
                    target_training_status="done_passed",
                    target_training_date_text="09.05.2026",
                    target_training_conducted_by="Коваль О.В.",
                    target_training_note="Інструктаж проведено перед початком робіт.",
                )

                permit_record = next(record for record in load_work_permit_registry(context.database_path) if record.permit_number == permit_number)
                training_record = next(
                    record
                    for record in load_training_registry(context.database_path)
                    if record.source_key == f"work_permit_target_training:{permit_record.record_id}:0001"
                )
                self.assertEqual(training_record.training_type.value, "targeted")
                self.assertEqual(training_record.knowledge_check_result.value, "satisfactory")
                self.assertEqual(training_record.work_admission_status.value, "allowed")
                self.assertEqual(training_record.source_module, "work_permits")
                self.assertEqual(training_record.source_record_id, permit_record.record_id)

                connection = sqlite3.connect(context.database_path)
                audit_row = connection.execute(
                    """
                    SELECT description_text
                    FROM audit_log
                    WHERE event_type = 'training.created_from_work_permit'
                    ORDER BY id DESC
                    LIMIT 1
                    """
                ).fetchone()
                connection.close()

                self.assertIsNotNone(audit_row)
                self.assertIn(permit_number, audit_row[0])
                self.assertIn("0001", audit_row[0])
                self.assertIn("satisfactory", audit_row[0])
            finally:
                shut_down_logging()

    def test_done_failed_creates_not_allowed_training_and_notifications(self) -> None:
        """Створює недопуск і critical-сповіщення для done_failed.
        Creates no-admission training and critical notifications for done_failed.
        """

        with tempfile.TemporaryDirectory() as temporary_directory:
            context = initialize_application(build_application_paths(Path(temporary_directory)))
            try:
                permit_number = "AUTO-WP-FAILED-001"
                create_work_permit_record(
                    context.database_path,
                    permit_number,
                    "Газонебезпечні роботи",
                    "Дільниця Б",
                    "10.05.2026 08:00",
                    "10.05.2026 12:00",
                    "Майстер",
                    "Інженер з ОП",
                    "0001",
                    "executor",
                    "Роботи під контролем",
                    target_training_status="done_failed",
                    target_training_date_text="09.05.2026",
                    target_training_conducted_by="Коваль О.В.",
                )

                permit_record = next(record for record in load_work_permit_registry(context.database_path) if record.permit_number == permit_number)
                training_record = next(
                    record
                    for record in load_training_registry(context.database_path)
                    if record.source_key == f"work_permit_target_training:{permit_record.record_id}:0001"
                )
                self.assertEqual(training_record.knowledge_check_result.value, "unsatisfactory")
                self.assertEqual(training_record.work_admission_status.value, "not_allowed")

                connection = sqlite3.connect(context.database_path)
                training_notification = connection.execute(
                    """
                    SELECT notification_level
                    FROM notifications
                    WHERE source_module = 'trainings.registry'
                      AND employee_personnel_number = '0001'
                      AND message_text LIKE '%Допуск до робіт заборонено%'
                    ORDER BY id DESC
                    LIMIT 1
                    """
                ).fetchone()
                permit_notification = connection.execute(
                    """
                    SELECT notification_level
                    FROM notifications
                    WHERE source_module = 'work_permits.registry'
                      AND employee_personnel_number = '0001'
                      AND message_text LIKE ?
                    ORDER BY id DESC
                    LIMIT 1
                    """,
                    (f"%{permit_number}%",),
                ).fetchone()
                connection.close()

                self.assertIsNotNone(training_notification)
                self.assertEqual(training_notification[0], "critical")
                self.assertIsNotNone(permit_notification)
                self.assertEqual(permit_notification[0], "critical")
            finally:
                shut_down_logging()

    def test_repeated_save_updates_without_duplicates(self) -> None:
        """Повторне збереження НД оновлює запис без дублювання інструктажу.
        Re-saving a permit updates the linked training without duplicating it.
        """

        with tempfile.TemporaryDirectory() as temporary_directory:
            context = initialize_application(build_application_paths(Path(temporary_directory)))
            try:
                permit_number = "AUTO-WP-DUP-001"
                create_work_permit_record(
                    context.database_path,
                    permit_number,
                    "Висотні роботи",
                    "Дільниця В",
                    "10.05.2026 08:00",
                    "10.05.2026 12:00",
                    "Майстер",
                    "Інженер з ОП",
                    "0001",
                    "executor",
                    "Перше збереження",
                    target_training_status="done_passed",
                    target_training_date_text="09.05.2026",
                    target_training_conducted_by="Коваль О.В.",
                )
                permit_record = next(record for record in load_work_permit_registry(context.database_path) if record.permit_number == permit_number)

                update_work_permit_record(
                    context.database_path,
                    int(permit_record.record_id),
                    permit_record.permit_number,
                    permit_record.work_kind,
                    permit_record.work_location,
                    "10.05.2026 08:00",
                    "10.05.2026 12:00",
                    permit_record.responsible_person,
                    permit_record.issuer_person,
                    "0001",
                    "executor",
                    "Друге збереження",
                    target_training_status="done_passed",
                    target_training_date_text="09.05.2026",
                    target_training_conducted_by="Петренко І.В.",
                    target_training_note="Оновлено під час повторного збереження.",
                )

                connection = sqlite3.connect(context.database_path)
                count_row = connection.execute(
                    f"""
                    SELECT COUNT(*)
                    FROM trainings
                    WHERE source_key = 'work_permit_target_training:{permit_record.record_id}:0001'
                    """
                ).fetchone()
                updated_row = connection.execute(
                    f"""
                    SELECT conducted_by, basis_note
                    FROM trainings
                    WHERE source_key = 'work_permit_target_training:{permit_record.record_id}:0001'
                    LIMIT 1
                    """
                ).fetchone()
                connection.close()

                self.assertEqual(count_row[0], 1)
                self.assertEqual(updated_row[0], "Петренко І.В.")
                self.assertIn("Оновлено", updated_row[1])
            finally:
                shut_down_logging()

    def test_multi_participant_permit_creates_targeted_training_for_each_participant(self) -> None:
        """Один НД створює окремий цільовий інструктаж для кожного учасника.
        One permit creates a separate targeted training for each participant.
        """

        with tempfile.TemporaryDirectory() as temporary_directory:
            context = initialize_application(build_application_paths(Path(temporary_directory)))
            try:
                create_work_permit_record(
                    context.database_path,
                    "AUTO-WP-MULTI-001",
                    "Висотні роботи",
                    "Дільниця Ж",
                    "10.05.2026 08:00",
                    "10.05.2026 12:00",
                    "Майстер",
                    "Інженер з ОП",
                    "0001",
                    "executor",
                    "Бригадний наряд",
                    target_training_status="done_passed",
                    target_training_date_text="09.05.2026",
                    target_training_conducted_by="Коваль О.В.",
                    participants=(
                        WorkPermitParticipant("0001", "Коваль Олена Вікторівна", WorkPermitParticipantRole.EXECUTOR),
                        WorkPermitParticipant("0002", "Іваненко Ігор Олександрович", WorkPermitParticipantRole.TEAM_MEMBER),
                    ),
                )

                permit_record = next(record for record in load_work_permit_registry(context.database_path) if record.permit_number == "AUTO-WP-MULTI-001")
                created_records = [
                    record
                    for record in load_training_registry(context.database_path)
                    if record.source_module == "work_permits"
                    and record.source_record_id == permit_record.record_id
                ]

                self.assertEqual(len(created_records), 2)
                self.assertEqual(
                    {record.employee_personnel_number for record in created_records},
                    {"0001", "0002"},
                )
            finally:
                shut_down_logging()

    def test_not_done_does_not_create_training_record(self) -> None:
        """Статус not_done не створює training-запис, але створює попередження по НД.
        Status not_done does not create a training record but creates a permit warning.
        """

        with tempfile.TemporaryDirectory() as temporary_directory:
            context = initialize_application(build_application_paths(Path(temporary_directory)))
            try:
                permit_number = "AUTO-WP-NOT-DONE-001"
                create_work_permit_record(
                    context.database_path,
                    permit_number,
                    "Електророботи",
                    "Дільниця Г",
                    "10.05.2099 08:00",
                    "10.05.2099 12:00",
                    "Майстер",
                    "Інженер з ОП",
                    "0001",
                    "executor",
                    "Інструктаж ще не проведено",
                    target_training_status="not_done",
                )

                trainings = load_training_registry(context.database_path)
                self.assertFalse(any(record.source_module == "work_permits" for record in trainings))

                connection = sqlite3.connect(context.database_path)
                notification_row = connection.execute(
                    """
                    SELECT notification_level
                    FROM notifications
                    WHERE source_module = 'work_permits.registry'
                      AND message_text LIKE ?
                    ORDER BY id DESC
                    LIMIT 1
                    """,
                    (f"%{permit_number}%",),
                ).fetchone()
                connection.close()

                self.assertIsNotNone(notification_row)
                self.assertEqual(notification_row[0], "warning")
            finally:
                shut_down_logging()

    def test_downgrade_to_not_done_archives_linked_training_records(self) -> None:
        """Перехід з done_passed на not_done видаляє автостворені training-записи з audit.
        Downgrading from done_passed to not_done removes linked auto-created trainings with audit.
        """

        with tempfile.TemporaryDirectory() as temporary_directory:
            context = initialize_application(build_application_paths(Path(temporary_directory)))
            try:
                permit_number = "AUTO-WP-DOWNGRADE-001"
                create_work_permit_record(
                    context.database_path,
                    permit_number,
                    "Висотні роботи",
                    "Дільниця И",
                    "10.05.2026 08:00",
                    "10.05.2026 12:00",
                    "Майстер",
                    "Інженер з ОП",
                    "0001",
                    "executor",
                    "Початково інструктаж проведено",
                    target_training_status="done_passed",
                    target_training_date_text="09.05.2026",
                    target_training_conducted_by="Коваль О.В.",
                )

                permit_record = next(record for record in load_work_permit_registry(context.database_path) if record.permit_number == permit_number)
                created_records = [
                    record
                    for record in load_training_registry(context.database_path)
                    if record.source_module == "work_permits"
                    and record.source_record_id == permit_record.record_id
                ]
                self.assertEqual(len(created_records), 1)

                update_work_permit_record(
                    context.database_path,
                    int(permit_record.record_id),
                    permit_record.permit_number,
                    permit_record.work_kind,
                    permit_record.work_location,
                    "10.05.2026 08:00",
                    "10.05.2026 12:00",
                    permit_record.responsible_person,
                    permit_record.issuer_person,
                    "0001",
                    "executor",
                    "Інструктаж скасовано",
                    target_training_status="not_done",
                    target_training_date_text="",
                    target_training_conducted_by="",
                    target_training_note="",
                )

                remaining_records = [
                    record
                    for record in load_training_registry(context.database_path)
                    if record.source_module == "work_permits"
                    and record.source_record_id == permit_record.record_id
                ]
                self.assertEqual(len(remaining_records), 0)

                archived_records = [
                    record
                    for record in load_training_registry(context.database_path, include_archived=True)
                    if record.source_module == "work_permits"
                    and record.source_record_id == permit_record.record_id
                ]
                self.assertEqual(len(archived_records), 1)
                self.assertFalse(archived_records[0].is_current)

                connection = sqlite3.connect(context.database_path)
                audit_row = connection.execute(
                    """
                    SELECT description_text
                    FROM audit_log
                    WHERE event_type = 'training.archived'
                    ORDER BY id DESC
                    LIMIT 1
                    """
                ).fetchone()
                connection.close()

                self.assertIsNotNone(audit_row)
                self.assertIn(permit_number, audit_row[0])
                self.assertIn("not_done", audit_row[0])
            finally:
                shut_down_logging()

    def test_legacy_status_does_not_create_noise(self) -> None:
        """Legacy-статус не створює ані training-записів, ані шумових сповіщень.
        Legacy status creates neither training records nor noisy notifications.
        """

        with tempfile.TemporaryDirectory() as temporary_directory:
            context = initialize_application(build_application_paths(Path(temporary_directory)))
            try:
                permit_number = "AUTO-WP-LEGACY-001"
                create_work_permit_record(
                    context.database_path,
                    permit_number,
                    "Ремонтні роботи",
                    "Дільниця Д",
                    "10.05.2099 08:00",
                    "10.05.2099 12:00",
                    "Майстер",
                    "Інженер з ОП",
                    "0001",
                    "executor",
                    "Старий сценарій без фіксації інструктажу",
                    target_training_status="legacy_not_tracked",
                )

                trainings = load_training_registry(context.database_path)
                self.assertFalse(any(record.source_module == "work_permits" for record in trainings))

                connection = sqlite3.connect(context.database_path)
                notification_count = connection.execute(
                    """
                    SELECT COUNT(*)
                    FROM notifications
                    WHERE source_module = 'work_permits.registry'
                      AND message_text LIKE ?
                      AND title_text LIKE '%цільовий інструктаж%'
                    """,
                    (f"%{permit_number}%",),
                ).fetchone()
                connection.close()

                self.assertEqual(notification_count[0], 0)
            finally:
                shut_down_logging()

    def test_done_status_requires_date_and_conductor(self) -> None:
        """Проведений цільовий інструктаж вимагає дату та проводившого.
        Conducted targeted training requires date and conductor.
        """

        with tempfile.TemporaryDirectory() as temporary_directory:
            context = initialize_application(build_application_paths(Path(temporary_directory)))
            try:
                with self.assertRaisesRegex(
                    ValueError,
                    "Для проведеного цільового інструктажу потрібно вказати дату та особу, яка його провела.",
                ):
                    create_work_permit_record(
                        context.database_path,
                        "AUTO-WP-VALIDATE-001",
                        "Вогневі роботи",
                        "Дільниця Е",
                        "10.05.2026 08:00",
                        "10.05.2026 12:00",
                        "Майстер",
                        "Інженер з ОП",
                        "0001",
                        "executor",
                        "Без дати",
                        target_training_status="done_passed",
                        target_training_conducted_by="Коваль О.В.",
                    )

                with self.assertRaisesRegex(
                    ValueError,
                    "Для проведеного цільового інструктажу потрібно вказати дату та особу, яка його провела.",
                ):
                    create_work_permit_record(
                        context.database_path,
                        "AUTO-WP-VALIDATE-002",
                        "Вогневі роботи",
                        "Дільниця Е",
                        "10.05.2026 08:00",
                        "10.05.2026 12:00",
                        "Майстер",
                        "Інженер з ОП",
                        "0001",
                        "executor",
                        "Без проводившого",
                        target_training_status="done_failed",
                        target_training_date_text="09.05.2026",
                    )
            finally:
                shut_down_logging()

    def test_training_source_columns_are_created(self) -> None:
        """Нова схема trainings має source-поля для зв'язку з НД.
        The trainings schema contains source columns for work-permit linkage.
        """

        with tempfile.TemporaryDirectory() as temporary_directory:
            context = initialize_application(build_application_paths(Path(temporary_directory)))
            try:
                connection = create_database_connection(context.database_path)
                try:
                    columns = {row["name"] for row in connection.execute("PRAGMA table_info(trainings);").fetchall()}
                finally:
                    connection.close()

                self.assertIn("source_module", columns)
                self.assertIn("source_record_id", columns)
                self.assertIn("source_key", columns)
            finally:
                shut_down_logging()


if __name__ == "__main__":
    unittest.main()
