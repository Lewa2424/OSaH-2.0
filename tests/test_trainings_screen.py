import unittest

from osah.domain.entities.training_registry_filter import TrainingRegistryFilter
from osah.domain.entities.training_workspace_row import TrainingWorkspaceRow
from osah.ui.qt.screens.trainings.trainings_screen import _collapse_by_employee


class TrainingsScreenCollapseTests(unittest.TestCase):
    """Тести стислого режиму перегляду інструктажів за працівниками.
    Tests for compact employee-oriented trainings view.
    """

    def test_collapse_by_employee_builds_one_summary_row_with_problem_list(self) -> None:
        """Повертає один рядок на працівника зі стислим переліком проблем.
        Returns one row per employee with a compact list of issues.
        """

        rows = (
            TrainingWorkspaceRow(
                record_id=None,
                employee_personnel_number="0001",
                employee_full_name="Іваненко Іван",
                department_name="Цех",
                site_name="Цех",
                position_name="Слюсар",
                training_type=None,
                training_type_label="Первинний",
                event_date="-",
                next_control_date="Потрібен",
                status_filter=TrainingRegistryFilter.MISSING,
                status_label="Відсутній",
                status_reason="Не зафіксовано первинний інструктаж.",
                conducted_by="-",
                note_text="",
                is_missing=True,
            ),
            TrainingWorkspaceRow(
                record_id=2,
                employee_personnel_number="0001",
                employee_full_name="Іваненко Іван",
                department_name="Цех",
                site_name="Цех",
                position_name="Слюсар",
                training_type=None,
                training_type_label="Повторний",
                event_date="2025-07-04",
                next_control_date="2026-02-02",
                status_filter=TrainingRegistryFilter.WARNING,
                status_label="Увага",
                status_reason="Увага - через 3 дн. спливає строк повторного інструктажу",
                conducted_by="Інспектор",
                note_text="",
                is_missing=False,
            ),
        )

        collapsed = _collapse_by_employee(rows)

        self.assertEqual(len(collapsed), 1)
        self.assertEqual(collapsed[0].training_type_label, "Стан працівника")
        self.assertEqual(collapsed[0].status_filter, TrainingRegistryFilter.MISSING)
        self.assertIn("первинний", collapsed[0].status_reason.lower())
        self.assertIn("повторний", collapsed[0].status_reason.lower())


if __name__ == "__main__":
    unittest.main()
