from dataclasses import dataclass
from pathlib import Path

from osah.application.services.load_medical_workspace import load_medical_workspace
from osah.application.services.load_ppe_workspace import load_ppe_workspace
from osah.application.services.load_training_workspace import load_training_workspace
from osah.application.services.load_work_permit_workspace import load_work_permit_workspace
from osah.domain.entities.app_section import AppSection
from osah.domain.entities.section_nav_fill_buckets import SectionNavFillBuckets
from osah.domain.services.build_section_nav_fill_buckets import build_section_nav_fill_bucket_profiles

_SECTION_LABELS: dict[AppSection, str] = {
    AppSection.DASHBOARD: "Головна",
    AppSection.TRAININGS: "Інструктажі",
    AppSection.PPE: "ЗІЗ",
    AppSection.MEDICAL: "Медицина",
    AppSection.WORK_PERMITS: "Наряди-допуски",
}


@dataclass(slots=True, frozen=True)
class SectionProblemRow:
    """Проблемний розділ із лічильниками nav-діаграми.
    Problematic section with nav diagram counters.
    """

    section: AppSection
    label: str
    critical: int
    warning: int
    total: int


def query_section_problems(database_path: Path) -> tuple[SectionProblemRow, ...]:
    """Повертає розділи з критичними або жовтими індикаторами.
    Returns sections that have critical or warning indicators.
    """

    training_workspace = load_training_workspace(database_path)
    ppe_workspace = load_ppe_workspace(database_path)
    medical_workspace = load_medical_workspace(database_path)
    work_permit_workspace = load_work_permit_workspace(database_path)

    bucket_profiles = build_section_nav_fill_bucket_profiles(
        training_workspace.summary,
        ppe_workspace.summary,
        medical_workspace.summary,
        work_permit_workspace.summary,
    )

    rows: list[SectionProblemRow] = []
    for section, buckets in bucket_profiles.items():
        if buckets is None:
            continue
        if not _section_has_problems(buckets):
            continue
        rows.append(
            SectionProblemRow(
                section=section,
                label=_SECTION_LABELS.get(section, section.value),
                critical=buckets.critical,
                warning=buckets.warning,
                total=buckets.total,
            )
        )
    return tuple(rows)


def _section_has_problems(buckets: SectionNavFillBuckets) -> bool:
    return buckets.critical > 0 or buckets.warning > 0
