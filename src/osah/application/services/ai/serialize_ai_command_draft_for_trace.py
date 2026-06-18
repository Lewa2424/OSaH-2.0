from osah.domain.entities.ai_command_draft import AiCommandDraft


def serialize_ai_command_draft_for_trace(draft: AiCommandDraft | None) -> dict[str, object]:
    """Готує чернетку AI-команди для trace-log без зайвих вкладених об'єктів.
    Prepares an AI command draft for trace logging.
    """

    if draft is None:
        return {}

    payload: dict[str, object] = {
        "intent": draft.intent.value,
        "source": draft.source,
        "employee_query": draft.employee_query,
        "department_query": draft.department_query,
        "position_query": draft.position_query,
        "personnel_number": draft.personnel_number,
        "ppe_item_query": draft.ppe_item_query,
        "training_type": draft.training_type,
        "issue_date": draft.issue_date,
        "next_control_date": draft.next_control_date,
        "work_risk_category": draft.work_risk_category,
        "use_manual_next_control_date": draft.use_manual_next_control_date,
        "valid_until_date": draft.valid_until_date,
        "module_key": draft.module_key,
        "needs_confirmation": draft.needs_confirmation,
        "clarification_message": draft.clarification_message,
    }
    if draft.items:
        payload["items"] = [{"name": item.name, "quantity": item.quantity} for item in draft.items]
    if draft.bulk_audience_spec is not None:
        spec = draft.bulk_audience_spec
        payload["bulk_audience_spec"] = {
            "employee_queries": list(spec.employee_queries),
            "department_query": spec.department_query,
            "filter_key": spec.filter_key,
            "permit_number": spec.permit_number,
        }
    return {key: value for key, value in payload.items() if value not in (None, "", [], {})}
