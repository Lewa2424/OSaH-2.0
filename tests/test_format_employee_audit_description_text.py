import unittest

from osah.domain.services.format_employee_audit_description_text import (
    build_employee_audit_summary_text,
    format_employee_audit_description_text,
)


class FormatEmployeeAuditDescriptionTextTests(unittest.TestCase):
    """Тести форматування audit-описів для картки працівника.
    Tests for employee audit description formatting.
    """

    def test_formats_employee_card_key_value_description(self) -> None:
        formatted_text = format_employee_audit_description_text(
            "full_name=Бондар Андрій Миколайович;department=Енергетична служба;"
            "position=Електромонтер;status=active;photo=set"
        )

        self.assertIn("• ПІБ: Бондар Андрій Миколайович", formatted_text)
        self.assertIn("• Підрозділ: Енергетична служба", formatted_text)
        self.assertIn("• Посада: Електромонтер", formatted_text)
        self.assertIn("• Статус: активний", formatted_text)
        self.assertIn("• Фото: додано", formatted_text)

    def test_formats_old_and_new_sections(self) -> None:
        formatted_text = format_employee_audit_description_text(
            "old=(id=1; type=Первинний; event_date=2026-01-01) "
            "new=(id=1; type=Первинний; event_date=2026-02-01)"
        )

        self.assertIn("Зміни:", formatted_text)
        self.assertIn("Дата проведення: 2026-01-01 → 2026-02-01", formatted_text)

    def test_build_summary_uses_first_formatted_line(self) -> None:
        summary = build_employee_audit_summary_text(
            "full_name=Тест Тестович;department=Цех;position=Слюсар;status=active;photo=none"
        )

        self.assertTrue(summary.startswith("• ПІБ:"))

    def test_hides_internal_work_permit_fields(self) -> None:
        formatted_text = format_employee_audit_description_text(
            "before=(permit_number=26-05-ЗЕР;work_kind=Земляні роботи;starts_at=2026-05-20 08:00;"
            "ends_at=2026-05-20 20:00;base_ends_at=2026-05-20 20:00;extension_count=0;extended_at=;"
            "reissued_from_record_id=;target_training_status=done_passed;"
            "participants=0041:executor,0052:team_member);closed_at=2026-06-10 10:34:36"
        )

        self.assertIn("№ наряду: 26-05-ЗЕР", formatted_text)
        self.assertIn("Виконавець", formatted_text)
        self.assertIn("перевірка знань пройдена", formatted_text)
        self.assertNotIn("base_ends_at", formatted_text)
        self.assertNotIn("extension_count", formatted_text)
        self.assertNotIn("reissued_from_record_id", formatted_text)
        self.assertNotIn("0041:executor", formatted_text)

    def test_formats_before_after_diff_only_for_changed_fields(self) -> None:
        formatted_text = format_employee_audit_description_text(
            "before=(permit_number=26-05-ЗЕР;work_kind=Земляні роботи;ends_at=2026-05-20 20:00);"
            "after=(permit_number=26-05-ЗЕР;work_kind=Земляні роботи;ends_at=2026-05-21 20:00)"
        )

        self.assertIn("Зміни:", formatted_text)
        self.assertIn("Завершення: 2026-05-20 20:00 → 2026-05-21 20:00", formatted_text)
        self.assertNotIn("№ наряду", formatted_text)


if __name__ == "__main__":
    unittest.main()
