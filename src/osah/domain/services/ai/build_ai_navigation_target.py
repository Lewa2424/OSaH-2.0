from osah.domain.entities.ai_command_draft import AiCommandDraft
from osah.domain.entities.ai_intent_kind import AiIntentKind
from osah.domain.entities.ai_navigation_target import AiNavigationTarget
from osah.domain.entities.ai_ui_context import AiUiContext
from osah.domain.entities.app_section import AppSection
from osah.domain.entities.medical_status import MedicalStatus
from osah.domain.entities.ppe_status import PpeStatus
from osah.domain.entities.training_status import TrainingStatus
from osah.domain.entities.work_permit_status import WorkPermitStatus

_SECTION_KEY_MAP: dict[str, AppSection] = {
    "dashboard": AppSection.DASHBOARD,
    "employees": AppSection.EMPLOYEES,
    "trainings": AppSection.TRAININGS,
    "ppe": AppSection.PPE,
    "medical": AppSection.MEDICAL,
    "work_permits": AppSection.WORK_PERMITS,
    "contractors": AppSection.CONTRACTORS,
    "archive": AppSection.ARCHIVE,
    "port_r": AppSection.PORT_R,
    "reports": AppSection.REPORTS,
    "news": AppSection.NEWS_NPA,
    "settings": AppSection.SETTINGS,
}


def build_ai_navigation_target(
    draft: AiCommandDraft,
    *,
    ui_context: AiUiContext | None = None,
) -> AiNavigationTarget | None:
    """Будує ціль навігації з read-only AI-intent.
    Builds a navigation target from a read-only AI intent.
    """

    if draft.intent == AiIntentKind.NAVIGATE_SECTION:
        section_key = (draft.section_key or "").strip().lower()
        section = _SECTION_KEY_MAP.get(section_key)
        if section is None and ui_context is not None and ui_context.section is not None:
            section = ui_context.section
        if section is None:
            section = AppSection.DASHBOARD
        return AiNavigationTarget(section=section)

    if draft.intent == AiIntentKind.SHOW_OVERDUE:
        section = _resolve_overdue_section(ui_context)
        return AiNavigationTarget(
            section=section,
            ppe_status_filter=PpeStatus.EXPIRED.value if section == AppSection.PPE else None,
            training_status_filter=TrainingStatus.OVERDUE.value if section == AppSection.TRAININGS else None,
            medical_status_filter=MedicalStatus.EXPIRED.value if section == AppSection.MEDICAL else None,
            work_permit_status_filter=WorkPermitStatus.EXPIRED.value if section == AppSection.WORK_PERMITS else None,
        )

    if draft.intent == AiIntentKind.OPEN_EMPLOYEE_CARD:
        personnel_number = draft.personnel_number
        if personnel_number is None and ui_context is not None:
            personnel_number = ui_context.employee_personnel_number
        return AiNavigationTarget(
            section=AppSection.EMPLOYEES,
            employee_personnel_number=personnel_number,
        )

    return None


def _resolve_overdue_section(ui_context: AiUiContext | None) -> AppSection:
    if ui_context is None or ui_context.section is None:
        return AppSection.DASHBOARD

    if ui_context.section in {
        AppSection.PPE,
        AppSection.TRAININGS,
        AppSection.MEDICAL,
        AppSection.WORK_PERMITS,
    }:
        return ui_context.section
    return AppSection.DASHBOARD
