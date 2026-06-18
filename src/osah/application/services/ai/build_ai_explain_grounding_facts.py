from pathlib import Path

from osah.application.services.ai.query_port_r_incomplete_passports import query_port_r_incomplete_passports
from osah.application.services.ai.query_work_permit_participant_readiness import query_work_permit_participant_readiness
from osah.domain.entities.ai_command_draft import AiCommandDraft
from osah.domain.entities.ai_ui_context import AiUiContext
from osah.application.services.ai.search_employees_by_query import search_employees_by_query
from osah.application.services.ai.query_employee_readiness import query_employee_readiness
from osah.application.services.load_medical_registry import load_medical_registry
from osah.application.services.load_ppe_registry import load_ppe_registry
from osah.application.services.load_training_registry import load_training_registry
from osah.domain.services.build_medical_status_reason import build_medical_status_reason
from osah.domain.services.build_ppe_status_reason import build_ppe_status_reason
from osah.domain.services.build_training_status_reason import build_training_status_reason


def build_ai_explain_grounding_facts(
    database_path: Path,
    draft: AiCommandDraft,
    *,
    ui_context: AiUiContext | None = None,
) -> str:
    """Збирає фактичну основу для explain_help з реєстрів БД.
    Collects factual grounding for explain_help from database registries.
    """

    module_key = (draft.module_key or draft.section_key or "").strip().lower()
    if ui_context and ui_context.section:
        section_value = ui_context.section.value
        if not module_key:
            module_key = section_value

    personnel_number = (draft.personnel_number or "").strip()
    if not personnel_number and ui_context and ui_context.employee_personnel_number:
        personnel_number = ui_context.employee_personnel_number.strip()
    if not personnel_number and draft.employee_query:
        matches = search_employees_by_query(database_path, draft.employee_query)
        if len(matches) == 1:
            personnel_number = matches[0].personnel_number

    facts: list[str] = []
    if personnel_number:
        readiness = query_employee_readiness(database_path, personnel_number=personnel_number)
        if readiness is not None:
            facts.append(f"Працівник: {readiness.employee_name}, таб. №{readiness.personnel_number}")
            facts.append(f"Інструктажі: {readiness.training_message}")
            facts.append(f"Медицина: {readiness.medical_message}")
            facts.append(f"ЗІЗ: {readiness.ppe_message}")

        if module_key in {"ppe", "зіз", "сиз"}:
            for record in load_ppe_registry(database_path):
                if record.employee_personnel_number == personnel_number:
                    facts.append(build_ppe_status_reason(record))
                    break
        if module_key in {"trainings", "інструктаж", "инструктаж"}:
            for record in load_training_registry(database_path):
                if record.employee_personnel_number == personnel_number:
                    facts.append(
                        build_training_status_reason(
                            record.status,
                            record.training_type,
                            record.next_control_date,
                            record.next_control_basis,
                        )
                    )
                    break
        if module_key in {"medical", "мед"}:
            for record in load_medical_registry(database_path):
                if record.employee_personnel_number == personnel_number:
                    facts.append(build_medical_status_reason(record))
                    break

    permit_number = (draft.permit_number or "").strip()
    if not permit_number and ui_context and ui_context.permit_number:
        permit_number = str(ui_context.permit_number).strip()
    if module_key in {"work_permits", "work_permit", "наряд"} or permit_number:
        if permit_number:
            readiness = query_work_permit_participant_readiness(
                database_path,
                permit_number=permit_number,
            )
            if readiness is not None:
                not_ready = sum(1 for row in readiness.participants if not row.ready)
                facts.append(
                    f"Наряд №{readiness.permit_number}: учасників {len(readiness.participants)}, "
                    f"не готові {not_ready}."
                )
                for row in readiness.participants[:8]:
                    facts.append(f"- {row.employee_name}: {row.message}")

    if module_key in {"port_r", "port-r"} or "port" in draft.raw_command.lower():
        gaps = query_port_r_incomplete_passports(database_path)
        if gaps:
            facts.append(f"Незаповнені паспорти PORT-R: {len(gaps)}")
            for row in gaps[:5]:
                facts.append(f"- {row.site_name} ({row.passport_code}): {row.gap_text}")
        else:
            facts.append("Усі паспорти PORT-R заповнені за основними полями.")

    if ui_context and ui_context.section:
        facts.append(f"Поточний розділ UI: {ui_context.section.value}")

    command_lower = draft.raw_command.lower()
    if "червон" in command_lower or "красн" in command_lower:
        facts.append("Червоний статус = критична проблема або прострочення.")
    if "жовт" in command_lower or "жёлт" in command_lower or "желт" in command_lower:
        facts.append("Жовтий статус = попередження або наближення строку.")

    return "\n".join(fact for fact in facts if fact.strip())
