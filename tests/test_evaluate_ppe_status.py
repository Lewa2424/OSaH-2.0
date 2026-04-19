import unittest
from datetime import date

from osah.domain.entities.ppe_record import PpeRecord
from osah.domain.entities.ppe_status import PpeStatus
from osah.domain.services.evaluate_ppe_status import evaluate_ppe_status


class EvaluatePpeStatusTests(unittest.TestCase):
    """Тести оцінки статусу ЗІЗ.
    Тесты оценки статуса СИЗ.
    """

    # ###### ПЕРЕВІРКА КРИТИЧНОГО СТАТУСУ НЕ ВИДАНО / ПРОВЕРКА КРИТИЧЕСКОГО СТАТУСА НЕ ВЫДАНО ######
    def test_evaluate_ppe_status_returns_not_issued_for_required_unissued_ppe(self) -> None:
        """Перевіряє критичний статус для обов'язкового невиданого ЗІЗ.
        Проверяет критический статус для обязательного невыданного СИЗ.
        """

        ppe_record = PpeRecord(
            record_id=1,
            employee_personnel_number="0001",
            employee_full_name="Працівник",
            ppe_name="Каска",
            is_required=True,
            is_issued=False,
            issue_date="2026-04-01",
            replacement_date="2026-05-01",
            quantity=1,
            note_text="",
            status=PpeStatus.CURRENT,
        )

        self.assertEqual(evaluate_ppe_status(ppe_record, today=date(2026, 4, 10)), PpeStatus.NOT_ISSUED)

    # ###### ПЕРЕВІРКА СТАТУСУ УВАГИ ПО СТРОКУ ЗАМІНИ / ПРОВЕРКА СТАТУСА ВНИМАНИЯ ПО СРОКУ ЗАМЕНЫ ######
    def test_evaluate_ppe_status_returns_warning_before_replacement_date(self) -> None:
        """Перевіряє статус уваги перед строком заміни ЗІЗ.
        Проверяет статус внимания перед сроком замены СИЗ.
        """

        ppe_record = PpeRecord(
            record_id=1,
            employee_personnel_number="0001",
            employee_full_name="Працівник",
            ppe_name="Рукавиці",
            is_required=True,
            is_issued=True,
            issue_date="2026-04-01",
            replacement_date="2026-04-15",
            quantity=1,
            note_text="",
            status=PpeStatus.CURRENT,
        )

        self.assertEqual(evaluate_ppe_status(ppe_record, today=date(2026, 4, 10)), PpeStatus.WARNING)


if __name__ == "__main__":
    unittest.main()
