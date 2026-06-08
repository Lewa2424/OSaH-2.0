from osah.domain.entities.nav_fill_palette import NavFillPalette
from osah.domain.entities.nav_fill_segment_kind import NavFillSegmentKind
from osah.domain.entities.section_nav_fill_buckets import SectionNavFillBuckets
from osah.domain.services.allocate_nav_fill_segments import allocate_nav_fill_segments
from osah.domain.services.interpolate_hex_colors import interpolate_hex_colors
from osah.domain.services.nav_fill_constants import NAV_FILL_COLORS, SEGMENT_COUNT

_KIND_COLORS: dict[NavFillSegmentKind, tuple[str, str]] = {
    NavFillSegmentKind.CRITICAL: (NAV_FILL_COLORS["critical_dark"], NAV_FILL_COLORS["critical_light"]),
    NavFillSegmentKind.WARNING: (NAV_FILL_COLORS["warning_dark"], NAV_FILL_COLORS["warning_light"]),
    NavFillSegmentKind.RESTRICTED: (NAV_FILL_COLORS["restricted_dark"], NAV_FILL_COLORS["restricted_light"]),
    NavFillSegmentKind.OK: (NAV_FILL_COLORS["ok_dark"], NAV_FILL_COLORS["ok_light"]),
    NavFillSegmentKind.NEUTRAL: (NAV_FILL_COLORS["neutral_dark"], NAV_FILL_COLORS["neutral_light"]),
}


# ###### ПАЛІТРА NAV-ДІАГРАМИ / NAV DIAGRAM PALETTE ######
def build_nav_fill_palette(buckets: SectionNavFillBuckets) -> NavFillPalette:
    """Будує 120 гармонійних відтінків для nav-діаграми.
    Builds 120 harmonious shades for the nav diagram.
    """

    segments = allocate_nav_fill_segments(buckets)
    zone_ranges = _collect_zone_ranges(segments)
    colors: list[str] = [NAV_FILL_COLORS["neutral_light"] for _ in range(SEGMENT_COUNT)]

    for start_index, end_index, kind in zone_ranges:
        dark_color, light_color = _KIND_COLORS[kind]
        zone_length = end_index - start_index + 1
        for offset in range(zone_length):
            segment_index = start_index + offset
            if zone_length == 1:
                ratio = 0.5
            else:
                ratio = offset / (zone_length - 1)
            colors[segment_index] = interpolate_hex_colors(dark_color, light_color, ratio)

    _apply_zone_boundary_blends(colors, segments, zone_ranges)
    return NavFillPalette(colors=tuple(colors))


# ###### МЕЖІ КОЛІРНИХ ЗОН / COLOR ZONE BOUNDARIES ######
def _collect_zone_ranges(
    segments: tuple[NavFillSegmentKind, ...],
) -> list[tuple[int, int, NavFillSegmentKind]]:
    """Повертає інтервали однакових категорій у масиві сегментів.
    Returns intervals of equal categories in the segment array.
    """

    if not segments:
        return []

    ranges: list[tuple[int, int, NavFillSegmentKind]] = []
    start_index = 0
    current_kind = segments[0]

    for index in range(1, len(segments)):
        if segments[index] != current_kind:
            ranges.append((start_index, index - 1, current_kind))
            start_index = index
            current_kind = segments[index]

    ranges.append((start_index, len(segments) - 1, current_kind))
    return ranges


# ###### ЗГЛАДЖУВАННЯ СТИКІВ ЗОН / ZONE BOUNDARY BLENDING ######
def _apply_zone_boundary_blends(
    colors: list[str],
    segments: tuple[NavFillSegmentKind, ...],
    zone_ranges: list[tuple[int, int, NavFillSegmentKind]],
) -> None:
    """Змішує 1–2 сегменти на межах сусідніх зон.
    Blends 1–2 segments at adjacent zone boundaries.
    """

    for zone_index in range(len(zone_ranges) - 1):
        left_start, left_end, left_kind = zone_ranges[zone_index]
        right_start, _right_end, right_kind = zone_ranges[zone_index + 1]
        if left_kind == right_kind:
            continue

        left_color = colors[left_end]
        right_dark_color = _KIND_COLORS[right_kind][0]
        colors[left_end] = interpolate_hex_colors(left_color, right_dark_color, 0.35)

        if right_start == left_end + 1:
            colors[right_start] = interpolate_hex_colors(left_color, colors[right_start], 0.35)
