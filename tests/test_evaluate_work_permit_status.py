import unittest
from datetime import datetime

from osah.domain.entities.work_permit_participant import WorkPermitParticipant
from osah.domain.entities.work_permit_participant_role import WorkPermitParticipantRole
from osah.domain.entities.work_permit_record import WorkPermitRecord
from osah.domain.entities.work_permit_status import WorkPermitStatus
from osah.domain.services.evaluate_work_permit_status import evaluate_work_permit_status


class EvaluateWorkPermitStatusTests(unittest.TestCase):
    """Тести оцінки статусу наряду-допуску.
    Tests for work permit status evaluation.
    """

    def test_evaluate_work_permit_status_returns_expired_for_unclosed_past_record(self) -> None:
        """Повертає прострочення для відкритого минулого наряду.
        Returns expired for an open past permit.
        """

        work_permit_record = WorkPermitRecord(
            record_id=1,
            permit_number="НД-001",
            work_kind="Висотні роботи",
            work_location="Цех 1",
            starts_at="2026-04-10 08:00",
            ends_at="2026-04-10 12:00",
            responsible_person="Майстер",
            issuer_person="Інспектор",
            note_text="",
            closed_at=None,
            participants=(
                WorkPermitParticipant(
                    employee_personnel_number="0001",
                    employee_full_name="Тестовий працівник",
                    participant_role=WorkPermitParticipantRole.EXECUTOR,
                ),
            ),
            status=WorkPermitStatus.ACTIVE,
        )

        self.assertEqual(
            evaluate_work_permit_status(work_permit_record, current_moment=datetime(2026, 4, 10, 12, 1)),
            WorkPermitStatus.EXPIRED,
        )

    def test_evaluate_work_permit_status_returns_active_for_lightweight_registry_record(self) -> None:
        """Легкий реєстровий запис лишається активним.
        A lightweight registry entry remains active.
        """

        work_permit_record = WorkPermitRecord(
            record_id=2,
            permit_number="НД-002",
            work_kind="Ремонтні роботи",
            work_location="Цех 2",
            starts_at="2026-04-10 08:00",
            ends_at="2026-04-20 18:00",
            responsible_person="Майстер",
            issuer_person="",
            note_text="",
            closed_at=None,
            participants=(),
            status=WorkPermitStatus.ACTIVE,
        )

        self.assertEqual(
            evaluate_work_permit_status(work_permit_record, current_moment=datetime(2026, 4, 10, 9, 0)),
            WorkPermitStatus.ACTIVE,
        )

    def test_evaluate_work_permit_status_returns_invalid_without_responsible_person(self) -> None:
        """Без керівника робіт запис проблемний.
        A record without responsible person is invalid.
        """

        work_permit_record = WorkPermitRecord(
            record_id=3,
            permit_number="НД-003",
            work_kind="Ремонтні роботи",
            work_location="Цех 3",
            starts_at="2026-04-10 08:00",
            ends_at="2026-04-10 18:00",
            responsible_person="",
            issuer_person="",
            note_text="",
            closed_at=None,
            participants=(),
            status=WorkPermitStatus.ACTIVE,
        )

        self.assertEqual(
            evaluate_work_permit_status(work_permit_record, current_moment=datetime(2026, 4, 10, 9, 0)),
            WorkPermitStatus.INVALID,
        )

    def test_evaluate_work_permit_status_returns_closed_for_manually_closed_record(self) -> None:
        """Повертає закритий статус для вручну закритого наряду.
        Returns closed for a manually closed permit.
        """

        work_permit_record = WorkPermitRecord(
            record_id=4,
            permit_number="НД-004",
            work_kind="Вогневі роботи",
            work_location="Цех 2",
            starts_at="2026-04-10 08:00",
            ends_at="2026-04-10 18:00",
            responsible_person="Майстер",
            issuer_person="Інспектор",
            note_text="",
            closed_at="2026-04-10 17:30",
            participants=(
                WorkPermitParticipant(
                    employee_personnel_number="0001",
                    employee_full_name="Тестовий працівник",
                    participant_role=WorkPermitParticipantRole.EXECUTOR,
                ),
            ),
            status=WorkPermitStatus.ACTIVE,
        )

        self.assertEqual(
            evaluate_work_permit_status(work_permit_record, current_moment=datetime(2026, 4, 10, 17, 31)),
            WorkPermitStatus.CLOSED,
        )

    def test_evaluate_work_permit_status_returns_canceled_for_superseded_record(self) -> None:
        """Повертає перевипущений статус для заміненого наряду.
        Returns reissued for a superseded permit.
        """

        work_permit_record = WorkPermitRecord(
            record_id=5,
            permit_number="НД-005",
            work_kind="Газонебезпечні роботи",
            work_location="Цех 3",
            starts_at="2026-04-10 08:00",
            ends_at="2026-04-10 18:00",
            responsible_person="Майстер",
            issuer_person="Інспектор",
            note_text="",
            closed_at=None,
            canceled_at="2026-04-10 10:00",
            reissued_to_record_id=17,
            participants=(
                WorkPermitParticipant(
                    employee_personnel_number="0001",
                    employee_full_name="Тестовий працівник",
                    participant_role=WorkPermitParticipantRole.EXECUTOR,
                ),
            ),
            status=WorkPermitStatus.ACTIVE,
        )

        self.assertEqual(
            evaluate_work_permit_status(work_permit_record, current_moment=datetime(2026, 4, 10, 10, 1)),
            WorkPermitStatus.CANCELED,
        )


if __name__ == "__main__":
    unittest.main()
