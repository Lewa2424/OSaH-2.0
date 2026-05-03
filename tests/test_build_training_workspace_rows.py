import unittest

from osah.domain.entities.employee import Employee
from osah.domain.entities.training_next_control_basis import TrainingNextControlBasis
from osah.domain.entities.training_person_category import TrainingPersonCategory
from osah.domain.entities.training_record import TrainingRecord
from osah.domain.entities.training_registry_filter import TrainingRegistryFilter
from osah.domain.entities.training_status import TrainingStatus
from osah.domain.entities.training_type import TrainingType
from osah.domain.entities.training_work_risk_category import TrainingWorkRiskCategory
from osah.domain.services.build_training_workspace_rows import build_training_workspace_rows


class BuildTrainingWorkspaceRowsTests(unittest.TestCase):
    """Тесты построения строк рабочего пространства инструктажей.
    Tests for building trainings workspace rows.
    """

    def test_active_employee_without_records_gets_missing_primary_row(self) -> None:
        """Проверяет, что активный сотрудник без записей получает проблему по первичному.
        Checks that an active employee without records gets a missing-primary problem row.
        """

        employee = Employee(
            personnel_number="0001",
            full_name="Працівник",
            position_name="Слюсар",
            department_name="Цех",
            employment_status="active",
        )

        rows = build_training_workspace_rows((employee,), ())

        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0].status_filter, TrainingRegistryFilter.MISSING)
        self.assertEqual(rows[0].training_type, TrainingType.PRIMARY)

    def test_targeted_training_without_primary_keeps_missing_primary_problem(self) -> None:
        """Проверяет, что целевой инструктаж не закрывает отсутствие первичного.
        Checks that targeted training does not close a missing primary requirement.
        """

        employee = Employee(
            personnel_number="0001",
            full_name="Працівник",
            position_name="Слюсар",
            department_name="Цех",
            employment_status="active",
        )
        targeted_record = TrainingRecord(
            record_id=1,
            employee_personnel_number="0001",
            employee_full_name="Працівник",
            training_type=TrainingType.TARGETED,
            event_date="2026-04-10",
            next_control_date="",
            conducted_by="Інспектор",
            note_text="",
            status=TrainingStatus.CURRENT,
            person_category=TrainingPersonCategory.OWN_EMPLOYEE,
            requires_primary_on_workplace=True,
            work_risk_category=TrainingWorkRiskCategory.NOT_APPLICABLE,
            next_control_basis=TrainingNextControlBasis.DOES_NOT_CHANGE_REPEATED_CONTROL,
        )

        rows = build_training_workspace_rows((employee,), (targeted_record,))

        self.assertTrue(any(row.status_filter == TrainingRegistryFilter.MISSING for row in rows))

    def test_contractor_introductory_without_primary_requirement_does_not_create_missing_row(self) -> None:
        """Проверяет, что подрядчик без требования первичного не получает ложный missing.
        Checks that a contractor without a primary requirement does not get a false missing row.
        """

        employee = Employee(
            personnel_number="0001",
            full_name="Підрядник",
            position_name="Представник",
            department_name="Підрядні роботи",
            employment_status="active",
        )
        introductory_record = TrainingRecord(
            record_id=1,
            employee_personnel_number="0001",
            employee_full_name="Підрядник",
            training_type=TrainingType.INTRODUCTORY,
            event_date="2026-04-10",
            next_control_date="",
            conducted_by="Інспектор",
            note_text="",
            status=TrainingStatus.NOT_REQUIRED,
            person_category=TrainingPersonCategory.CONTRACTOR,
            requires_primary_on_workplace=False,
            work_risk_category=TrainingWorkRiskCategory.NOT_APPLICABLE,
            next_control_basis=TrainingNextControlBasis.INTRODUCTORY_PRIMARY_NOT_REQUIRED,
        )

        rows = build_training_workspace_rows((employee,), (introductory_record,))

        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0].status_filter, TrainingRegistryFilter.CURRENT)
        self.assertIn("не потрібен", rows[0].status_reason.lower())


if __name__ == "__main__":
    unittest.main()
