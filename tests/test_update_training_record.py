import sqlite3
import tempfile
import unittest
from pathlib import Path

from osah.application.services.create_training_record import create_training_record
from osah.application.services.create_work_permit_record import create_work_permit_record
from osah.application.services.initialize_application import initialize_application
from osah.application.services.load_training_registry import load_training_registry
from osah.application.services.update_training_record import update_training_record
from osah.infrastructure.config.application_paths import build_application_paths
from osah.infrastructure.logging.shutdown_logging import shut_down_logging


class UpdateTrainingRecordTests(unittest.TestCase):
    """Тести оновлення запису інструктажу.
    Tests for updating a training record.
    """

    def test_update_training_record_updates_record_and_writes_audit_log(self) -> None:
        """Оновлює запис інструктажу і пише audit-подію.
        Updates a training record and writes an audit event.
        """

        with tempfile.TemporaryDirectory() as temporary_directory:
            application_paths = build_application_paths(Path(temporary_directory))
            context = initialize_application(application_paths)
            try:
                create_training_record(
                    database_path=context.database_path,
                    employee_personnel_number="0001",
                    training_type="introductory",
                    event_date_text="2026-04-09",
                    next_control_date_text="",
                    conducted_by="Інспектор з ОП",
                    note_text="Вступний запис",
                )
                create_training_record(
                    database_path=context.database_path,
                    employee_personnel_number="0001",
                    training_type="primary",
                    event_date_text="2026-04-10",
                    next_control_date_text="",
                    work_risk_category="regular",
                    conducted_by="Інспектор з ОП",
                    note_text="Початковий запис",
                )
                create_training_record(
                    database_path=context.database_path,
                    employee_personnel_number="0001",
                    training_type="repeated",
                    event_date_text="2026-04-11",
                    next_control_date_text="",
                    work_risk_category="regular",
                    conducted_by="Інспектор з ОП",
                    note_text="Початковий повторний",
                )

                created_record = next(
                    training_record
                    for training_record in load_training_registry(context.database_path)
                    if training_record.employee_personnel_number == "0001"
                    and training_record.note_text == "Початковий повторний"
                )
                update_training_record(
                    database_path=context.database_path,
                    record_id=int(created_record.record_id),
                    employee_personnel_number="0001",
                    training_type="repeated",
                    event_date_text="2026-04-12",
                    next_control_date_text="",
                    work_risk_category="high_risk",
                    conducted_by="Головний інспектор",
                    note_text="Оновлений запис",
                )

                updated_record = next(
                    training_record
                    for training_record in load_training_registry(context.database_path)
                    if int(training_record.record_id) == int(created_record.record_id)
                )
                connection = sqlite3.connect(context.database_path)
                audit_events = connection.execute(
                    "SELECT event_type FROM audit_log WHERE event_type = 'training.updated';"
                ).fetchall()
                connection.close()

                self.assertEqual(updated_record.conducted_by, "Головний інспектор")
                self.assertEqual(updated_record.note_text, "Оновлений запис")
                self.assertEqual(updated_record.next_control_date, "2026-07-12")
                self.assertEqual(len(audit_events), 1)
            finally:
                shut_down_logging()

    def test_update_training_record_preserves_work_permit_source_link(self) -> None:
        """Зберігає source-зв'язок з НД при ручному редагуванні авто-інструктажу.
        Preserves work-permit source link when manually editing an auto-created training.
        """

        with tempfile.TemporaryDirectory() as temporary_directory:
            application_paths = build_application_paths(Path(temporary_directory))
            context = initialize_application(application_paths)
            try:
                create_work_permit_record(
                    database_path=context.database_path,
                    permit_number="AUTO-WP-LINK-001",
                    work_kind="Вогневі роботи",
                    work_location="Дільниця З",
                    starts_at_text="10.05.2026 08:00",
                    ends_at_text="10.05.2026 12:00",
                    responsible_person="Майстер",
                    issuer_person="Інженер з ОП",
                    employee_personnel_number="0001",
                    participant_role="executor",
                    note_text="Автостворений цільовий інструктаж",
                    target_training_status="done_passed",
                    target_training_date_text="09.05.2026",
                    target_training_conducted_by="Коваль О.В.",
                )

                created_record = next(
                    training_record
                    for training_record in load_training_registry(context.database_path)
                    if training_record.source_module == "work_permits"
                    and training_record.source_key.startswith("work_permit_target_training:")
                )
                previous_source_module = created_record.source_module
                previous_source_record_id = created_record.source_record_id
                previous_source_key = created_record.source_key

                update_training_record(
                    database_path=context.database_path,
                    record_id=int(created_record.record_id),
                    employee_personnel_number=created_record.employee_personnel_number,
                    training_type=created_record.training_type.value,
                    event_date_text="09.05.2026",
                    next_control_date_text="",
                    work_risk_category=created_record.work_risk_category.value,
                    conducted_by="Петренко І.В.",
                    note_text="Ручне уточнення запису",
                    person_category=created_record.person_category.value,
                    requires_primary_on_workplace=created_record.requires_primary_on_workplace,
                    knowledge_check_result=created_record.knowledge_check_result.value,
                    work_admission_status=created_record.work_admission_status.value,
                    knowledge_check_note=created_record.knowledge_check_note,
                    basis_text=created_record.basis_text,
                    basis_note=created_record.basis_note,
                )

                updated_record = next(
                    training_record
                    for training_record in load_training_registry(context.database_path)
                    if int(training_record.record_id) == int(created_record.record_id)
                )

                self.assertEqual(updated_record.source_module, previous_source_module)
                self.assertEqual(updated_record.source_record_id, previous_source_record_id)
                self.assertEqual(updated_record.source_key, previous_source_key)
                self.assertEqual(updated_record.conducted_by, "Петренко І.В.")
            finally:
                shut_down_logging()

    def test_update_training_record_rejects_invalid_chronology(self) -> None:
        """Не дозволяє оновити запис до хронологічно неможливого повторного інструктажу.
        Rejects updating a record to an impossible repeated-training chronology.
        """

        with tempfile.TemporaryDirectory() as temporary_directory:
            application_paths = build_application_paths(Path(temporary_directory))
            context = initialize_application(application_paths)
            try:
                create_training_record(
                    database_path=context.database_path,
                    employee_personnel_number="0001",
                    training_type="introductory",
                    event_date_text="2026-04-10",
                    next_control_date_text="",
                    conducted_by="Інспектор з ОП",
                    note_text="Вступний запис",
                )
                created_record = next(
                    training_record
                    for training_record in load_training_registry(context.database_path)
                    if training_record.employee_personnel_number == "0001"
                    and training_record.training_type.value == "introductory"
                )

                with self.assertRaisesRegex(ValueError, "послідовність інструктажів"):
                    update_training_record(
                        database_path=context.database_path,
                        record_id=int(created_record.record_id),
                        employee_personnel_number="0001",
                        training_type="repeated",
                        event_date_text="2026-04-09",
                        next_control_date_text="",
                        work_risk_category="regular",
                        conducted_by="Головний інспектор",
                        note_text="Конфліктний запис",
                    )
            finally:
                shut_down_logging()


if __name__ == "__main__":
    unittest.main()
