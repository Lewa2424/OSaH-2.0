import sqlite3
import tempfile
import unittest
from pathlib import Path
from osah.application.services.create_work_permit_record import create_work_permit_record
from osah.application.services.extend_work_permit_record import extend_work_permit_record
from osah.application.services.initialize_application import initialize_application
from osah.application.services.load_work_permit_registry import load_work_permit_registry
from osah.infrastructure.config.application_paths import build_application_paths
from osah.infrastructure.logging.shutdown_logging import shut_down_logging
from osah.domain.entities.access_role import AccessRole

class ExtendWorkPermitRecordTests(unittest.TestCase):
    """Тести одноразового продовження наряду-допуску.
    Tests for one-time work permit extension.
    """

    def test_extend_work_permit_record_updates_end_date_and_writes_audit_log(self) -> None:
        """Перевіряє успішне одноразове продовження наряду в межах ще 15 днів.
        Checks successful one-time permit extension within another 15 days.
        """
        with tempfile.TemporaryDirectory() as temporary_directory:
            application_paths = build_application_paths(Path(temporary_directory))
            context = initialize_application(application_paths)
            create_work_permit_record(context.database_path, 'ND-EXT-001', 'Вогневі роботи', 'Дільниця А', '2099-04-10 08:00', '2099-04-20 18:00', 'Майстер', 'Інспектор', '0001', 'executor', 'Початковий наряд', access_role=AccessRole.INSPECTOR)
            created_record = next((record for record in load_work_permit_registry(context.database_path) if record.permit_number == 'ND-EXT-001'))
            extend_work_permit_record(context.database_path, int(created_record.record_id), '2099-05-05 18:00', 'Завершення робіт перенесено без зміни заходів безпеки', access_role=AccessRole.INSPECTOR)
            extended_record = next((record for record in load_work_permit_registry(context.database_path) if int(record.record_id) == int(created_record.record_id)))
            connection = sqlite3.connect(context.database_path)
            audit_events = connection.execute("SELECT event_type FROM audit_log WHERE event_type = 'work_permit.extended';").fetchall()
            connection.close()
            self.assertEqual(extended_record.base_ends_at, '2099-04-20 18:00')
            self.assertEqual(extended_record.ends_at, '2099-05-05 18:00')
            self.assertEqual(extended_record.extension_count, 1)
            self.assertEqual(extended_record.extension_reason_text, 'Завершення робіт перенесено без зміни заходів безпеки')
            self.assertEqual(len(audit_events), 1)
            shut_down_logging()

    def test_extend_work_permit_record_rejects_second_extension(self) -> None:
        """Перевіряє, що повторне продовження того самого наряду заборонене.
        Checks that extending the same permit twice is forbidden.
        """
        with tempfile.TemporaryDirectory() as temporary_directory:
            application_paths = build_application_paths(Path(temporary_directory))
            context = initialize_application(application_paths)
            create_work_permit_record(context.database_path, 'ND-EXT-002', 'Вогневі роботи', 'Дільниця Б', '2099-04-10 08:00', '2099-04-18 18:00', 'Майстер', 'Інспектор', '0001', 'executor', 'Початковий наряд', access_role=AccessRole.INSPECTOR)
            created_record = next((record for record in load_work_permit_registry(context.database_path) if record.permit_number == 'ND-EXT-002'))
            extend_work_permit_record(context.database_path, int(created_record.record_id), '2099-04-28 18:00', 'Перше продовження', access_role=AccessRole.INSPECTOR)
            with self.assertRaisesRegex(ValueError, 'уже був продовжений'):
                extend_work_permit_record(context.database_path, int(created_record.record_id), '2099-05-05 18:00', 'Друге продовження', access_role=AccessRole.INSPECTOR)
            shut_down_logging()

    def test_extend_work_permit_record_allows_extending_expired_record(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            application_paths = build_application_paths(Path(temporary_directory))
            context = initialize_application(application_paths)
            create_work_permit_record(context.database_path, 'ND-EXT-003', 'Р’РѕРіРЅРµРІС– СЂРѕР±РѕС‚Рё', 'Р”С–Р»СЊРЅРёС†СЏ Р’', '2000-04-10 08:00', '2000-04-20 18:00', 'РњР°Р№СЃС‚РµСЂ', 'Р†РЅСЃРїРµРєС‚РѕСЂ', '0001', 'executor', 'РџСЂРѕСЃС‚СЂРѕС‡РµРЅРёР№ РЅР°СЂСЏРґ', access_role=AccessRole.INSPECTOR)
            created_record = next((record for record in load_work_permit_registry(context.database_path) if record.permit_number == 'ND-EXT-003'))
            extend_work_permit_record(context.database_path, int(created_record.record_id), '2000-05-01 18:00', 'РџРѕС‚СЂС–Р±РЅРѕ РґРѕРєРѕРјРїР»РµРєС‚СѓРІР°С‚Рё СЂРѕР±РѕС‚Рё Р±РµР· Р·РјС–РЅРё Р·Р°С…РѕРґС–РІ', access_role=AccessRole.INSPECTOR)
            extended_record = next((record for record in load_work_permit_registry(context.database_path) if int(record.record_id) == int(created_record.record_id)))
            self.assertEqual(extended_record.ends_at, '2000-05-01 18:00')
            self.assertEqual(extended_record.extension_count, 1)
            shut_down_logging()
if __name__ == '__main__':
    unittest.main()
