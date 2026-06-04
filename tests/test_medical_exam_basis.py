import tempfile
import unittest
from pathlib import Path
from osah.application.services.create_medical_record import create_medical_record
from osah.application.services.initialize_application import initialize_application
from osah.application.services.load_medical_registry import load_medical_registry
from osah.infrastructure.config.application_paths import build_application_paths
from osah.infrastructure.logging.shutdown_logging import shut_down_logging
from osah.domain.entities.access_role import AccessRole

class MedicalExamBasisTests(unittest.TestCase):
    """Тести нового основания медогляду.
    Tests for the new medical exam basis field.
    """

    def test_medical_exam_basis_persists_and_loads(self) -> None:
        """Зберігає та повертає підставу медогляду.
        Persists and loads the medical exam basis.
        """
        with tempfile.TemporaryDirectory() as temporary_directory:
            context = initialize_application(build_application_paths(Path(temporary_directory)))
            create_medical_record(context.database_path, '0001', '2026-05-01', '2027-05-01', 'fit', '', medical_exam_basis='under_21', basis_text='Річний огляд', basis_note='Контрольний приклад', access_role=AccessRole.INSPECTOR)
            record = next((record for record in load_medical_registry(context.database_path) if record.basis_note == 'Контрольний приклад'))
            self.assertEqual(record.medical_exam_basis.value, 'under_21')
            self.assertEqual(record.basis_text, 'Річний огляд')
            self.assertEqual(record.basis_note, 'Контрольний приклад')
            self.assertFalse(hasattr(record, 'diagnosis'))
            shut_down_logging()

    def test_not_fit_is_critical_and_restricted_is_warning(self) -> None:
        """Сохраняет критичный и предупреждающий медстатусы без добавления диагнозов.
        Preserves critical and warning medical statuses without diagnosis fields.
        """
        with tempfile.TemporaryDirectory() as temporary_directory:
            context = initialize_application(build_application_paths(Path(temporary_directory)))
            create_medical_record(context.database_path, '0001', '2026-05-01', '2027-05-01', 'not_fit', 'Заборона', medical_exam_basis='harmful_or_dangerous_factors', access_role=AccessRole.INSPECTOR)
            create_medical_record(context.database_path, '0002', '2026-05-01', '2027-05-01', 'restricted', 'Нічні роботи', medical_exam_basis='heavy_work', access_role=AccessRole.INSPECTOR)
            records = load_medical_registry(context.database_path)
            not_fit_record = next((record for record in records if record.employee_personnel_number == '0001' and record.restriction_note == 'Заборона'))
            restricted_record = next((record for record in records if record.employee_personnel_number == '0002' and record.restriction_note == 'Нічні роботи'))
            self.assertEqual(not_fit_record.status.value, 'not_fit')
            self.assertEqual(restricted_record.status.value, 'restricted')
            shut_down_logging()
if __name__ == '__main__':
    unittest.main()
