from osah.domain.entities.app_section import AppSection
from osah.domain.entities.medical_workspace_summary import MedicalWorkspaceSummary
from osah.domain.entities.ppe_workspace_summary import PpeWorkspaceSummary
from osah.domain.entities.section_nav_fill_buckets import SectionNavFillBuckets
from osah.domain.entities.training_workspace_summary import TrainingWorkspaceSummary
from osah.domain.entities.work_permit_workspace_summary import WorkPermitWorkspaceSummary


# ###### ПІДСУМКИ МОДУЛІВ ДЛЯ NAV-ДІАГРАМИ / MODULE SUMMARIES FOR NAV DIAGRAM ######
def build_training_nav_fill_buckets(summary: TrainingWorkspaceSummary) -> SectionNavFillBuckets:
    """Будує лічильники інструктажів для nav-діаграми.
    Builds trainings counters for the nav diagram.
    """

    critical = summary.critical_total + summary.missing_total
    warning = summary.warning_total
    ok = summary.current_total
    return SectionNavFillBuckets(
        total=summary.total_rows,
        critical=critical,
        warning=warning,
        restricted=0,
        ok=ok,
    )


# ###### ПІДСУМКИ ЗІЗ ДЛЯ NAV-ДІАГРАМИ / PPE SUMMARY FOR NAV DIAGRAM ######
def build_ppe_nav_fill_buckets(summary: PpeWorkspaceSummary) -> SectionNavFillBuckets:
    """Будує лічильники ЗІЗ для nav-діаграми.
    Builds PPE counters for the nav diagram.
    """

    critical = summary.critical_total + summary.not_issued_total
    warning = summary.warning_total
    ok = summary.current_total
    return SectionNavFillBuckets(
        total=summary.total_rows,
        critical=critical,
        warning=warning,
        restricted=0,
        ok=ok,
    )


# ###### ПІДСУМКИ МЕДИЦИНИ ДЛЯ NAV-ДІАГРАМИ / MEDICAL SUMMARY FOR NAV DIAGRAM ######
def build_medical_nav_fill_buckets(summary: MedicalWorkspaceSummary) -> SectionNavFillBuckets:
    """Будує лічильники медицини для nav-діаграми.
    Builds medical counters for the nav diagram.
    """

    return SectionNavFillBuckets(
        total=summary.total_rows,
        critical=summary.critical_total,
        warning=summary.warning_total,
        restricted=summary.restricted_total,
        ok=summary.current_total,
    )


# ###### ПІДСУМКИ НАРЯДІВ ДЛЯ NAV-ДІАГРАМИ / WORK PERMIT SUMMARY FOR NAV DIAGRAM ######
def build_work_permit_nav_fill_buckets(summary: WorkPermitWorkspaceSummary) -> SectionNavFillBuckets:
    """Будує лічильники нарядів-допусків для nav-діаграми.
    Builds work-permit counters for the nav diagram.
    """

    critical = summary.expired_total + summary.conflict_total
    warning = summary.warning_total
    ok = summary.active_total
    total = critical + warning + ok
    return SectionNavFillBuckets(
        total=total,
        critical=critical,
        warning=warning,
        restricted=0,
        ok=ok,
    )


# ###### АГРЕГАТ ГОЛОВНОЇ ДЛЯ NAV-ДІАГРАМИ / DASHBOARD AGGREGATE FOR NAV DIAGRAM ######
def build_dashboard_nav_fill_buckets(
    training_buckets: SectionNavFillBuckets,
    ppe_buckets: SectionNavFillBuckets,
    medical_buckets: SectionNavFillBuckets,
    work_permit_buckets: SectionNavFillBuckets,
) -> SectionNavFillBuckets:
    """Сумує OP-модулі для діаграми розділу «Головна».
    Aggregates OP modules for the dashboard nav diagram.
    """

    return SectionNavFillBuckets(
        total=(
            training_buckets.total
            + ppe_buckets.total
            + medical_buckets.total
            + work_permit_buckets.total
        ),
        critical=(
            training_buckets.critical
            + ppe_buckets.critical
            + medical_buckets.critical
            + work_permit_buckets.critical
        ),
        warning=(
            training_buckets.warning
            + ppe_buckets.warning
            + medical_buckets.warning
            + work_permit_buckets.warning
        ),
        restricted=(
            training_buckets.restricted
            + ppe_buckets.restricted
            + medical_buckets.restricted
            + work_permit_buckets.restricted
        ),
        ok=(
            training_buckets.ok
            + ppe_buckets.ok
            + medical_buckets.ok
            + work_permit_buckets.ok
        ),
    )


# ###### ПРОФІЛІ NAV-ДІАГРАМ ПО РОЗДІЛАХ / NAV DIAGRAM PROFILES BY SECTION ######
def build_section_nav_fill_bucket_profiles(
    training_summary: TrainingWorkspaceSummary,
    ppe_summary: PpeWorkspaceSummary,
    medical_summary: MedicalWorkspaceSummary,
    work_permit_summary: WorkPermitWorkspaceSummary,
) -> dict[AppSection, SectionNavFillBuckets | None]:
    """Повертає buckets для OP-розділів і головної; інші розділи без діаграми.
    Returns buckets for OP sections and dashboard; other sections have no diagram.
    """

    training_buckets = build_training_nav_fill_buckets(training_summary)
    ppe_buckets = build_ppe_nav_fill_buckets(ppe_summary)
    medical_buckets = build_medical_nav_fill_buckets(medical_summary)
    work_permit_buckets = build_work_permit_nav_fill_buckets(work_permit_summary)
    dashboard_buckets = build_dashboard_nav_fill_buckets(
        training_buckets,
        ppe_buckets,
        medical_buckets,
        work_permit_buckets,
    )

    return {
        AppSection.DASHBOARD: dashboard_buckets,
        AppSection.TRAININGS: training_buckets,
        AppSection.PPE: ppe_buckets,
        AppSection.MEDICAL: medical_buckets,
        AppSection.WORK_PERMITS: work_permit_buckets,
        AppSection.EMPLOYEES: None,
        AppSection.CONTRACTORS: None,
        AppSection.ARCHIVE: None,
        AppSection.PORT_R: None,
        AppSection.REPORTS: None,
        AppSection.NEWS_NPA: None,
        AppSection.SETTINGS: None,
        AppSection.ABOUT: None,
    }
