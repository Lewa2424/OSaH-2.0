import unittest

from osah.domain.entities.port_passport_risk_status import PortPassportRiskStatus
from osah.domain.entities.port_passport_status import PortPassportStatus
from osah.domain.entities.port_risk_level import PortRiskLevel
from osah.domain.entities.port_risk_profile import PortRiskProfile
from osah.domain.entities.port_site_passport_input import PortSitePassportInput
from osah.domain.entities.port_site_passport_row import PortSitePassportRow
from osah.domain.entities.port_site_risk import PortSiteRisk
from osah.domain.services.build_port_shift_briefing import build_port_shift_briefing


class BuildPortShiftBriefingTests(unittest.TestCase):
    """Тести зборки даних оперативного листа зміни ПОРТ-Р.
    Tests for assembling the PORT-R shift briefing data.
    """

    def test_briefing_picks_active_risks_and_skips_rejected(self) -> None:
        """Беремо тільки прийняті/ручні ризики у ключові пункти листа.
        Picks only accepted/manual risks into the briefing key risks.
        """

        passport_row = _make_passport_row(final_profile=PortRiskProfile.HIGH)
        passport_input = _make_passport_input()
        risks = (
            _make_risk(1, "Падіння вантажу", "Кран", PortRiskLevel.HIGH, PortPassportRiskStatus.ACCEPTED, 1),
            _make_risk(2, "Старий ризик", "Пристрій", PortRiskLevel.LOW, PortPassportRiskStatus.REJECTED, 2),
            _make_risk(3, "Ручний ризик", "Стропа", PortRiskLevel.CRITICAL, PortPassportRiskStatus.MANUAL, 3),
            _make_risk(4, "Пропозиція", "Інший", PortRiskLevel.MEDIUM, PortPassportRiskStatus.SUGGESTED, 4),
        )

        briefing = build_port_shift_briefing(passport_row, passport_input, risks)

        self.assertEqual(len(briefing.key_risks), 2)
        self.assertEqual(briefing.key_risks[0].risk_situation, "Ручний ризик")
        self.assertEqual(briefing.key_risks[0].level, PortRiskLevel.CRITICAL)
        self.assertEqual(briefing.key_risks[1].risk_situation, "Падіння вантажу")
        self.assertEqual(briefing.key_risks[1].level, PortRiskLevel.HIGH)

    def test_briefing_limits_key_risks_to_five(self) -> None:
        """Обмежуємо ключові ризики п'ятьма пунктами.
        Limits key risks to five items.
        """

        passport_row = _make_passport_row()
        passport_input = _make_passport_input()
        risks = tuple(
            _make_risk(index, f"Ризик {index}", "Джерело", PortRiskLevel.HIGH, PortPassportRiskStatus.ACCEPTED, index)
            for index in range(1, 9)
        )

        briefing = build_port_shift_briefing(passport_row, passport_input, risks)

        self.assertEqual(len(briefing.key_risks), 5)

    def test_briefing_builds_seven_barriers(self) -> None:
        """Збираємо сім стандартних бар'єрів з паспорта (стан вказує лінійний керівник).
        Builds seven standard barriers from the passport (state is filled by the line manager).
        """

        passport_row = _make_passport_row()
        passport_input = _make_passport_input(
            communication_barrier="радіо",
            ppe_text="каска, жилет",
        )

        briefing = build_port_shift_briefing(passport_row, passport_input, ())

        self.assertEqual(len(briefing.barriers), 7)
        barrier_names = tuple(barrier.name for barrier in briefing.barriers)
        self.assertEqual(
            barrier_names,
            (
                "Зв'язок",
                "Огородження / зонування",
                "Сигнальник",
                "Освітлення",
                "ЗІЗ",
                "ВЗП / стропи / захвати",
                "Проходи / проїзди",
            ),
        )
        self.assertEqual(briefing.barriers[0].comment, "радіо")
        self.assertEqual(briefing.barriers[4].comment, "каска, жилет")


def _make_passport_row(
    final_profile: PortRiskProfile = PortRiskProfile.MEDIUM,
) -> PortSitePassportRow:
    return PortSitePassportRow(
        passport_id=10,
        passport_code="P-001",
        site_name="Причал №1",
        site_type="ВРР",
        calculated_profile=final_profile,
        final_profile=final_profile,
        status=PortPassportStatus.ACTIVE,
        updated_at="2026-05-28 10:00:00",
    )


def _make_passport_input(**overrides: object) -> PortSitePassportInput:
    defaults: dict[str, object] = dict(
        passport_code="P-001",
        site_name="Причал №1",
        site_type="ВРР",
        site_location="Одеса",
        site_description="",
        work_kind="ВРР",
        typical_operations="стропування",
        work_mode="одна зміна",
        typical_cargo="метал",
        cargo_features="",
        main_equipment="кран",
        lifting_devices="стропи",
        has_railway_zone=False,
        has_auto_zone=True,
        has_crane_zone=True,
        crew_composition="бригада",
        responsible_person="майстер",
        has_contractors=False,
        contractors_note="",
        zone_kind="відкритий причал",
        has_night_works=False,
        weather_features="",
        has_limited_visibility=False,
        has_height_work=False,
        has_water_edge_work=False,
        has_stack_edge_work=False,
        has_communication_barrier=False,
        communication_barrier="",
        has_fencing_barrier=False,
        fencing_barrier="",
        has_signalman=False,
        has_lighting_barrier=True,
        lighting_barrier="прожектори",
        ppe_text="каска, жилет",
        additional_barriers="",
    )
    defaults.update(overrides)
    return PortSitePassportInput(**defaults)  # type: ignore[arg-type]


def _make_risk(
    risk_id: int,
    risk_situation: str,
    hazard_source: str,
    level: PortRiskLevel,
    status: PortPassportRiskStatus,
    sort_order: int,
) -> PortSiteRisk:
    return PortSiteRisk(
        risk_id=risk_id,
        passport_id=10,
        registry_risk_id=None,
        risk_situation=risk_situation,
        hazard_source=hazard_source,
        occurrence_conditions="",
        consequences="",
        assessment_reason="",
        risk_level=level.value,
        method_note="",
        inspector_comment="",
        suggestion_reason="",
        status=status,
        addition_source="manual",
        sort_order=sort_order,
    )


if __name__ == "__main__":
    unittest.main()
