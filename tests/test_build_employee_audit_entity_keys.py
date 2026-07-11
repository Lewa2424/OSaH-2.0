import unittest

from osah.domain.entities.medical_record import MedicalRecord
from osah.domain.entities.medical_decision import MedicalDecision
from osah.domain.entities.medical_status import MedicalStatus
from osah.domain.entities.ppe_record import PpeRecord
from osah.domain.entities.ppe_status import PpeStatus
from osah.domain.entities.training_record import TrainingRecord
from osah.domain.entities.training_status import TrainingStatus
from osah.domain.entities.training_type import TrainingType
from osah.domain.entities.work_permit_record import WorkPermitRecord
from osah.domain.entities.work_permit_status import WorkPermitStatus
from osah.domain.services.build_employee_audit_entity_keys import build_employee_audit_entity_keys


class BuildEmployeeAuditEntityKeysTests(unittest.TestCase):
    """Тести генерації audit-ключів для історії працівника.
    Tests for employee audit key generation.
    """

    def test_builds_exact_keys_for_related_records(self) -> None:
        keys = build_employee_audit_entity_keys(
            personnel_number="0001",
            training_records=(
                TrainingRecord(
                    record_id=7,
                    employee_personnel_number="0001",
                    employee_full_name="Працівник",
                    training_type=TrainingType.PRIMARY,
                    event_date="2026-01-01",
                    next_control_date="2026-07-01",
                    conducted_by="Інспектор",
                    note_text="",
                    status=TrainingStatus.CURRENT,
                ),
            ),
            ppe_records=(
                PpeRecord(
                    record_id=3,
                    employee_personnel_number="0001",
                    employee_full_name="Працівник",
                    ppe_name="Каска",
                    is_required=True,
                    is_issued=True,
                    issue_date="2026-01-01",
                    replacement_date="2027-01-01",
                    quantity=1,
                    note_text="",
                    status=PpeStatus.CURRENT,
                ),
            ),
            medical_records=(
                MedicalRecord(
                    record_id=5,
                    employee_personnel_number="0001",
                    employee_full_name="Працівник",
                    valid_from="2026-01-01",
                    valid_until="2027-01-01",
                    medical_decision=MedicalDecision.FIT,
                    restriction_note="",
                    status=MedicalStatus.CURRENT,
                ),
            ),
            work_permit_records=(
                WorkPermitRecord(
                    record_id=9,
                    permit_number="НД-1",
                    work_kind="Роботи",
                    work_location="Цех",
                    starts_at="2026-01-01 08:00",
                    ends_at="2026-01-01 18:00",
                    responsible_person="Майстер",
                    issuer_person="Інспектор",
                    note_text="",
                    closed_at=None,
                    participants=(),
                    status=WorkPermitStatus.ACTIVE,
                ),
            ),
        )

        self.assertEqual(keys.training_entity_prefix, "training:0001")
        self.assertEqual(keys.legacy_personnel_entity_name, "0001")
        self.assertIn("employee:0001", keys.exact_entity_names)
        self.assertIn("training:0001", keys.exact_entity_names)
        self.assertIn("training:7", keys.exact_entity_names)
        self.assertIn("ppe:0001", keys.exact_entity_names)
        self.assertIn("ppe:3", keys.exact_entity_names)
        self.assertIn("medical:0001", keys.exact_entity_names)
        self.assertIn("medical:5", keys.exact_entity_names)
        self.assertIn("work_permit:НД-1", keys.exact_entity_names)
        self.assertIn("0001", keys.exact_entity_names)


if __name__ == "__main__":
    unittest.main()
