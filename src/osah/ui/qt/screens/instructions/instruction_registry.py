from collections.abc import Callable
from dataclasses import dataclass

from PySide6.QtWidgets import QWidget

from osah.domain.entities.access_role import AccessRole
from osah.domain.entities.app_section import AppSection
from osah.ui.shared.security.build_available_sections_for_role import build_available_sections_for_role
from osah.ui.qt.screens.instructions.sections.archive_instruction import build_archive_instruction_content
from osah.ui.qt.screens.instructions.sections.contractors_instruction import (
    build_contractors_instruction_content,
)
from osah.ui.qt.screens.instructions.sections.dashboard_instruction import build_dashboard_instruction_content
from osah.ui.qt.screens.instructions.sections.employees_instruction import build_employees_instruction_content
from osah.ui.qt.screens.instructions.sections.medical_instruction import build_medical_instruction_content
from osah.ui.qt.screens.instructions.sections.news_npa_instruction import build_news_npa_instruction_content
from osah.ui.qt.screens.instructions.sections.port_r_instruction import build_port_r_instruction_content
from osah.ui.qt.screens.instructions.sections.ppe_instruction import build_ppe_instruction_content
from osah.ui.qt.screens.instructions.sections.reports_instruction import build_reports_instruction_content
from osah.ui.qt.screens.instructions.sections.settings_instruction import build_settings_instruction_content
from osah.ui.qt.screens.instructions.sections.trainings_instruction import build_trainings_instruction_content
from osah.ui.qt.screens.instructions.sections.work_permits_instruction import build_work_permits_instruction_content

_SECTION_SUBTITLES: dict[AppSection, str] = {
    AppSection.DASHBOARD: "огляд сигналів і стану системи",
    AppSection.EMPLOYEES: "реєстр персоналу, фільтри та картка працівника",
    AppSection.TRAININGS: "облік проведення, строків повторення та проблемних записів",
    AppSection.PPE: "норми, видача, строки заміни та критичні відхилення",
    AppSection.MEDICAL: "меддопуск, строки дії та робочі обмеження",
    AppSection.WORK_PERMITS: "активні, прострочені та проблемні допуски до робіт",
    AppSection.CONTRACTORS: "облік підрядників і контроль їхнього допуску",
    AppSection.ARCHIVE: "архів подій, записів і службових підстав",
    AppSection.PORT_R: "методика динамічного оцінювання ризиків і робота в ClearWork",
    AppSection.REPORTS: "щоденний звіт, доставка та службові помилки",
    AppSection.NEWS_NPA: "довірені джерела НПА та новин",
    AppSection.SETTINGS: "резервні копії, імпорт, журнал і параметри системи",
}


@dataclass(frozen=True)
class InstructionEntry:
    """Запис реєстру інструкцій по розділу.
    Registry entry for a section instruction guide.
    """

    title: str
    subtitle: str
    build_content: Callable[[], QWidget]


INSTRUCTION_REGISTRY: dict[AppSection, InstructionEntry] = {
    AppSection.DASHBOARD: InstructionEntry(
        AppSection.DASHBOARD.value,
        _SECTION_SUBTITLES[AppSection.DASHBOARD],
        build_dashboard_instruction_content,
    ),
    AppSection.EMPLOYEES: InstructionEntry(
        AppSection.EMPLOYEES.value,
        _SECTION_SUBTITLES[AppSection.EMPLOYEES],
        build_employees_instruction_content,
    ),
    AppSection.TRAININGS: InstructionEntry(
        AppSection.TRAININGS.value,
        _SECTION_SUBTITLES[AppSection.TRAININGS],
        build_trainings_instruction_content,
    ),
    AppSection.PPE: InstructionEntry(
        AppSection.PPE.value,
        _SECTION_SUBTITLES[AppSection.PPE],
        build_ppe_instruction_content,
    ),
    AppSection.MEDICAL: InstructionEntry(
        AppSection.MEDICAL.value,
        _SECTION_SUBTITLES[AppSection.MEDICAL],
        build_medical_instruction_content,
    ),
    AppSection.WORK_PERMITS: InstructionEntry(
        AppSection.WORK_PERMITS.value,
        _SECTION_SUBTITLES[AppSection.WORK_PERMITS],
        build_work_permits_instruction_content,
    ),
    AppSection.CONTRACTORS: InstructionEntry(
        AppSection.CONTRACTORS.value,
        _SECTION_SUBTITLES[AppSection.CONTRACTORS],
        build_contractors_instruction_content,
    ),
    AppSection.ARCHIVE: InstructionEntry(
        AppSection.ARCHIVE.value,
        _SECTION_SUBTITLES[AppSection.ARCHIVE],
        build_archive_instruction_content,
    ),
    AppSection.PORT_R: InstructionEntry(
        AppSection.PORT_R.value,
        _SECTION_SUBTITLES[AppSection.PORT_R],
        build_port_r_instruction_content,
    ),
    AppSection.REPORTS: InstructionEntry(
        AppSection.REPORTS.value,
        _SECTION_SUBTITLES[AppSection.REPORTS],
        build_reports_instruction_content,
    ),
    AppSection.NEWS_NPA: InstructionEntry(
        AppSection.NEWS_NPA.value,
        _SECTION_SUBTITLES[AppSection.NEWS_NPA],
        build_news_npa_instruction_content,
    ),
    AppSection.SETTINGS: InstructionEntry(
        AppSection.SETTINGS.value,
        _SECTION_SUBTITLES[AppSection.SETTINGS],
        build_settings_instruction_content,
    ),
}


def get_instruction_entry(section: AppSection) -> InstructionEntry | None:
    """Повертає запис інструкції або None.
    Returns the instruction entry or None.
    """

    return INSTRUCTION_REGISTRY.get(section)


def list_instruction_sections_for_role(access_role: AccessRole) -> tuple[AppSection, ...]:
    """Повертає розділи з інструкціями, доступні для ролі.
    Returns instruction sections available for the given access role.
    """

    allowed = set(build_available_sections_for_role(access_role))
    ordered = tuple(section for section in AppSection if section in INSTRUCTION_REGISTRY)
    return tuple(section for section in ordered if section in allowed)
