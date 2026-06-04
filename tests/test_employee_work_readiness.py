import sqlite3
import tempfile
import unittest
from pathlib import Path
from osah.application.services.create_medical_record import create_medical_record
from osah.application.services.create_ppe_record import create_ppe_record
from osah.application.services.create_training_record import create_training_record
from osah.application.services.initialize_application import initialize_application
from osah.application.services.load_employee_work_readiness import load_employee_work_readiness
from osah.infrastructure.config.application_paths import build_application_paths
from osah.infrastructure.logging.shutdown_logging import shut_down_logging
from osah.domain.entities.access_role import AccessRole

class EmployeeWorkReadinessTests(unittest.TestCase):
    """Тести сервісу готовності працівника до робіт.
    Tests for the employee work-readiness service.
    """

    def test_employee_without_problems_returns_normal_levels(self) -> None:
        """Повертає normal для працівника без проблемних записів.
        Returns normal levels for an employee without problems.
        """
        with tempfile.TemporaryDirectory() as temporary_directory:
            context = initialize_application(build_application_paths(Path(temporary_directory)))
            try:
                _clear_employee_related_records(context.database_path, '0001')
                create_training_record(context.database_path, '0001', 'targeted', '2026-05-01', '', 'Інженер', 'Норма', knowledge_check_result='satisfactory', access_role=AccessRole.INSPECTOR)
                create_ppe_record(context.database_path, '0001', 'Каска', True, True, '2026-05-01', '2026-12-01', '1', 'Норма', provision_status='issued', compliance_check_state='checked', access_role=AccessRole.INSPECTOR)
                create_medical_record(context.database_path, '0001', '2026-05-01', '2027-05-01', 'fit', '', medical_exam_basis='internal_list', access_role=AccessRole.INSPECTOR)
                readiness = load_employee_work_readiness(context.database_path, '0001')
                self.assertEqual(readiness.training_level.value, 'normal')
                self.assertEqual(readiness.medical_level.value, 'normal')
                self.assertEqual(readiness.ppe_level.value, 'normal')
            finally:
                shut_down_logging()

    def test_expired_medical_sets_critical_level(self) -> None:
        """Повертає critical для простроченого меддопуску.
        Returns critical for expired medical readiness.
        """
        with tempfile.TemporaryDirectory() as temporary_directory:
            context = initialize_application(build_application_paths(Path(temporary_directory)))
            try:
                _clear_employee_related_records(context.database_path, '0001')
                create_medical_record(context.database_path, '0001', '2024-01-01', '2024-02-01', 'fit', '', medical_exam_basis='heavy_work', access_role=AccessRole.INSPECTOR)
                readiness = load_employee_work_readiness(context.database_path, '0001')
                self.assertEqual(readiness.medical_level.value, 'critical')
                self.assertIn('прострочено', readiness.medical_message.lower())
            finally:
                shut_down_logging()

    def test_required_not_issued_ppe_sets_critical_level(self) -> None:
        """Повертає critical для обов'язкового невиданого ЗІЗ.
        Returns critical for required-not-issued PPE.
        """
        with tempfile.TemporaryDirectory() as temporary_directory:
            context = initialize_application(build_application_paths(Path(temporary_directory)))
            try:
                _clear_employee_related_records(context.database_path, '0001')
                create_ppe_record(context.database_path, '0001', 'Щиток', True, False, '2026-05-01', '2026-12-01', '1', 'Немає видачі', provision_status='required_not_issued', access_role=AccessRole.INSPECTOR)
                readiness = load_employee_work_readiness(context.database_path, '0001')
                self.assertEqual(readiness.ppe_level.value, 'critical')
                self.assertIn('невиданий', readiness.ppe_message.lower())
            finally:
                shut_down_logging()

    def test_unsatisfactory_training_sets_critical_level(self) -> None:
        """Повертає critical для незадовільного інструктажу.
        Returns critical for unsatisfactory training.
        """
        with tempfile.TemporaryDirectory() as temporary_directory:
            context = initialize_application(build_application_paths(Path(temporary_directory)))
            try:
                _clear_employee_related_records(context.database_path, '0001')
                create_training_record(context.database_path, '0001', 'targeted', '2026-05-01', '', 'Інженер', 'Незадовільно', knowledge_check_result='unsatisfactory', access_role=AccessRole.INSPECTOR)
                readiness = load_employee_work_readiness(context.database_path, '0001')
                self.assertEqual(readiness.training_level.value, 'critical')
                self.assertIn('незадовіль', readiness.training_message.lower())
            finally:
                shut_down_logging()

def _clear_employee_related_records(database_path: Path, personnel_number: str) -> None:
    """Очищає пов'язані записи працівника для ізольованого тесту.
    Clears employee-linked records for an isolated test scenario.
    """
    connection = sqlite3.connect(database_path)
    try:
        work_permit_ids = tuple((row[0] for row in connection.execute('SELECT work_permit_id FROM work_permit_participants WHERE employee_personnel_number = ?;', (personnel_number,)).fetchall()))
        connection.execute('DELETE FROM work_permit_participants WHERE employee_personnel_number = ?;', (personnel_number,))
        if work_permit_ids:
            placeholders = ', '.join(('?' for _ in work_permit_ids))
            connection.execute(f'DELETE FROM work_permits WHERE id IN ({placeholders}) AND id NOT IN (SELECT work_permit_id FROM work_permit_participants);', work_permit_ids)
        connection.execute('DELETE FROM trainings WHERE employee_personnel_number = ?;', (personnel_number,))
        connection.execute('DELETE FROM ppe_records WHERE employee_personnel_number = ?;', (personnel_number,))
        connection.execute('DELETE FROM medical_records WHERE employee_personnel_number = ?;', (personnel_number,))
        connection.execute('DELETE FROM notifications WHERE employee_personnel_number = ?;', (personnel_number,))
        connection.commit()
    finally:
        connection.close()
if __name__ == '__main__':
    unittest.main()
