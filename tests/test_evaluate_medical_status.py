import unittest
from datetime import date

from osah.domain.entities.medical_decision import MedicalDecision
from osah.domain.entities.medical_record import MedicalRecord
from osah.domain.entities.medical_status import MedicalStatus
from osah.domain.services.evaluate_medical_status import evaluate_medical_status


class EvaluateMedicalStatusTests(unittest.TestCase):
    """Тести оцінки статусу медичного запису.
    Тесты оценки статуса медицинской записи.
    """

    # ###### ПЕРЕВІРКА СТАТУСУ ПРОСТРОЧЕНОГО МЕДДОПУСКУ / ПРОВЕРКА СТАТУСА ПРОСРОЧЕННОГО МЕДДОПУСКА ######
    def test_evaluate_medical_status_returns_expired_for_past_valid_until(self) -> None:
        """Перевіряє повернення статусу прострочення для минулого строку дії.
        Проверяет возврат статуса просрочки для прошедшего срока действия.
        """

        medical_record = MedicalRecord(
            record_id=1,
            employee_personnel_number="0001",
            employee_full_name="Тестовий працівник",
            valid_from="2026-01-01",
            valid_until="2026-04-01",
            medical_decision=MedicalDecision.FIT,
            restriction_note="",
            status=MedicalStatus.CURRENT,
        )

        self.assertEqual(
            evaluate_medical_status(medical_record, today=date(2026, 4, 10)),
            MedicalStatus.EXPIRED,
        )

    # ###### ПЕРЕВІРКА СТАТУСУ ОБМЕЖЕННЯ / ПРОВЕРКА СТАТУСА ОГРАНИЧЕНИЯ ######
    def test_evaluate_medical_status_returns_restricted_for_restricted_decision(self) -> None:
        """Перевіряє повернення статусу обмеження для рішення з обмеженнями.
        Проверяет возврат статуса ограничения для решения с ограничениями.
        """

        medical_record = MedicalRecord(
            record_id=2,
            employee_personnel_number="0001",
            employee_full_name="Тестовий працівник",
            valid_from="2026-04-01",
            valid_until="2026-06-01",
            medical_decision=MedicalDecision.RESTRICTED,
            restriction_note="Без висотних робіт",
            status=MedicalStatus.CURRENT,
        )

        self.assertEqual(
            evaluate_medical_status(medical_record, today=date(2026, 4, 10)),
            MedicalStatus.RESTRICTED,
        )

    # ###### ПЕРЕВІРКА СТАТУСУ ПОПЕРЕДЖЕННЯ / ПРОВЕРКА СТАТУСА ПРЕДУПРЕЖДЕНИЯ ######
    def test_evaluate_medical_status_returns_warning_when_valid_until_is_close(self) -> None:
        """Перевіряє повернення статусу уваги для близького завершення строку.
        Проверяет возврат статуса внимания для близкого окончания срока.
        """

        medical_record = MedicalRecord(
            record_id=3,
            employee_personnel_number="0001",
            employee_full_name="Тестовий працівник",
            valid_from="2026-04-01",
            valid_until="2026-04-14",
            medical_decision=MedicalDecision.FIT,
            restriction_note="",
            status=MedicalStatus.CURRENT,
        )

        self.assertEqual(
            evaluate_medical_status(medical_record, today=date(2026, 4, 10)),
            MedicalStatus.WARNING,
        )


if __name__ == "__main__":
    unittest.main()
