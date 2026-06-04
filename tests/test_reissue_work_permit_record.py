import sqlite3
import tempfile
import unittest
from pathlib import Path
from osah.application.services.create_work_permit_record import create_work_permit_record
from osah.application.services.initialize_application import initialize_application
from osah.application.services.load_work_permit_registry import load_work_permit_registry
from osah.application.services.reissue_work_permit_record import reissue_work_permit_record
from osah.domain.entities.work_permit_participant import WorkPermitParticipant
from osah.domain.entities.work_permit_participant_role import WorkPermitParticipantRole
from osah.domain.entities.work_permit_record import WorkPermitRecord
from osah.domain.entities.work_permit_status import WorkPermitStatus
from osah.infrastructure.config.application_paths import build_application_paths
from osah.infrastructure.logging.shutdown_logging import shut_down_logging
from osah.domain.entities.access_role import AccessRole

class ReissueWorkPermitRecordTests(unittest.TestCase):
    """Тести перевипуску наряду-допуску.
    Tests for reissuing a work permit.
    """

    def test_reissue_work_permit_record_creates_new_record_and_marks_source_as_reissued(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            application_paths = build_application_paths(Path(temporary_directory))
            context = initialize_application(application_paths)
            create_work_permit_record(context.database_path, 'ND-RS-001', 'Вогневі роботи', 'Дільниця А', '2099-04-10 08:00', '2099-04-10 12:00', 'Майстер', 'Інспектор', '0001', 'executor', 'Початковий наряд', access_role=AccessRole.INSPECTOR)
            source_record = next((record for record in load_work_permit_registry(context.database_path) if record.permit_number == 'ND-RS-001'))
            reissued_record = WorkPermitRecord(record_id=None, permit_number='ND-RS-002', work_kind='Газонебезпечні роботи', work_location='Дільниця Б', starts_at=source_record.starts_at, ends_at=source_record.ends_at, responsible_person=source_record.responsible_person, issuer_person=source_record.issuer_person, note_text='Перевипущений наряд', closed_at=None, participants=source_record.participants, status=WorkPermitStatus.ACTIVE, target_training_status=source_record.target_training_status, target_training_date=source_record.target_training_date, target_training_conducted_by=source_record.target_training_conducted_by, target_training_note=source_record.target_training_note, basis_text=source_record.basis_text, basis_note=source_record.basis_note, base_ends_at=source_record.base_ends_at)
            reissue_work_permit_record(context.database_path, int(source_record.record_id), reissued_record, 'Змінено умови виконання робіт', access_role=AccessRole.INSPECTOR)
            records = load_work_permit_registry(context.database_path)
            original_record = next((record for record in records if int(record.record_id) == int(source_record.record_id)))
            new_record = next((record for record in records if record.permit_number == 'ND-RS-002'))
            connection = sqlite3.connect(context.database_path)
            audit_events = connection.execute("SELECT event_type FROM audit_log WHERE event_type = 'work_permit.reissued';").fetchall()
            connection.close()
            self.assertEqual(original_record.status, WorkPermitStatus.CANCELED)
            self.assertIsNotNone(original_record.reissued_to_record_id)
            self.assertEqual(original_record.reissue_reason_text, 'Змінено умови виконання робіт')
            self.assertEqual(new_record.reissued_from_record_id, source_record.record_id)
            self.assertEqual(new_record.reissue_reason_text, 'Змінено умови виконання робіт')
            self.assertEqual(len(audit_events), 1)
            shut_down_logging()

    def test_reissue_work_permit_record_rejects_reissue_without_changed_conditions(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            application_paths = build_application_paths(Path(temporary_directory))
            context = initialize_application(application_paths)
            create_work_permit_record(context.database_path, 'ND-RS-003', 'Вогневі роботи', 'Дільниця А', '2099-04-10 08:00', '2099-04-10 12:00', 'Майстер', 'Інспектор', '0001', 'executor', 'Початковий наряд', access_role=AccessRole.INSPECTOR)
            source_record = next((record for record in load_work_permit_registry(context.database_path) if record.permit_number == 'ND-RS-003'))
            same_record = WorkPermitRecord(record_id=None, permit_number='ND-RS-004', work_kind=source_record.work_kind, work_location=source_record.work_location, starts_at=source_record.starts_at, ends_at=source_record.ends_at, responsible_person=source_record.responsible_person, issuer_person=source_record.issuer_person, note_text='Дубль', closed_at=None, participants=source_record.participants, status=WorkPermitStatus.ACTIVE, target_training_status=source_record.target_training_status, target_training_date=source_record.target_training_date, target_training_conducted_by=source_record.target_training_conducted_by, target_training_note=source_record.target_training_note, basis_text=source_record.basis_text, basis_note=source_record.basis_note, base_ends_at=source_record.base_ends_at)
            with self.assertRaisesRegex(ValueError, 'вид робіт'):
                reissue_work_permit_record(context.database_path, int(source_record.record_id), same_record, 'Без зміни умов', access_role=AccessRole.INSPECTOR)
            shut_down_logging()

    def test_reissue_work_permit_record_allows_participant_only_change(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            application_paths = build_application_paths(Path(temporary_directory))
            context = initialize_application(application_paths)
            create_work_permit_record(context.database_path, 'ND-RS-005', 'Вогневі роботи', 'Дільниця А', '2099-04-10 08:00', '2099-04-10 12:00', 'Майстер', '', '', '', 'Початковий склад', participants=(WorkPermitParticipant('0001', 'Коваль Олена', WorkPermitParticipantRole.EXECUTOR), WorkPermitParticipant('0002', 'Іваненко Сергій', WorkPermitParticipantRole.TEAM_MEMBER), WorkPermitParticipant('0003', 'Петренко Андрій', WorkPermitParticipantRole.TEAM_MEMBER)), access_role=AccessRole.INSPECTOR)
            source_record = next((record for record in load_work_permit_registry(context.database_path) if record.permit_number == 'ND-RS-005'))
            reissued_record = WorkPermitRecord(record_id=None, permit_number='ND-RS-006', work_kind=source_record.work_kind, work_location=source_record.work_location, starts_at=source_record.starts_at, ends_at=source_record.ends_at, responsible_person=source_record.responsible_person, issuer_person=source_record.issuer_person, note_text='Перевипуск через зміну складу', closed_at=None, participants=(WorkPermitParticipant('0001', 'Коваль Олена', WorkPermitParticipantRole.EXECUTOR), WorkPermitParticipant('0004', 'Шевченко Михайло', WorkPermitParticipantRole.TEAM_MEMBER), WorkPermitParticipant('0005', 'Бондар Тетяна', WorkPermitParticipantRole.TEAM_MEMBER)), status=WorkPermitStatus.ACTIVE, target_training_status=source_record.target_training_status, target_training_date=source_record.target_training_date, target_training_conducted_by=source_record.target_training_conducted_by, target_training_note=source_record.target_training_note, basis_text=source_record.basis_text, basis_note=source_record.basis_note, base_ends_at=source_record.base_ends_at)
            reissue_work_permit_record(context.database_path, int(source_record.record_id), reissued_record, 'Змінено більше 50% складу бригади', access_role=AccessRole.INSPECTOR)
            records = load_work_permit_registry(context.database_path)
            original_record = next((record for record in records if int(record.record_id) == int(source_record.record_id)))
            new_record = next((record for record in records if record.permit_number == 'ND-RS-006'))
            self.assertEqual(original_record.status, WorkPermitStatus.CANCELED)
            self.assertEqual(tuple((participant.employee_personnel_number for participant in new_record.participants)), ('0001', '0004', '0005'))
            shut_down_logging()
if __name__ == '__main__':
    unittest.main()
