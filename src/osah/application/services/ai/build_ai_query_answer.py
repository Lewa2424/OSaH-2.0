from dataclasses import dataclass
from pathlib import Path

from osah.application.services.ai.build_ai_explain_answer import build_ai_explain_answer
from osah.application.services.ai.build_ai_report_text import build_ai_report_text
from osah.application.services.ai.ground_ai_command_draft import effective_department_query
from osah.application.services.ai.query_daily_focus import query_daily_focus
from osah.application.services.ai.query_employee_module_records import query_employee_module_records
from osah.application.services.ai.query_employee_readiness import query_employee_readiness
from osah.application.services.ai.query_employees_by_department import query_employees_by_department
from osah.application.services.ai.query_employees_by_filter import query_employees_by_filter
from osah.application.services.ai.query_employees_by_module_status import query_employees_by_module_status
from osah.application.services.ai.query_employees_missing_ppe import (
    query_employees_missing_ppe,
    resolve_missing_ppe_item_label,
)
from osah.application.services.ai.query_section_problems import query_section_problems
from osah.application.services.ai.query_port_r_incomplete_passports import query_port_r_incomplete_passports
from osah.application.services.ai.query_work_permit_list import query_work_permit_list
from osah.application.services.ai.query_work_permit_participant_readiness import query_work_permit_participant_readiness
from osah.application.services.ai.search_ppe_catalog_candidates import search_ppe_catalog_candidates
from osah.domain.entities.ai_command_draft import AiCommandDraft
from osah.domain.entities.ai_intent_kind import AiIntentKind
from osah.domain.entities.ai_navigation_target import AiNavigationTarget
from osah.domain.entities.ai_ui_context import AiUiContext
from osah.domain.entities.app_section import AppSection
from osah.domain.entities.ppe_status import PpeStatus
from osah.domain.services.ai.format_ai_filter_key_label import format_ai_filter_key_label


@dataclass(slots=True, frozen=True)
class AiQueryAnswer:
    """Текстова відповідь AI-запиту.
    Text answer for an AI query command.
    """

    text: str
    follow_up_navigation: AiNavigationTarget | None = None
    allow_copy: bool = False


def build_ai_query_answer(
    database_path: Path,
    draft: AiCommandDraft,
    *,
    ui_context: AiUiContext | None = None,
) -> AiQueryAnswer | None:
    """Формує текстову відповідь для query/report/explain intent.
    Builds a text answer for query, report or explain intents.
    """

    if draft.intent == AiIntentKind.GENERATE_REPORT_TEXT:
        return AiQueryAnswer(
            text=build_ai_report_text(database_path, draft.report_scope),
            allow_copy=True,
        )

    if draft.intent == AiIntentKind.EXPLAIN_HELP:
        return AiQueryAnswer(text=build_ai_explain_answer(database_path, draft, ui_context=ui_context))

    if draft.intent == AiIntentKind.QUERY_MISSING_PPE:
        return _build_missing_ppe_answer(database_path, draft)

    if draft.intent == AiIntentKind.QUERY_MODULE_STATUS:
        return _build_module_status_answer(database_path, draft)

    if draft.intent == AiIntentKind.QUERY_DAILY_FOCUS:
        return _build_daily_focus_answer(database_path)

    if draft.intent == AiIntentKind.QUERY_EMPLOYEE_READINESS:
        return _build_employee_readiness_answer(database_path, draft)

    if draft.intent == AiIntentKind.QUERY_OVERDUE_SUMMARY:
        return _build_overdue_summary_answer(database_path, draft)

    if draft.intent == AiIntentKind.QUERY_SECTION_PROBLEMS:
        return _build_section_problems_answer(database_path)

    if draft.intent == AiIntentKind.QUERY_EMPLOYEE_RECORDS:
        return _build_employee_records_answer(database_path, draft)

    if draft.intent == AiIntentKind.QUERY_EMPLOYEES_FILTER:
        return _build_employees_filter_answer(database_path, draft)

    if draft.intent == AiIntentKind.QUERY_WORK_PERMIT_LIST:
        return _build_work_permit_list_answer(database_path, draft)

    if draft.intent == AiIntentKind.QUERY_WORK_PERMIT_READINESS:
        return _build_work_permit_readiness_answer(database_path, draft)

    if draft.intent == AiIntentKind.QUERY_PORT_R_GAPS:
        return _build_port_r_gaps_answer(database_path)

    return None


def _build_module_status_answer(database_path: Path, draft: AiCommandDraft) -> AiQueryAnswer:
    rows = query_employees_by_module_status(
        database_path,
        module_key=draft.module_key or draft.section_key,
        filter_key=draft.filter_key,
    )
    department_query = effective_department_query(draft) or ""
    if department_query:
        department_rows = query_employees_by_department(database_path, department_query)
        allowed_numbers = {row.personnel_number for row in department_rows}
        rows = tuple(row for row in rows if row.personnel_number in allowed_numbers)
    module_label = _module_label(draft.module_key or draft.section_key)
    status_label = format_ai_filter_key_label(draft.filter_key)
    if not rows:
        return AiQueryAnswer(
            text=f"За даними реєстру, працівників зі статусом «{status_label}» у розділі «{module_label}» не знайдено.",
            follow_up_navigation=AiNavigationTarget(section=_module_to_section(draft.module_key or draft.section_key)),
        )

    lines = [f"Працівники зі статусом «{status_label}» у «{module_label}» ({len(rows)}):"]
    display_rows = rows[:15]
    for row in display_rows:
        lines.append(f"• {row.full_name}, таб. №{row.personnel_number} — {row.status_label}: {row.detail}")
    if len(rows) > len(display_rows):
        lines.append(f"… і ще {len(rows) - len(display_rows)}.")
    navigation = AiNavigationTarget(section=_module_to_section(draft.module_key or draft.section_key))
    if navigation.section == AppSection.TRAININGS and draft.filter_key == "warning":
        navigation = AiNavigationTarget(section=AppSection.TRAININGS, training_status_filter="warning")
    if navigation.section == AppSection.PPE and draft.filter_key in {"not_issued", "overdue"}:
        navigation = AiNavigationTarget(
            section=AppSection.PPE,
            ppe_status_filter="not_issued" if draft.filter_key == "not_issued" else "expired",
        )
    return AiQueryAnswer(text="\n".join(lines), follow_up_navigation=navigation)


def _module_label(module_key: str | None) -> str:
    normalized = (module_key or "all").strip().lower()
    labels = {
        "trainings": "інструктажі",
        "інструктаж": "інструктажі",
        "инструктаж": "інструктажі",
        "ppe": "ЗІЗ",
        "зіз": "ЗІЗ",
        "сиз": "ЗІЗ",
        "medical": "медицина",
        "мед": "медицина",
    }
    return labels.get(normalized, module_key or "модуль")


def _build_missing_ppe_answer(database_path: Path, draft: AiCommandDraft) -> AiQueryAnswer:
    from osah.domain.services.ai.normalize_ppe_item_query import normalize_ppe_item_query

    ppe_item_query = normalize_ppe_item_query((draft.ppe_item_query or "").strip())
    if not search_ppe_catalog_candidates(database_path, ppe_item_query):
        return AiQueryAnswer(
            text=f"Предмет «{ppe_item_query}» не знайдено в каталозі ЗІЗ. Уточніть назву.",
            follow_up_navigation=AiNavigationTarget(section=AppSection.PPE),
        )

    item_label = resolve_missing_ppe_item_label(database_path, ppe_item_query)
    rows = query_employees_missing_ppe(
        database_path,
        ppe_item_query,
        department_query=effective_department_query(draft),
        position_query=(draft.position_query or "").strip() or None,
    )
    if not rows:
        return AiQueryAnswer(
            text=f"За даними реєстру, усі працівники мають актуальний запис «{item_label}».",
            follow_up_navigation=AiNavigationTarget(section=AppSection.PPE),
        )

    lines = [f"Потрібно закрити «{item_label}» для {len(rows)} працівник(ів):"]
    display_rows = rows[:15]
    for row in display_rows:
        status_label = "не видано" if row.status == PpeStatus.NOT_ISSUED else "прострочено"
        lines.append(f"• {row.full_name}, таб. №{row.personnel_number} — {status_label}")
    if len(rows) > len(display_rows):
        lines.append(f"… і ще {len(rows) - len(display_rows)}.")
    return AiQueryAnswer(
        text="\n".join(lines),
        follow_up_navigation=AiNavigationTarget(section=AppSection.PPE, ppe_status_filter=PpeStatus.NOT_ISSUED.value),
    )


def _build_daily_focus_answer(database_path: Path) -> AiQueryAnswer:
    result = query_daily_focus(database_path)
    lines = [result.focus_text]
    if result.problems:
        lines.append("")
        lines.append("Пріоритетні записи:")
        for problem in result.problems:
            lines.append(f"• {problem.employee_name} (№{problem.personnel_number}): {problem.title}")
    return AiQueryAnswer(
        text="\n".join(lines),
        follow_up_navigation=AiNavigationTarget(section=AppSection.DASHBOARD),
    )


def _build_employee_readiness_answer(database_path: Path, draft: AiCommandDraft) -> AiQueryAnswer | None:
    personnel_number = (draft.personnel_number or "").strip()
    if not personnel_number:
        return AiQueryAnswer(text="Потрібен працівник або табельний номер.")

    result = query_employee_readiness(database_path, personnel_number=personnel_number)
    if result is None:
        return AiQueryAnswer(text="Працівника не знайдено.")
    readiness_label = "готовий" if result.overall_ready else "не готовий"
    text = (
        f"{result.employee_name} (таб. №{result.personnel_number}) — {readiness_label} до робіт.\n"
        f"Інструктажі: {result.training_message}\n"
        f"Медицина: {result.medical_message}\n"
        f"ЗІЗ: {result.ppe_message}"
    )
    return AiQueryAnswer(
        text=text,
        follow_up_navigation=AiNavigationTarget(
            section=AppSection.EMPLOYEES,
            employee_personnel_number=result.personnel_number,
        ),
    )


def _build_overdue_summary_answer(database_path: Path, draft: AiCommandDraft) -> AiQueryAnswer:
    module_key = normalize_ai_module_key(draft.module_key or draft.section_key)
    summary = query_overdue_summary(database_path, module_key)
    lines = [
        "Прострочення та попередження:",
        f"• ЗІЗ прострочено: {summary.ppe_expired}",
        f"• ЗІЗ не видано: {summary.ppe_not_issued}",
        f"• ЗІЗ попередження: {summary.ppe_warning}",
        f"• Інструктажі прострочено: {summary.training_overdue}",
        f"• Інструктажі попередження: {summary.training_warning}",
        f"• Медицина прострочена: {summary.medical_expired}",
        f"• Медицина попередження: {summary.medical_warning}",
        f"• Наряди прострочені: {summary.work_permit_expired}",
        f"• Наряди попередження: {summary.work_permit_warning}",
    ]
    section = _module_to_section(module_key)
    return AiQueryAnswer(text="\n".join(lines), follow_up_navigation=AiNavigationTarget(section=section))


def _build_section_problems_answer(database_path: Path) -> AiQueryAnswer:
    rows = query_section_problems(database_path)
    if not rows:
        return AiQueryAnswer(
            text="Зараз у всіх розділах немає критичних або жовтих індикаторів.",
            follow_up_navigation=AiNavigationTarget(section=AppSection.DASHBOARD),
        )
    lines = ["Проблемні розділи (як на nav-діаграмі):"]
    for row in rows:
        lines.append(
            f"• {row.label}: критичних {row.critical}, попереджень {row.warning} (всього записів {row.total})"
        )
    return AiQueryAnswer(
        text="\n".join(lines),
        follow_up_navigation=AiNavigationTarget(section=AppSection.DASHBOARD),
    )


def _build_employee_records_answer(database_path: Path, draft: AiCommandDraft) -> AiQueryAnswer:
    rows = query_employee_module_records(
        database_path,
        employee_query=draft.employee_query,
        personnel_number=draft.personnel_number,
        module_key=draft.module_key or draft.section_key,
    )
    if not rows:
        return AiQueryAnswer(text="Записів для цього працівника не знайдено.")
    lines = ["Записи працівника:"]
    for row in rows[:20]:
        lines.append(f"• {row.title} — {row.status_label}: {row.detail}")
    section = _module_to_section(draft.module_key or draft.section_key)
    return AiQueryAnswer(
        text="\n".join(lines),
        follow_up_navigation=AiNavigationTarget(
            section=section,
            employee_personnel_number=draft.personnel_number,
        ),
    )


def _build_employees_filter_answer(database_path: Path, draft: AiCommandDraft) -> AiQueryAnswer:
    filter_key = draft.filter_key or draft.module_key or draft.section_key or "active"
    if filter_key.strip().lower() == "department":
        department_query = effective_department_query(draft) or ""
        if not department_query:
            return AiQueryAnswer(text="Вкажіть підрозділ для списку працівників.")
        rows = query_employees_by_department(database_path, department_query)
        if not rows:
            return AiQueryAnswer(text=f"У підрозділі «{department_query}» активних працівників не знайдено.")
        lines = [f"Підрозділ «{rows[0].department_name}»: {len(rows)} працівник(ів)"]
        for row in rows[:20]:
            detail = row.position_name or "без посади"
            lines.append(f"• {row.full_name}, №{row.personnel_number} — {detail}")
        if len(rows) > 20:
            lines.append(f"… і ще {len(rows) - 20}.")
        return AiQueryAnswer(
            text="\n".join(lines),
            follow_up_navigation=AiNavigationTarget(section=AppSection.EMPLOYEES),
        )

    rows = query_employees_by_filter(database_path, filter_key)
    if not rows:
        return AiQueryAnswer(text="За цим фільтром працівників не знайдено.")
    lines = [f"Знайдено {len(rows)} працівник(ів):"]
    for row in rows[:20]:
        detail = row.position_name or "без посади"
        if row.department_name:
            detail = f"{detail}, {row.department_name}"
        if row.employment_status:
            detail = f"{detail} — {row.employment_status}"
        lines.append(f"• {row.full_name}, №{row.personnel_number} — {detail}")
    return AiQueryAnswer(
        text="\n".join(lines),
        follow_up_navigation=AiNavigationTarget(section=AppSection.EMPLOYEES),
    )


def _build_work_permit_list_answer(database_path: Path, draft: AiCommandDraft) -> AiQueryAnswer:
    rows = query_work_permit_list(database_path, draft.module_key or draft.section_key or "open")
    if not rows:
        return AiQueryAnswer(text="Нарядів за цим фільтром не знайдено.")
    lines = [f"Наряди ({len(rows)}):"]
    for row in rows[:15]:
        lines.append(f"• №{row.permit_number} — {row.work_kind}, {row.starts_at} — {row.status.value}")
    return AiQueryAnswer(
        text="\n".join(lines),
        follow_up_navigation=AiNavigationTarget(section=AppSection.WORK_PERMITS),
    )


def _build_work_permit_readiness_answer(database_path: Path, draft: AiCommandDraft) -> AiQueryAnswer:
    result = query_work_permit_participant_readiness(
        database_path,
        permit_number=draft.permit_number,
        permit_query=draft.permit_query,
    )
    if result is None:
        return AiQueryAnswer(text="Наряд не знайдено.")
    lines = [f"Готовність учасників наряду №{result.permit_number}:"]
    for row in result.participants:
        label = "готовий" if row.ready else "не готовий"
        lines.append(f"• {row.employee_name} — {label}: {row.message}")
    return AiQueryAnswer(
        text="\n".join(lines),
        follow_up_navigation=AiNavigationTarget(section=AppSection.WORK_PERMITS),
    )


def _build_port_r_gaps_answer(database_path: Path) -> AiQueryAnswer:
    rows = query_port_r_incomplete_passports(database_path)
    if not rows:
        return AiQueryAnswer(text="Критичних прогалин у паспортах PORT-R не знайдено.")
    lines = ["Паспорти PORT-R, що потребують уваги:"]
    for row in rows[:15]:
        lines.append(f"• {row.passport_code} / {row.site_name} — {row.gap_text} ({row.profile_label})")
    return AiQueryAnswer(
        text="\n".join(lines),
        follow_up_navigation=AiNavigationTarget(section=AppSection.PORT_R),
    )


def _module_to_section(module_key: str | None) -> AppSection:
    normalized = (module_key or "all").strip().lower()
    if normalized in {"trainings", "інструктаж", "инструктаж"}:
        return AppSection.TRAININGS
    if normalized in {"medical", "мед"}:
        return AppSection.MEDICAL
    if normalized in {"work_permits", "наряд", "наряди"}:
        return AppSection.WORK_PERMITS
    if normalized in {"port_r", "port-r"}:
        return AppSection.PORT_R
    if normalized in {"employees", "працівник", "сотрудник"}:
        return AppSection.EMPLOYEES
    return AppSection.PPE
