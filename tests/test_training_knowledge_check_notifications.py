import sqlite3
import tempfile
import unittest
from pathlib import Path
from osah.application.services.create_training_record import create_training_record
from osah.application.services.initialize_application import initialize_application
from osah.application.services.load_training_registry import load_training_registry
from osah.infrastructure.config.application_paths import build_application_paths
from osah.infrastructure.database.create_database_connection import create_database_connection
from osah.infrastructure.database.schema.ensure_core_schema import ensure_core_schema
from osah.infrastructure.logging.shutdown_logging import shut_down_logging
from osah.domain.entities.access_role import AccessRole

class TrainingKnowledgeCheckNotificationTests(unittest.TestCase):
    """Тести нових полів перевірки знань для інструктажів.
    Tests for training knowledge-check fields and notifications.
    """

    def test_create_training_with_satisfactory_result_persists_value(self) -> None:
        """Зберігає позитивний результат перевірки знань у записі.
        Persists a satisfactory knowledge-check result in the record.
        """
        with tempfile.TemporaryDirectory() as temporary_directory:
            context = initialize_application(build_application_paths(Path(temporary_directory)))
            try:
                create_training_record(context.database_path, '0001', 'targeted', '2026-05-01', '', 'Інженер з ОП', 'Перевірка після вступу', knowledge_check_result='satisfactory', work_admission_status='allowed', knowledge_check_note='Допущено до роботи', basis_text='Наказ №12', basis_note='Тестовий запис', access_role=AccessRole.INSPECTOR)
                created_record = next((record for record in load_training_registry(context.database_path) if record.note_text == 'Перевірка після вступу'))
                self.assertEqual(created_record.knowledge_check_result.value, 'satisfactory')
                self.assertEqual(created_record.work_admission_status.value, 'allowed')
                self.assertEqual(created_record.basis_text, 'Наказ №12')
                self.assertEqual(created_record.basis_note, 'Тестовий запис')
            finally:
                shut_down_logging()

    def test_unsatisfactory_training_creates_critical_notification(self) -> None:
        """Створює critical-сповіщення для незадовільного інструктажу.
        Creates a critical notification for an unsatisfactory training.
        """
        with tempfile.TemporaryDirectory() as temporary_directory:
            context = initialize_application(build_application_paths(Path(temporary_directory)))
            try:
                create_training_record(context.database_path, '0001', 'introductory', '2026-03-01', '', 'Інженер з ОП', 'Вступний перед незачетом', access_role=AccessRole.INSPECTOR)
                create_training_record(context.database_path, '0001', 'primary', '2026-04-01', '', 'Інженер з ОП', 'Первинний перед незачетом', work_risk_category='regular', access_role=AccessRole.INSPECTOR)
                create_training_record(context.database_path, '0001', 'repeated', '2026-05-01', '', 'Інженер з ОП', 'Незадовільна перевірка', knowledge_check_result='unsatisfactory', work_risk_category='regular', access_role=AccessRole.INSPECTOR)
                connection = sqlite3.connect(context.database_path)
                rows = connection.execute("\n                    SELECT notification_level, message_text\n                    FROM notifications\n                    WHERE source_module = 'trainings.registry' AND message_text LIKE '%незадовіль%'\n                    ").fetchall()
                connection.close()
                self.assertTrue(rows)
                self.assertTrue(all((row[0] == 'critical' for row in rows)))
            finally:
                shut_down_logging()

    def test_targeted_unsatisfactory_training_creates_forbidden_admission_message(self) -> None:
        """Пише окремий текст про заборону допуску для цільового інструктажу.
        Writes the explicit no-admission message for targeted training.
        """
        with tempfile.TemporaryDirectory() as temporary_directory:
            context = initialize_application(build_application_paths(Path(temporary_directory)))
            try:
                create_training_record(context.database_path, '0001', 'targeted', '2026-05-01', '', 'Інженер з ОП', 'Цільовий інструктаж', knowledge_check_result='unsatisfactory', access_role=AccessRole.INSPECTOR)
                connection = sqlite3.connect(context.database_path)
                message_row = connection.execute("\n                    SELECT message_text\n                    FROM notifications\n                    WHERE source_module = 'trainings.registry' AND message_text LIKE '%Допуск до робіт заборонено%'\n                    ").fetchone()
                connection.close()
                self.assertIsNotNone(message_row)
            finally:
                shut_down_logging()

    def test_ensure_core_schema_adds_new_training_columns_to_legacy_table(self) -> None:
        """Додає нові колонки до старої таблиці trainings без ручної міграції.
        Adds new columns to a legacy trainings table without manual migration.
        """
        with tempfile.TemporaryDirectory() as temporary_directory:
            database_path = Path(temporary_directory) / 'legacy.db'
            connection = create_database_connection(database_path)
            try:
                connection.execute("\n                    CREATE TABLE trainings (\n                        id INTEGER PRIMARY KEY AUTOINCREMENT,\n                        employee_personnel_number TEXT NOT NULL,\n                        training_type TEXT NOT NULL,\n                        event_date TEXT NOT NULL,\n                        next_control_date TEXT NOT NULL DEFAULT '',\n                        conducted_by TEXT NOT NULL DEFAULT '',\n                        note_text TEXT NOT NULL DEFAULT '',\n                        person_category TEXT NOT NULL DEFAULT 'own_employee',\n                        requires_primary_on_workplace INTEGER NOT NULL DEFAULT 0,\n                        work_risk_category TEXT NOT NULL DEFAULT 'not_applicable',\n                        next_control_basis TEXT NOT NULL DEFAULT 'manual'\n                    );\n                    ")
                ensure_core_schema(connection)
                columns = {row['name'] for row in connection.execute('PRAGMA table_info(trainings);').fetchall()}
            finally:
                connection.close()
            self.assertIn('knowledge_check_result', columns)
            self.assertIn('work_admission_status', columns)
            self.assertIn('knowledge_check_note', columns)
            self.assertIn('basis_text', columns)
            self.assertIn('basis_note', columns)
if __name__ == '__main__':
    unittest.main()
