import unittest
from datetime import datetime

from osah.domain.entities.work_permit_participant import WorkPermitParticipant
from osah.domain.entities.work_permit_participant_role import WorkPermitParticipantRole
from osah.domain.entities.work_permit_record import WorkPermitRecord
from osah.domain.entities.work_permit_status import WorkPermitStatus
from osah.domain.services.evaluate_work_permit_status import evaluate_work_permit_status


class EvaluateWorkPermitStatusTests(unittest.TestCase):
    """Тести оцінки статусу наряду-допуску.
    Тесты оценки статуса наряда-допуска.
    """

    # ###### ПЕРЕВІРКА СТАТУСУ ПРОСТРОЧЕНОГО НАРЯДУ / ПРОВЕРКА СТАТУСА ПРОСРОЧЕННОГО НАРЯДА ######
    def test_evaluate_work_permit_status_returns_expired_for_unclosed_past_record(self) -> None:
        """Перевіряє повернення статусу прострочення для незакритого наряду після строку завершення.
        Проверяет возврат статуса просрочки для незакрытого наряда после срока завершения.
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

    # ###### ПЕРЕВІРКА СТАТУСУ ЗАКРИТОГО НАРЯДУ / ПРОВЕРКА СТАТУСА ЗАКРЫТОГО НАРЯДА ######
    def test_evaluate_work_permit_status_returns_closed_for_manually_closed_record(self) -> None:
        """Перевіряє повернення статусу закриття для вручну закритого наряду.
        Проверяет возврат статуса закрытия для вручную закрытого наряда.
        """

        work_permit_record = WorkPermitRecord(
            record_id=2,
            permit_number="НД-002",
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


if __name__ == "__main__":
    unittest.main()
