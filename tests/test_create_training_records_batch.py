import tempfile
import unittest
from pathlib import Path
from osah.application.services.create_training_records_batch import create_training_records_batch
from osah.application.services.initialize_application import initialize_application
from osah.application.services.load_training_registry import load_training_registry
from osah.infrastructure.config.application_paths import build_application_paths
from osah.infrastructure.logging.shutdown_logging import shut_down_logging
from osah.domain.entities.access_role import AccessRole

class CreateTrainingRecordsBatchTests(unittest.TestCase):
    """Тести масового створення записів інструктажів.
    Tests for batch creation of training records.
    """

    def test_create_training_records_batch_creates_records_for_each_employee(self) -> None:
        """Створює коректний масовий повторний інструктаж після базового циклу.
        Creates a valid batch repeated training after the base cycle exists.
        """
        with tempfile.TemporaryDirectory() as temporary_directory:
            application_paths = build_application_paths(Path(temporary_directory))
            context = initialize_application(application_paths)
            try:
                training_total_before = len(load_training_registry(context.database_path))
                for training_type, event_date_text, note_text in (('introductory', '2026-04-01', 'Вступний масовий запис'), ('primary', '2026-04-02', 'Первинний масовий запис')):
                    create_training_records_batch(database_path=context.database_path, employee_personnel_numbers=('0001', '0002'), training_type=training_type, event_date_text=event_date_text, next_control_date_text='', work_risk_category='high_risk', conducted_by='Інспектор з ОП', note_text=note_text, access_role=AccessRole.INSPECTOR)
                create_training_records_batch(database_path=context.database_path, employee_personnel_numbers=('0001', '0002'), training_type='repeated', event_date_text='2026-04-10', next_control_date_text='', work_risk_category='high_risk', conducted_by='Інспектор з ОП', note_text='Масовий запис', access_role=AccessRole.INSPECTOR)
                training_records = load_training_registry(context.database_path)
                self.assertEqual(len(training_records), training_total_before + 6)
                self.assertTrue({'0001', '0002'}.issubset({training_record.employee_personnel_number for training_record in training_records if training_record.note_text == 'Масовий запис'}))
            finally:
                shut_down_logging()

    def test_create_training_records_batch_rejects_repeated_without_base_cycle(self) -> None:
        """Не дозволяє масово створити повторний інструктаж без базового циклу.
        Rejects batch creation of repeated trainings without a base cycle.
        """
        with tempfile.TemporaryDirectory() as temporary_directory:
            application_paths = build_application_paths(Path(temporary_directory))
            context = initialize_application(application_paths)
            try:
                with self.assertRaisesRegex(ValueError, 'послідовність інструктажів'):
                    create_training_records_batch(database_path=context.database_path, employee_personnel_numbers=('0001', '0002'), training_type='repeated', event_date_text='2026-04-10', next_control_date_text='', work_risk_category='high_risk', conducted_by='Інспектор з ОП', note_text='Помилковий масовий запис', access_role=AccessRole.INSPECTOR)
            finally:
                shut_down_logging()
if __name__ == '__main__':
    unittest.main()
