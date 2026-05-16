import unittest

from osah.domain.entities.work_permit_record import WorkPermitRecord
from osah.domain.entities.work_permit_status import WorkPermitStatus
from osah.ui.qt.screens.work_permits.build_work_permit_extension_summary import build_work_permit_extension_summary


class BuildWorkPermitExtensionSummaryTests(unittest.TestCase):
    """Тести текстового стану продовження наряду для Qt.
    Tests for Qt-oriented work permit extension summary state.
    """

    def test_summary_for_new_record_keeps_dates_editable_and_extension_disabled(self) -> None:
        summary = build_work_permit_extension_summary(None)

        self.assertFalse(summary["can_extend"])
        self.assertFalse(summary["lock_dates"])
        self.assertIn("після збереження", str(summary["state_text"]).lower())

    def test_summary_for_active_record_allows_single_extension(self) -> None:
        record = WorkPermitRecord(
            record_id=1,
            permit_number="ND-01",
            work_kind="Вогневі роботи",
            work_location="Дільниця А",
            starts_at="2099-04-10 08:00",
            ends_at="2099-04-20 18:00",
            base_ends_at="2099-04-20 18:00",
            responsible_person="Майстер",
            issuer_person="Інспектор",
            note_text="",
            closed_at=None,
            participants=(),
            status=WorkPermitStatus.ACTIVE,
        )

        summary = build_work_permit_extension_summary(record)

        self.assertTrue(summary["can_extend"])
        self.assertTrue(summary["lock_dates"])
        self.assertIn("одноразове продовження", str(summary["state_text"]).lower())

    def test_summary_for_extended_record_shows_reason_and_blocks_second_extension(self) -> None:
        record = WorkPermitRecord(
            record_id=2,
            permit_number="ND-02",
            work_kind="Вогневі роботи",
            work_location="Дільниця Б",
            starts_at="2099-04-10 08:00",
            ends_at="2099-05-05 18:00",
            base_ends_at="2099-04-20 18:00",
            responsible_person="Майстер",
            issuer_person="Інспектор",
            note_text="",
            closed_at=None,
            participants=(),
            status=WorkPermitStatus.ACTIVE,
            extension_count=1,
            extended_at="2099-04-19 09:30",
            extension_reason_text="Роботи тривають без зміни заходів",
        )

        summary = build_work_permit_extension_summary(record)

        self.assertFalse(summary["can_extend"])
        self.assertTrue(summary["lock_dates"])
        self.assertIn("вже продовжено", str(summary["state_text"]).lower())
        self.assertIn("Роботи тривають", str(summary["reason_text"]))


    def test_summary_for_expired_record_allows_extension(self) -> None:
        record = WorkPermitRecord(
            record_id=3,
            permit_number="ND-03",
            work_kind="Р’РѕРіРЅРµРІС– СЂРѕР±РѕС‚Рё",
            work_location="Р”С–Р»СЊРЅРёС†СЏ Р’",
            starts_at="2099-04-10 08:00",
            ends_at="2099-04-20 18:00",
            base_ends_at="2099-04-20 18:00",
            responsible_person="РњР°Р№СЃС‚РµСЂ",
            issuer_person="Р†РЅСЃРїРµРєС‚РѕСЂ",
            note_text="",
            closed_at=None,
            participants=(),
            status=WorkPermitStatus.EXPIRED,
        )

        summary = build_work_permit_extension_summary(record)

        self.assertTrue(summary["can_extend"])


if __name__ == "__main__":
    unittest.main()
