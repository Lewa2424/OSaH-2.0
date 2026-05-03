import unittest
from datetime import date

from osah.domain.entities.training_next_control_basis import TrainingNextControlBasis
from osah.domain.entities.training_person_category import TrainingPersonCategory
from osah.domain.entities.training_type import TrainingType
from osah.domain.entities.training_work_risk_category import TrainingWorkRiskCategory
from osah.domain.services.resolve_training_next_control_date import resolve_training_next_control_date


class ResolveTrainingNextControlDateTests(unittest.TestCase):
    """Тесты определения следующей контрольной даты инструктажа.
    Tests for resolving the next training control date.
    """

    def test_primary_regular_work_calculates_six_months(self) -> None:
        """Проверяет расчёт повторного инструктажа для обычных работ.
        Checks repeated training calculation for regular work.
        """

        next_date, basis, risk = resolve_training_next_control_date(
            TrainingType.PRIMARY,
            date(2026, 4, 10),
            TrainingPersonCategory.OWN_EMPLOYEE,
            True,
            TrainingWorkRiskCategory.REGULAR,
            None,
            True,
            False,
        )

        self.assertEqual(next_date, "2026-10-10")
        self.assertEqual(basis, TrainingNextControlBasis.CALCULATED_AFTER_PRIMARY_6M)
        self.assertEqual(risk, TrainingWorkRiskCategory.REGULAR)

    def test_repeated_high_risk_work_calculates_three_months(self) -> None:
        """Проверяет расчёт повторного инструктажа для работ повышенной опасности.
        Checks repeated training calculation for high-risk work.
        """

        next_date, basis, risk = resolve_training_next_control_date(
            TrainingType.REPEATED,
            date(2026, 4, 10),
            TrainingPersonCategory.OWN_EMPLOYEE,
            True,
            TrainingWorkRiskCategory.HIGH_RISK,
            None,
            True,
            False,
        )

        self.assertEqual(next_date, "2026-07-10")
        self.assertEqual(basis, TrainingNextControlBasis.CALCULATED_AFTER_REPEATED_3M)
        self.assertEqual(risk, TrainingWorkRiskCategory.HIGH_RISK)

    def test_introductory_for_own_employee_can_require_primary(self) -> None:
        """Проверяет требование первичного после вводного для своего сотрудника.
        Checks the primary-training requirement after introductory training for an own employee.
        """

        next_date, basis, risk = resolve_training_next_control_date(
            TrainingType.INTRODUCTORY,
            date(2026, 4, 10),
            TrainingPersonCategory.OWN_EMPLOYEE,
            True,
            TrainingWorkRiskCategory.NOT_APPLICABLE,
            None,
            False,
            False,
        )

        self.assertEqual(next_date, "2026-04-10")
        self.assertEqual(basis, TrainingNextControlBasis.REQUIRES_PRIMARY_AFTER_INTRODUCTORY)
        self.assertEqual(risk, TrainingWorkRiskCategory.NOT_APPLICABLE)

    def test_introductory_for_contractor_can_skip_primary(self) -> None:
        """Проверяет вводный подрядчика без автоматического требования первичного.
        Checks contractor introductory training without automatic primary requirement.
        """

        next_date, basis, risk = resolve_training_next_control_date(
            TrainingType.INTRODUCTORY,
            date(2026, 4, 10),
            TrainingPersonCategory.CONTRACTOR,
            False,
            TrainingWorkRiskCategory.NOT_APPLICABLE,
            None,
            False,
            False,
        )

        self.assertEqual(next_date, "")
        self.assertEqual(basis, TrainingNextControlBasis.INTRODUCTORY_PRIMARY_NOT_REQUIRED)
        self.assertEqual(risk, TrainingWorkRiskCategory.NOT_APPLICABLE)

    def test_unscheduled_without_transfer_does_not_change_repeated_control(self) -> None:
        """Проверяет, что внеплановый без ручного переноса не создаёт контрольную дату.
        Checks that unscheduled training without transfer does not create a control date.
        """

        next_date, basis, risk = resolve_training_next_control_date(
            TrainingType.UNSCHEDULED,
            date(2026, 4, 10),
            TrainingPersonCategory.OWN_EMPLOYEE,
            True,
            TrainingWorkRiskCategory.NOT_APPLICABLE,
            None,
            False,
            False,
        )

        self.assertEqual(next_date, "")
        self.assertEqual(basis, TrainingNextControlBasis.DOES_NOT_CHANGE_REPEATED_CONTROL)
        self.assertEqual(risk, TrainingWorkRiskCategory.NOT_APPLICABLE)


if __name__ == "__main__":
    unittest.main()
