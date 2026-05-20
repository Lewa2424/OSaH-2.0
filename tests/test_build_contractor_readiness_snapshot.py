import unittest

from osah.domain.entities.contractor_readiness_status import ContractorReadinessStatus
from osah.domain.entities.contractor_record import ContractorRecord
from osah.domain.entities.contractor_worker import ContractorWorker
from osah.domain.services.build_contractor_readiness_snapshot import build_contractor_readiness_snapshot


class BuildContractorReadinessSnapshotTests(unittest.TestCase):
    """Тести легкого підрахунку готовності підрядника.
    Tests lightweight contractor readiness calculation.
    """

    def test_returns_ready_when_all_workers_have_full_access(self) -> None:
        record = ContractorRecord(
            contractor_id="ctr-1",
            company_name="Інтертек",
            contact_person="Контакт",
            contact_phone="",
            contact_email="",
            activity_status="active",
            note_text="",
            workers=(
                ContractorWorker("w1", "Працівник 1", "Монтажник", True, True, True, True),
                ContractorWorker("w2", "Працівник 2", "Монтажник", True, True, True, True),
            ),
        )

        snapshot = build_contractor_readiness_snapshot(record)

        self.assertEqual(snapshot.status, ContractorReadinessStatus.READY)
        self.assertTrue(snapshot.can_work_now)
        self.assertEqual(snapshot.ready_workers, 2)
        self.assertEqual(snapshot.problem_workers, 0)

    def test_returns_warning_when_part_of_workers_have_issues(self) -> None:
        record = ContractorRecord(
            contractor_id="ctr-2",
            company_name="ПромВисота",
            contact_person="Контакт",
            contact_phone="",
            contact_email="",
            activity_status="active",
            note_text="",
            workers=(
                ContractorWorker("w1", "Працівник 1", "Монтажник", True, True, True, True),
                ContractorWorker("w2", "Працівник 2", "Монтажник", False, True, True, True, "Немає інструктажу"),
            ),
        )

        snapshot = build_contractor_readiness_snapshot(record)

        self.assertEqual(snapshot.status, ContractorReadinessStatus.WARNING)
        self.assertFalse(snapshot.can_work_now)
        self.assertEqual(snapshot.ready_workers, 1)
        self.assertEqual(snapshot.problem_workers, 1)
        self.assertIn("інструктаж", snapshot.issues_text)

    def test_returns_blocked_when_no_workers_defined(self) -> None:
        record = ContractorRecord(
            contractor_id="ctr-3",
            company_name="Порожній підрядник",
            contact_person="Контакт",
            contact_phone="",
            contact_email="",
            activity_status="active",
            note_text="",
        )

        snapshot = build_contractor_readiness_snapshot(record)

        self.assertEqual(snapshot.status, ContractorReadinessStatus.BLOCKED)
        self.assertFalse(snapshot.can_work_now)
        self.assertIn("не заповнено", snapshot.headline_text)


if __name__ == "__main__":
    unittest.main()
