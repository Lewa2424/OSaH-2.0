import unittest

from osah.domain.entities.work_permit_daily_check import WorkPermitDailyCheck
from osah.domain.entities.work_permit_record import WorkPermitRecord
from osah.domain.entities.work_permit_status import WorkPermitStatus
from osah.domain.services.build_work_permit_daily_check_summary import build_work_permit_daily_check_summary


class BuildWorkPermitDailyCheckSummaryTests(unittest.TestCase):
    """Тести Qt-сводки щоденних перевірок наряду-допуску.
    Tests for the Qt daily-check summary of work permits.
    """

    def test_summary_for_new_record_disables_daily_checks(self) -> None:
        summary = build_work_permit_daily_check_summary(None)

        self.assertFalse(summary["can_record"])
        self.assertIn("після збереження", str(summary["requirement_text"]).lower())

    def test_summary_for_single_day_record_marks_daily_checks_as_not_required(self) -> None:
        record = WorkPermitRecord(
            record_id=1,
            permit_number="ND-SUM-001",
            work_kind="Вогневі роботи",
            work_location="Дільниця А",
            starts_at="2099-04-10 08:00",
            ends_at="2099-04-10 18:00",
            responsible_person="Майстер",
            issuer_person="Інспектор",
            note_text="",
            closed_at=None,
            participants=(),
            status=WorkPermitStatus.ACTIVE,
        )

        summary = build_work_permit_daily_check_summary(record)

        self.assertFalse(summary["can_record"])
        self.assertIn("одноденного", str(summary["requirement_text"]).lower())

    def test_summary_for_multiday_record_shows_latest_check(self) -> None:
        record = WorkPermitRecord(
            record_id=2,
            permit_number="ND-SUM-002",
            work_kind="Вогневі роботи",
            work_location="Дільниця Б",
            starts_at="2099-04-10 08:00",
            ends_at="2099-04-12 18:00",
            responsible_person="Майстер",
            issuer_person="Інспектор",
            note_text="",
            closed_at=None,
            participants=(),
            status=WorkPermitStatus.ACTIVE,
            daily_checks=(
                WorkPermitDailyCheck(
                    check_id=1,
                    checked_at="2099-04-11 09:30",
                    checked_by="Старший майстер",
                    note_text="Перевірено",
                ),
            ),
        )

        summary = build_work_permit_daily_check_summary(record)

        self.assertTrue(summary["can_record"])
        self.assertIn("щодня", str(summary["requirement_text"]).lower())
        self.assertIn("Старший майстер", str(summary["last_check_text"]))
