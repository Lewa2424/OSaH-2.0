import unittest
from datetime import date

from osah.domain.entities.training_next_control_basis import TrainingNextControlBasis
from osah.domain.entities.training_person_category import TrainingPersonCategory
from osah.domain.entities.training_record import TrainingRecord
from osah.domain.entities.training_status import TrainingStatus
from osah.domain.entities.training_type import TrainingType
from osah.domain.entities.training_work_risk_category import TrainingWorkRiskCategory
from osah.domain.services.evaluate_training_status import evaluate_training_status


class EvaluateTrainingStatusTests(unittest.TestCase):
    """Тесты оценки статуса инструктажа.
    Tests for training status evaluation.
    """

    def test_warning_when_next_control_is_within_configured_threshold(self) -> None:
        """Проверяет статус WARNING при приближении повторного контроля.
        Checks WARNING status when repeated control is within the configured threshold.
        """

        training_record = TrainingRecord(
            record_id=1,
            employee_personnel_number="0001",
            employee_full_name="Працівник",
            training_type=TrainingType.REPEATED,
            event_date="2026-01-10",
            next_control_date="2026-04-20",
            conducted_by="Інспектор",
            note_text="",
            status=TrainingStatus.CURRENT,
            work_risk_category=TrainingWorkRiskCategory.REGULAR,
            next_control_basis=TrainingNextControlBasis.CALCULATED_AFTER_REPEATED_6M,
        )

        status = evaluate_training_status(training_record, today=date(2026, 4, 10), warning_days=10)

        self.assertEqual(status, TrainingStatus.WARNING)

    def test_overdue_when_next_control_date_has_passed(self) -> None:
        """Проверяет статус OVERDUE после даты повторного контроля.
        Checks OVERDUE status after the repeated-control date has passed.
        """

        training_record = TrainingRecord(
            record_id=1,
            employee_personnel_number="0001",
            employee_full_name="Працівник",
            training_type=TrainingType.REPEATED,
            event_date="2026-01-10",
            next_control_date="2026-04-05",
            conducted_by="Інспектор",
            note_text="",
            status=TrainingStatus.CURRENT,
            work_risk_category=TrainingWorkRiskCategory.REGULAR,
            next_control_basis=TrainingNextControlBasis.CALCULATED_AFTER_REPEATED_6M,
        )

        status = evaluate_training_status(training_record, today=date(2026, 4, 10), warning_days=30)

        self.assertEqual(status, TrainingStatus.OVERDUE)

    def test_introductory_without_required_primary_is_not_required(self) -> None:
        """Проверяет статус NOT_REQUIRED для вводного без требования первичного.
        Checks NOT_REQUIRED status for introductory training without a primary requirement.
        """

        training_record = TrainingRecord(
            record_id=1,
            employee_personnel_number="0001",
            employee_full_name="Підрядник",
            training_type=TrainingType.INTRODUCTORY,
            event_date="2026-04-10",
            next_control_date="",
            conducted_by="Інспектор",
            note_text="",
            status=TrainingStatus.CURRENT,
            person_category=TrainingPersonCategory.CONTRACTOR,
            requires_primary_on_workplace=False,
            work_risk_category=TrainingWorkRiskCategory.NOT_APPLICABLE,
            next_control_basis=TrainingNextControlBasis.INTRODUCTORY_PRIMARY_NOT_REQUIRED,
        )

        status = evaluate_training_status(training_record, today=date(2026, 4, 10), warning_days=30)

        self.assertEqual(status, TrainingStatus.NOT_REQUIRED)

    def test_introductory_requirement_is_closed_by_primary_after_it(self) -> None:
        """Проверяет закрытие требования вводного последующим первичным.
        Checks that an introductory requirement is closed by a later primary training.
        """

        introductory_record = TrainingRecord(
            record_id=1,
            employee_personnel_number="0001",
            employee_full_name="Працівник",
            training_type=TrainingType.INTRODUCTORY,
            event_date="2026-04-10",
            next_control_date="2026-04-10",
            conducted_by="Інспектор",
            note_text="",
            status=TrainingStatus.CURRENT,
            person_category=TrainingPersonCategory.OWN_EMPLOYEE,
            requires_primary_on_workplace=True,
            work_risk_category=TrainingWorkRiskCategory.NOT_APPLICABLE,
            next_control_basis=TrainingNextControlBasis.REQUIRES_PRIMARY_AFTER_INTRODUCTORY,
        )
        primary_record = TrainingRecord(
            record_id=2,
            employee_personnel_number="0001",
            employee_full_name="Працівник",
            training_type=TrainingType.PRIMARY,
            event_date="2026-04-11",
            next_control_date="2026-10-11",
            conducted_by="Інспектор",
            note_text="",
            status=TrainingStatus.CURRENT,
            person_category=TrainingPersonCategory.OWN_EMPLOYEE,
            requires_primary_on_workplace=True,
            work_risk_category=TrainingWorkRiskCategory.REGULAR,
            next_control_basis=TrainingNextControlBasis.CALCULATED_AFTER_PRIMARY_6M,
        )

        status = evaluate_training_status(
            introductory_record,
            related_training_records=(introductory_record, primary_record),
            today=date(2026, 4, 12),
            warning_days=30,
        )

        self.assertEqual(status, TrainingStatus.CLOSED_BY_PRIMARY)

    def test_non_control_record_without_transfer_stays_current(self) -> None:
        """Проверяет, что запись без переноса повторного контроля остаётся CURRENT.
        Checks that a record without repeated-control transfer stays CURRENT.
        """

        training_record = TrainingRecord(
            record_id=1,
            employee_personnel_number="0001",
            employee_full_name="Працівник",
            training_type=TrainingType.TARGETED,
            event_date="2026-04-10",
            next_control_date="",
            conducted_by="Інспектор",
            note_text="",
            status=TrainingStatus.CURRENT,
            work_risk_category=TrainingWorkRiskCategory.NOT_APPLICABLE,
            next_control_basis=TrainingNextControlBasis.DOES_NOT_CHANGE_REPEATED_CONTROL,
        )

        status = evaluate_training_status(training_record, today=date(2026, 4, 10), warning_days=30)

        self.assertEqual(status, TrainingStatus.CURRENT)


if __name__ == "__main__":
    unittest.main()
