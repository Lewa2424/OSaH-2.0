from pathlib import Path

from osah.application.services.ai.build_ai_explain_grounding_facts import build_ai_explain_grounding_facts
from osah.application.services.ai.format_ai_explain_text_with_llm import format_ai_explain_text_with_llm
from osah.application.services.ai.query_employee_readiness import query_employee_readiness
from osah.application.services.ai.search_employees_by_query import search_employees_by_query
from osah.application.services.load_medical_registry import load_medical_registry
from osah.application.services.load_ppe_registry import load_ppe_registry
from osah.application.services.load_training_registry import load_training_registry
from osah.domain.ai.ai_domain_help_snippets import get_ai_domain_help_snippet, get_ai_error_help_snippet
from osah.domain.entities.ai_command_draft import AiCommandDraft
from osah.domain.entities.ai_ui_context import AiUiContext
from osah.domain.services.build_medical_status_reason import build_medical_status_reason
from osah.domain.services.build_ppe_status_reason import build_ppe_status_reason
from osah.domain.services.build_training_status_reason import build_training_status_reason
from osah.infrastructure.config.build_ai_runtime_paths import (
    build_ai_runtime_paths,
    is_ai_runtime_bundle_available,
)


def build_ai_explain_answer(
    database_path: Path,
    draft: AiCommandDraft,
    *,
    ui_context: AiUiContext | None = None,
    project_root: Path | None = None,
    prefer_fallback_model: bool = False,
) -> str:
    """Формує пояснення для explain_help intent.
    Builds an explanation answer for the explain_help intent.
    """

    topic = (draft.explain_topic or "domain").strip().lower()
    module_key = (draft.module_key or draft.section_key or "").strip().lower()
    command_lower = draft.raw_command.lower()

    if topic == "error":
        for key in ("employee_not_found", "ambiguous_employee", "invalid_date", "save_failed", "bulk_unsupported"):
            snippet = get_ai_error_help_snippet(key)
            if snippet and key.replace("_", " ")[:4] in command_lower:
                return snippet
        if "не знайден" in command_lower or "не найден" in command_lower:
            return get_ai_error_help_snippet("employee_not_found") or ""
        if "кілька" in command_lower or "несколько" in command_lower:
            return get_ai_error_help_snippet("ambiguous_employee") or ""
        return get_ai_error_help_snippet("save_failed") or "Перевірте введені дані та спробуйте ще раз."

    if topic == "ui":
        section_label = ui_context.section.value if ui_context and ui_context.section else "поточний розділ"
        return (
            f"Пояснення для {section_label}. "
            "Статуси та поля формуються правилами модуля: червоний — критична проблема, "
            "жовтий — попередження, зелений — актуально."
        )

    grounded_facts = build_ai_explain_grounding_facts(database_path, draft, ui_context=ui_context)
    runtime_paths = build_ai_runtime_paths(project_root)
    if grounded_facts and is_ai_runtime_bundle_available(runtime_paths):
        try:
            llm_text = format_ai_explain_text_with_llm(
                database_path,
                draft,
                grounded_facts,
                runtime_paths,
                ui_context=ui_context,
                prefer_fallback_model=prefer_fallback_model,
            )
            if llm_text:
                return llm_text
        except (RuntimeError, TimeoutError, ValueError):
            pass

    if topic == "status":
        if grounded_facts:
            return grounded_facts
        return _build_status_explanation(database_path, draft, module_key)

    domain_key = module_key or draft.raw_command
    snippet = get_ai_domain_help_snippet(domain_key)
    if snippet:
        return snippet
    return (
        "ClearWork AI пояснює статуси, поля та терміни на основі даних реєстру. "
        "Уточніть модуль або працівника для точнішої відповіді."
    )


def _build_status_explanation(database_path: Path, draft: AiCommandDraft, module_key: str) -> str:
    personnel_number = (draft.personnel_number or "").strip()
    if not personnel_number and draft.employee_query:
        matches = search_employees_by_query(database_path, draft.employee_query)
        if len(matches) == 1:
            personnel_number = matches[0].personnel_number

    if personnel_number and module_key in {"ppe", "зіз", "сиз"}:
        for record in load_ppe_registry(database_path):
            if record.employee_personnel_number == personnel_number:
                return build_ppe_status_reason(record)
    if personnel_number and module_key in {"trainings", "інструктаж", "инструктаж"}:
        for record in load_training_registry(database_path):
            if record.employee_personnel_number == personnel_number:
                return build_training_status_reason(
                    record.status,
                    record.training_type,
                    record.next_control_date,
                    record.next_control_basis,
                )
    if personnel_number and module_key in {"medical", "мед"}:
        for record in load_medical_registry(database_path):
            if record.employee_personnel_number == personnel_number:
                return build_medical_status_reason(record)

    if personnel_number:
        readiness = query_employee_readiness(database_path, personnel_number=personnel_number)
        if readiness is not None:
            return (
                f"{readiness.employee_name}: інструктажі — {readiness.training_message}; "
                f"медицина — {readiness.medical_message}; ЗІЗ — {readiness.ppe_message}."
            )

    if "червон" in draft.raw_command.lower() or "красн" in draft.raw_command.lower():
        return "Червоний статус означає критичну проблему: прострочення, відсутній запис або недопуск до робіт."
    if "жовт" in draft.raw_command.lower() or "жёлт" in draft.raw_command.lower() or "желт" in draft.raw_command.lower():
        return "Жовтий статус — попередження: строк скоро закінчується або потрібна перевірка."
    return "Зелений статус означає, що запис актуальний і не блокує допуск до робіт."
