import tempfile
import unittest
from pathlib import Path

from osah.application.services.initialize_application import initialize_application
from osah.application.services.load_contractor_workspace import load_contractor_workspace
from osah.application.services.save_contractor_record import save_contractor_record
from osah.domain.entities.contractor_record import ContractorRecord
from osah.domain.entities.contractor_worker import ContractorWorker
from osah.infrastructure.config.application_paths import build_application_paths
from osah.infrastructure.logging.shutdown_logging import shut_down_logging


class ContractorWorkspaceTests(unittest.TestCase):
    """Тести збереження і завантаження легкого реєстру підрядників.
    Tests persistence for lightweight contractors registry.
    """

    def test_initialize_application_seeds_demo_contractors(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            context = initialize_application(build_application_paths(Path(temporary_directory)))

            workspace = load_contractor_workspace(context.database_path)

            self.assertGreaterEqual(len(workspace.records), 5)
            company_names = {record.company_name for record in workspace.records}
            self.assertIn("Інтертек", company_names)
            self.assertIn("ГазЛайн Монтаж", company_names)
            shut_down_logging()

    def test_save_and_load_contractor_record_keeps_workers_and_scope(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            context = initialize_application(build_application_paths(Path(temporary_directory)))
            saved = save_contractor_record(
                context.database_path,
                ContractorRecord(
                    contractor_id="",
                    company_name="Нова компанія",
                    contact_person="Петренко",
                    contact_phone="+380500000001",
                    contact_email="office@test.local",
                    activity_status="active",
                    note_text="Контрольний запис",
                    enterprise_supervisor="Іваненко С.П.",
                    work_scope_text="Цех 1, монтаж трубопроводу",
                    workers=(
                        ContractorWorker("w1", "Перший Працівник", "Монтажник", True, True, True, True),
                        ContractorWorker("w2", "Другий Працівник", "Стропальник", True, False, True, True, "Потрібен комплект ЗІЗ"),
                    ),
                ),
            )

            workspace = load_contractor_workspace(context.database_path)
            restored = next(record for record in workspace.records if record.contractor_id == saved.contractor_id)

            self.assertEqual(restored.enterprise_supervisor, "Іваненко С.П.")
            self.assertEqual(restored.work_scope_text, "Цех 1, монтаж трубопроводу")
            self.assertEqual(len(restored.workers), 2)
            self.assertEqual(restored.workers[1].full_name, "Другий Працівник")
            self.assertFalse(restored.workers[1].ppe_ok)
            shut_down_logging()


if __name__ == "__main__":
    unittest.main()
