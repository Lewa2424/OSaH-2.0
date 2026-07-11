import unittest

from osah.domain.services.format_employee_audit_event_label import format_employee_audit_event_label


class FormatEmployeeAuditEventLabelTests(unittest.TestCase):
    """Тести локалізації назв audit-подій працівника.
    Tests for employee audit event label localization.
    """

    def test_returns_known_event_labels(self) -> None:
        self.assertEqual(format_employee_audit_event_label("employee.updated"), "Картку оновлено")
        self.assertEqual(format_employee_audit_event_label("training.created"), "Інструктаж створено")
        self.assertEqual(format_employee_audit_event_label("work_permit.closed"), "Наряд закрито")

    def test_returns_raw_event_type_as_fallback(self) -> None:
        self.assertEqual(format_employee_audit_event_label("custom.event"), "custom.event")
        self.assertEqual(format_employee_audit_event_label(""), "Подія")


if __name__ == "__main__":
    unittest.main()
