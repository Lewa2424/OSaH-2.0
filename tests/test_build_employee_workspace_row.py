import unittest

from osah.domain.entities.employee import Employee
from osah.domain.entities.employee_status_level import EmployeeStatusLevel
from osah.domain.entities.training_next_control_basis import TrainingNextControlBasis
from osah.domain.entities.training_person_category import TrainingPersonCategory
from osah.domain.entities.training_record import TrainingRecord
from osah.domain.entities.training_status import TrainingStatus
from osah.domain.entities.training_type import TrainingType
from osah.domain.entities.training_work_risk_category import TrainingWorkRiskCategory
from osah.domain.services.build_employee_workspace_row import build_employee_workspace_row


class BuildEmployeeWorkspaceRowTests(unittest.TestCase):
    """Тести узгодження статусу працівника з реєстром інструктажів.
    Tests that employee card status matches trainings registry logic.
    """

    def test_primary_closed_by_later_repeated_is_not_critical_in_employee_card(self) -> None:
        """Первинний не лишається критичним, якщо його цикл закрито повторним.
        Primary training is not left critical when a later repeated training closes the cycle.
        """

        employee = Employee(
            personnel_number="0001",
            full_name="Працівник",
            position_name="Слюсар",
            department_name="Цех",
            employment_status="active",
        )
        records = (
            TrainingRecord(
                record_id=1,
                employee_personnel_number="0001",
                employee_full_name="Працівник",
                training_type=TrainingType.INTRODUCTORY,
                event_date="2025-06-02",
                next_control_date="2025-06-02",
                conducted_by="Інспектор",
                note_text="",
                status=TrainingStatus.CLOSED_BY_PRIMARY,
                person_category=TrainingPersonCategory.OWN_EMPLOYEE,
                requires_primary_on_workplace=True,
                work_risk_category=TrainingWorkRiskCategory.NOT_APPLICABLE,
                next_control_basis=TrainingNextControlBasis.REQUIRES_PRIMARY_AFTER_INTRODUCTORY,
            ),
            TrainingRecord(
                record_id=2,
                employee_personnel_number="0001",
                employee_full_name="Працівник",
                training_type=TrainingType.PRIMARY,
                event_date="2025-06-04",
                next_control_date="2025-12-04",
                conducted_by="Інспектор",
                note_text="",
                status=TrainingStatus.OVERDUE,
                person_category=TrainingPersonCategory.OWN_EMPLOYEE,
                requires_primary_on_workplace=True,
                work_risk_category=TrainingWorkRiskCategory.REGULAR,
                next_control_basis=TrainingNextControlBasis.CALCULATED_AFTER_PRIMARY_6M,
            ),
            TrainingRecord(
                record_id=3,
                employee_personnel_number="0001",
                employee_full_name="Працівник",
                training_type=TrainingType.REPEATED,
                event_date="2025-07-04",
                next_control_date="2026-02-02",
                conducted_by="Інспектор",
                note_text="",
                status=TrainingStatus.CURRENT,
                person_category=TrainingPersonCategory.OWN_EMPLOYEE,
                requires_primary_on_workplace=True,
                work_risk_category=TrainingWorkRiskCategory.REGULAR,
                next_control_basis=TrainingNextControlBasis.CALCULATED_AFTER_REPEATED_6M,
            ),
        )

        row = build_employee_workspace_row(employee, records, (), (), ())

        self.assertEqual(row.module_summaries[0].level, EmployeeStatusLevel.NORMAL)
        self.assertEqual(row.module_summaries[0].reason, "актуально")


if __name__ == "__main__":
    unittest.main()
