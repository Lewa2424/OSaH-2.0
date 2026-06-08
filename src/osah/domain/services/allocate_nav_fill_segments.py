from osah.domain.entities.nav_fill_segment_kind import NavFillSegmentKind
from osah.domain.entities.section_nav_fill_buckets import SectionNavFillBuckets
from osah.domain.services.nav_fill_constants import MIN_PROBLEM_SHARE, SEGMENT_COUNT

_ORDERED_KINDS = (
    NavFillSegmentKind.CRITICAL,
    NavFillSegmentKind.WARNING,
    NavFillSegmentKind.RESTRICTED,
    NavFillSegmentKind.OK,
)


# ###### РОЗПОДІЛ СЕГМЕНТІВ NAV-ДІАГРАМИ / ALLOCATE NAV DIAGRAM SEGMENTS ######
def allocate_nav_fill_segments(buckets: SectionNavFillBuckets) -> tuple[NavFillSegmentKind, ...]:
    """Розподіляє 120 сегментів з 20% floor для проблемних категорій.
    Allocates 120 segments with a 20% floor for problem categories.
    """

    if buckets.total <= 0:
        return tuple(NavFillSegmentKind.NEUTRAL for _ in range(SEGMENT_COUNT))

    min_problem_segments = int(SEGMENT_COUNT * MIN_PROBLEM_SHARE)
    reserved_critical = 0
    reserved_warning = 0

    if buckets.critical > 0 and buckets.warning > 0:
        reserved_critical = min_problem_segments
    elif buckets.critical > 0:
        reserved_critical = min_problem_segments
    elif buckets.warning > 0:
        reserved_warning = min_problem_segments

    remaining = SEGMENT_COUNT - reserved_critical - reserved_warning
    proportional_counts = _allocate_proportional_counts(
        remaining,
        (
            (NavFillSegmentKind.CRITICAL, buckets.critical),
            (NavFillSegmentKind.WARNING, buckets.warning),
            (NavFillSegmentKind.RESTRICTED, buckets.restricted),
            (NavFillSegmentKind.OK, buckets.ok),
        ),
    )

    ordered_segments: list[NavFillSegmentKind] = []
    if reserved_critical > 0:
        ordered_segments.extend(NavFillSegmentKind.CRITICAL for _ in range(reserved_critical))
    if reserved_warning > 0:
        ordered_segments.extend(NavFillSegmentKind.WARNING for _ in range(reserved_warning))

    for kind in _ORDERED_KINDS:
        ordered_segments.extend(kind for _ in range(proportional_counts.get(kind, 0)))

    if len(ordered_segments) < SEGMENT_COUNT:
        ordered_segments.extend(
            NavFillSegmentKind.NEUTRAL for _ in range(SEGMENT_COUNT - len(ordered_segments))
        )
    elif len(ordered_segments) > SEGMENT_COUNT:
        ordered_segments = ordered_segments[:SEGMENT_COUNT]

    return tuple(ordered_segments)


# ###### ПРОПОРЦІЙНИЙ РОЗПОДІЛ СЕГМЕНТІВ / PROPORTIONAL SEGMENT ALLOCATION ######
def _allocate_proportional_counts(
    total_segments: int,
    weighted_kinds: tuple[tuple[NavFillSegmentKind, int], ...],
) -> dict[NavFillSegmentKind, int]:
    """Розподіляє сегменти методом найбільших залишків.
    Allocates segments using the largest-remainder method.
    """

    active_weights = [(kind, weight) for kind, weight in weighted_kinds if weight > 0]
    if total_segments <= 0 or not active_weights:
        return {kind: 0 for kind in _ORDERED_KINDS}

    total_weight = sum(weight for _, weight in active_weights)
    exact_values = [
        (kind, (total_segments * weight) / total_weight)
        for kind, weight in active_weights
    ]
    allocated = {kind: int(value) for kind, value in exact_values}
    assigned_total = sum(allocated.values())
    remainder = total_segments - assigned_total

    if remainder > 0:
        remainders = sorted(
            ((kind, value - int(value)) for kind, value in exact_values),
            key=lambda item: item[1],
            reverse=True,
        )
        for index in range(remainder):
            kind = remainders[index % len(remainders)][0]
            allocated[kind] = allocated.get(kind, 0) + 1

    for kind in _ORDERED_KINDS:
        allocated.setdefault(kind, 0)
    return allocated
