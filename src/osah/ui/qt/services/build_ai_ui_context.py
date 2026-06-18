from osah.domain.entities.ai_navigation_target import AiNavigationTarget
from osah.domain.entities.ai_ui_context import AiUiContext
from osah.domain.entities.app_section import AppSection
from osah.ui.qt.routing.qt_navigation_intent import QtNavigationIntent


def build_ai_ui_context(
    *,
    section: AppSection | None,
    navigation_intent: QtNavigationIntent | None,
) -> AiUiContext:
    """Збирає UI-контекст для AI-команди.
    Builds UI context for AI commands.
    """

    if navigation_intent is None:
        return AiUiContext(section=section)

    return AiUiContext(
        section=section,
        employee_personnel_number=navigation_intent.employee_personnel_number,
        ppe_status_filter=navigation_intent.ppe_status_filter,
        training_status_filter=navigation_intent.training_status_filter,
        medical_status_filter=navigation_intent.medical_status_filter,
        work_permit_status_filter=navigation_intent.work_permit_status_filter,
        permit_number=navigation_intent.work_permit_number,
        port_passport_code=navigation_intent.port_passport_code,
    )


def build_qt_navigation_intent(target: AiNavigationTarget) -> QtNavigationIntent:
    """Конвертує AI navigation target у QtNavigationIntent.
    Converts an AI navigation target into QtNavigationIntent.
    """

    return QtNavigationIntent(
        target_section=target.section,
        employee_personnel_number=target.employee_personnel_number,
        ppe_status_filter=target.ppe_status_filter,
        training_status_filter=target.training_status_filter,
        medical_status_filter=target.medical_status_filter,
        work_permit_status_filter=target.work_permit_status_filter,
    )
