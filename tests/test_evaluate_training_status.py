import unittest
from datetime import date

from osah.domain.entities.training_record import TrainingRecord
from osah.domain.entities.training_next_control_basis import TrainingNextControlBasis
from osah.domain.entities.training_status import TrainingStatus
from osah.domain.entities.training_type import TrainingType
from osah.domain.services.evaluate_training_status import evaluate_training_status


class EvaluateTrainingStatusTests(unittest.TestCase):
    """Тести оцінки статусу інструктажу.
    Тесты оценки статуса инструктажа.
    """

    # ###### ПЕРЕВІРКА СТАТУСУ УВАГИ / ПРОВЕРКА СТАТУСА ВНИМАНИЯ ######
    def test_evaluate_training_status_returns_warning_before_deadline(self) -> None:
        """Перевіряє перехід у статус уваги перед строком контролю.
        Проверяет переход в статус внимания перед сроком контроля.
        """

        training_record = TrainingRecord(
            record_id=1,
            employee_personnel_number="0001",
            employee_full_name="Працівник",
            training_type=TrainingType.REPEATED,
            event_date="2026-04-01",
            next_control_date="2026-04-20",
            conducted_by="Інспектор",
            note_text="",
            status=TrainingStatus.CURRENT,
        )

        status = evaluate_training_status(training_record, today=date(2026, 4, 10), warning_days=30)

        self.assertEqual(status, TrainingStatus.WARNING)

    # ###### ПЕРЕВІРКА ПРОСТРОЧЕННЯ / ПРОВЕРКА ПРОСРОЧКИ ######
    def test_evaluate_training_status_returns_overdue_after_deadline(self) -> None:
        """Перевіряє перехід у прострочений статус після строку контролю.
        Проверяет переход в просроченный статус после срока контроля.
        """

        training_record = TrainingRecord(
            record_id=1,
            employee_personnel_number="0001",
            employee_full_name="Працівник",
            training_type=TrainingType.PRIMARY,
            event_date="2026-03-01",
            next_control_date="2026-03-31",
            conducted_by="Інспектор",
            note_text="",
            status=TrainingStatus.CURRENT,
        )

        status = evaluate_training_status(training_record, today=date(2026, 4, 10), warning_days=30)

        self.assertEqual(status, TrainingStatus.OVERDUE)

    def test_evaluate_training_status_returns_current_for_non_control_record(self) -> None:
        """Перевіряє нейтральний статус запису без переносу повторного інструктажу.
        Checks neutral status for a record that does not transfer repeated training.
        """

        training_record = TrainingRecord(
            record_id=1,
            employee_personnel_number="0001",
            employee_full_name="Працівник",
            training_type=TrainingType.UNSCHEDULED,
            event_date="2026-03-01",
            next_control_date="",
            conducted_by="Інспектор",
            note_text="",
            status=TrainingStatus.CURRENT,
            next_control_basis=TrainingNextControlBasis.DOES_NOT_CHANGE_REPEATED_CONTROL,
        )

        status = evaluate_training_status(training_record, today=date(2026, 4, 10), warning_days=30)

        self.assertEqual(status, TrainingStatus.CURRENT)


if __name__ == "__main__":
    unittest.main()
