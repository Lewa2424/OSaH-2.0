import unittest

from osah.domain.entities.nav_fill_segment_kind import NavFillSegmentKind
from osah.domain.entities.section_nav_fill_buckets import SectionNavFillBuckets
from osah.domain.services.allocate_nav_fill_segments import allocate_nav_fill_segments
from osah.domain.services.build_nav_fill_palette import build_nav_fill_palette
from osah.domain.services.build_section_nav_fill_buckets import build_dashboard_nav_fill_buckets
from osah.domain.services.nav_fill_constants import MIN_PROBLEM_SHARE, SEGMENT_COUNT


class BuildNavFillPaletteTests(unittest.TestCase):
    """Тести діаграми nav-кнопок / Nav-button diagram tests."""

    # ###### FLOOR 20% ПРИ 1 КРИТИЧНОМУ / 20% FLOOR WITH 1 CRITICAL ######
    def test_floor_applies_for_single_critical_record(self) -> None:
        buckets = SectionNavFillBuckets(total=1000, critical=1, warning=0, restricted=0, ok=999)
        segments = allocate_nav_fill_segments(buckets)
        min_problem_segments = int(SEGMENT_COUNT * MIN_PROBLEM_SHARE)

        self.assertEqual(len(segments), SEGMENT_COUNT)
        self.assertTrue(all(kind == NavFillSegmentKind.CRITICAL for kind in segments[:min_problem_segments]))

    # ###### ПЕРШІ 20% КРАСНІ ПРИ КРИТИЦІ Й УВАЗІ / FIRST 20% RED WHEN CRITICAL AND WARNING ######
    def test_both_problem_levels_reserve_critical_floor(self) -> None:
        buckets = SectionNavFillBuckets(total=100, critical=10, warning=5, restricted=0, ok=85)
        segments = allocate_nav_fill_segments(buckets)
        min_problem_segments = int(SEGMENT_COUNT * MIN_PROBLEM_SHARE)

        self.assertTrue(all(kind == NavFillSegmentKind.CRITICAL for kind in segments[:min_problem_segments]))
        self.assertIn(NavFillSegmentKind.WARNING, segments[min_problem_segments:])

    # ###### ПОРЯДОК КАТЕГОРІЙ МЕДИЦИНИ / MEDICAL CATEGORY ORDER ######
    def test_medical_segments_follow_category_order(self) -> None:
        buckets = SectionNavFillBuckets(total=48, critical=42, warning=5, restricted=0, ok=1)
        segments = allocate_nav_fill_segments(buckets)

        first_warning_index = segments.index(NavFillSegmentKind.WARNING)
        first_ok_index = segments.index(NavFillSegmentKind.OK)
        self.assertLess(first_warning_index, first_ok_index)
        self.assertTrue(all(kind == NavFillSegmentKind.CRITICAL for kind in segments[:first_warning_index]))

    # ###### ІНСТРУКТАЖІ 76/0/27 / TRAININGS 76/0/27 ######
    def test_trainings_distribution_matches_expected_counts(self) -> None:
        buckets = SectionNavFillBuckets(total=103, critical=76, warning=0, restricted=0, ok=27)
        segments = allocate_nav_fill_segments(buckets)

        self.assertEqual(len(segments), SEGMENT_COUNT)
        self.assertEqual(segments.count(NavFillSegmentKind.CRITICAL), 95)
        self.assertEqual(segments.count(NavFillSegmentKind.WARNING), 0)
        self.assertEqual(segments.count(NavFillSegmentKind.OK), 25)

    # ###### TOTAL=0 / ZERO TOTAL ######
    def test_zero_total_returns_neutral_segments(self) -> None:
        buckets = SectionNavFillBuckets(total=0, critical=0, warning=0, restricted=0, ok=0)
        palette = build_nav_fill_palette(buckets)

        self.assertEqual(len(palette.colors), SEGMENT_COUNT)
        self.assertTrue(all(kind == NavFillSegmentKind.NEUTRAL for kind in allocate_nav_fill_segments(buckets)))

    # ###### УНІКАЛЬНІ ВІДТІНКИ В ЗОНІ / UNIQUE SHADES IN ZONE ######
    def test_palette_has_unique_colors_inside_non_trivial_zone(self) -> None:
        buckets = SectionNavFillBuckets(total=103, critical=76, warning=0, restricted=0, ok=27)
        palette = build_nav_fill_palette(buckets)

        self.assertEqual(len(palette.colors), SEGMENT_COUNT)
        self.assertEqual(len(set(palette.colors[:95])), 95)

    # ###### АГРЕГАТ ГОЛОВНОЇ / DASHBOARD AGGREGATE ######
    def test_dashboard_aggregate_sums_module_buckets(self) -> None:
        training = SectionNavFillBuckets(total=10, critical=4, warning=1, restricted=0, ok=5)
        ppe = SectionNavFillBuckets(total=20, critical=8, warning=2, restricted=0, ok=10)
        medical = SectionNavFillBuckets(total=30, critical=6, warning=3, restricted=1, ok=20)
        work_permits = SectionNavFillBuckets(total=12, critical=5, warning=1, restricted=0, ok=6)

        dashboard = build_dashboard_nav_fill_buckets(training, ppe, medical, work_permits)

        self.assertEqual(dashboard.total, 72)
        self.assertEqual(dashboard.critical, 23)
        self.assertEqual(dashboard.warning, 7)
        self.assertEqual(dashboard.restricted, 1)
        self.assertEqual(dashboard.ok, 41)


if __name__ == "__main__":
    unittest.main()
