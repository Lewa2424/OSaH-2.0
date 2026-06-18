from pathlib import Path

from osah.application.services.ai.query_work_permit_participant_readiness import query_work_permit_participant_readiness
from osah.domain.entities.ai_command_draft import AiCommandDraft
from osah.domain.entities.ai_confirmation_view import AiConfirmationLine, AiConfirmationView
from osah.domain.entities.ai_intent_kind import AiIntentKind
from osah.domain.services.ai.detect_duplicate_ppe_issuance import detect_duplicate_ppe_issuance
from osah.domain.services.ai.normalize_ai_issue_date_text import normalize_ai_issue_date_text
from osah.domain.services.ai.normalize_ai_medical_decision import normalize_ai_medical_decision
from osah.domain.entities.training_type import TrainingType
from osah.domain.entities.training_work_risk_category import TrainingWorkRiskCategory
from osah.domain.services.format_training_type_label import format_training_type_label
from osah.domain.services.format_training_work_risk_category_label import format_training_work_risk_category_label
from osah.domain.services.ai.normalize_ai_training_type import normalize_ai_training_type


def build_ai_confirmation_view(
    draft: AiCommandDraft,
    *,
    employee_label: str,
    resolved_personnel_number: str | None,
    database_path: Path | None = None,
) -> AiConfirmationView:
    """Будує прев'ю підтвердження для AI-дії.
    Builds the confirmation preview for an AI action.
    """

    lines: list[AiConfirmationLine] = []
    warning_text = ""
    if employee_label:
        lines.append(AiConfirmationLine(label="Працівник", value=employee_label))
    elif resolved_personnel_number:
        lines.append(AiConfirmationLine(label="Табельний №", value=resolved_personnel_number))

    if draft.intent == AiIntentKind.CREATE_PPE_ISSUANCE:
        for index, item in enumerate(draft.items, start=1):
            lines.append(AiConfirmationLine(label=f"ЗІЗ {index}", value=f"{item.name} — {item.quantity} шт."))
        lines.append(AiConfirmationLine(label="Дата видачі", value=normalize_ai_issue_date_text(draft.issue_date)))
        if draft.replacement_date:
            lines.append(AiConfirmationLine(label="Дата заміни", value=normalize_ai_issue_date_text(draft.replacement_date)))
        if database_path is not None and resolved_personnel_number:
            for item in draft.items:
                if detect_duplicate_ppe_issuance(
                    database_path,
                    personnel_number=resolved_personnel_number,
                    ppe_name=item.name,
                    issue_date_text=draft.issue_date,
                ):
                    warning_text = "Увага: схожий запис ЗІЗ уже існує. Перевірте перед підтвердженням."
                    break
        return AiConfirmationView(
            title="Підтвердьте дію",
            summary="Буде створено записи ЗІЗ.",
            lines=tuple(lines),
            needs_confirmation=True,
            warning_text=warning_text,
        )

    if draft.intent == AiIntentKind.CREATE_TRAINING_RECORD:
        training_type = TrainingType(normalize_ai_training_type(draft.training_type))
        lines.append(AiConfirmationLine(label="Тип", value=format_training_type_label(training_type)))
        lines.append(AiConfirmationLine(label="Дата інструктажу", value=normalize_ai_issue_date_text(draft.issue_date)))
        if draft.work_risk_category and draft.work_risk_category != "not_applicable":
            risk = TrainingWorkRiskCategory(draft.work_risk_category)
            lines.append(
                AiConfirmationLine(
                    label="Категорія робіт",
                    value=format_training_work_risk_category_label(risk),
                )
            )
        if draft.next_control_date:
            lines.append(
                AiConfirmationLine(
                    label="Наступний контроль",
                    value=normalize_ai_issue_date_text(draft.next_control_date),
                )
            )
        if draft.conducted_by:
            lines.append(AiConfirmationLine(label="Провів", value=draft.conducted_by))
        return AiConfirmationView(
            title="Підтвердьте дію",
            summary="Буде створено запис інструктажу.",
            lines=tuple(lines),
            needs_confirmation=True,
        )

    if draft.intent == AiIntentKind.CREATE_MEDICAL_RECORD:
        lines.append(AiConfirmationLine(label="Дата початку", value=normalize_ai_issue_date_text(draft.issue_date)))
        lines.append(
            AiConfirmationLine(
                label="Дата завершення",
                value=normalize_ai_issue_date_text(draft.valid_until_date or draft.issue_date),
            )
        )
        lines.append(AiConfirmationLine(label="Рішення", value=normalize_ai_medical_decision(draft.medical_decision)))
        return AiConfirmationView(
            title="Підтвердьте дію",
            summary="Буде створено медичний запис.",
            lines=tuple(lines),
            needs_confirmation=True,
        )

    if draft.intent == AiIntentKind.UPDATE_PPE_RECORD:
        lines.append(AiConfirmationLine(label="Дія", value="Оновити запис ЗІЗ"))
        if draft.issue_date:
            lines.append(AiConfirmationLine(label="Нова дата видачі", value=normalize_ai_issue_date_text(draft.issue_date)))
        return AiConfirmationView(title="Підтвердьте дію", summary="Буде оновлено запис ЗІЗ.", lines=tuple(lines), needs_confirmation=True)

    if draft.intent == AiIntentKind.UPDATE_TRAINING_RECORD:
        lines.append(AiConfirmationLine(label="Дія", value="Оновити інструктаж"))
        if draft.issue_date:
            lines.append(AiConfirmationLine(label="Нова дата", value=normalize_ai_issue_date_text(draft.issue_date)))
        return AiConfirmationView(title="Підтвердьте дію", summary="Буде оновлено інструктаж.", lines=tuple(lines), needs_confirmation=True)

    if draft.intent == AiIntentKind.UPDATE_MEDICAL_RECORD:
        lines.append(AiConfirmationLine(label="Дія", value="Оновити медогляд"))
        if draft.valid_until_date:
            lines.append(AiConfirmationLine(label="Новий строк до", value=normalize_ai_issue_date_text(draft.valid_until_date)))
        if draft.issue_date:
            lines.append(AiConfirmationLine(label="Нова дата початку", value=normalize_ai_issue_date_text(draft.issue_date)))
        return AiConfirmationView(title="Підтвердьте дію", summary="Буде оновлено медичний запис.", lines=tuple(lines), needs_confirmation=True)

    if draft.intent == AiIntentKind.UPDATE_EMPLOYEE_FIELDS and draft.employee_field_updates is not None:
        updates = draft.employee_field_updates
        if updates.position_name:
            lines.append(AiConfirmationLine(label="Нова посада", value=updates.position_name))
        if updates.department_name:
            lines.append(AiConfirmationLine(label="Новий підрозділ", value=updates.department_name))
        if updates.employment_status:
            lines.append(AiConfirmationLine(label="Новий статус", value=updates.employment_status))
        return AiConfirmationView(title="Підтвердьте дію", summary="Буде оновлено картку працівника.", lines=tuple(lines), needs_confirmation=True)

    if draft.intent == AiIntentKind.CREATE_WORK_PERMIT_DRAFT:
        lines.append(AiConfirmationLine(label="Номер", value=(draft.permit_number or draft.permit_query or "")))
        lines.append(AiConfirmationLine(label="Вид робіт", value=(draft.work_kind or "")))
        lines.append(AiConfirmationLine(label="Початок", value=(draft.starts_at_text or "")))
        lines.append(AiConfirmationLine(label="Завершення", value=(draft.ends_at_text or "")))
        return AiConfirmationView(title="Підтвердьте дію", summary="Буде створено чернетку наряду.", lines=tuple(lines), needs_confirmation=True)

    if draft.intent in {AiIntentKind.ADD_WORK_PERMIT_PARTICIPANT, AiIntentKind.REMOVE_WORK_PERMIT_PARTICIPANT}:
        action = "Додати" if draft.intent == AiIntentKind.ADD_WORK_PERMIT_PARTICIPANT else "Прибрати"
        lines.append(AiConfirmationLine(label="Наряд", value=(draft.permit_number or draft.permit_query or "")))
        lines.append(AiConfirmationLine(label="Дія", value=f"{action} учасника"))
        if database_path is not None and draft.intent == AiIntentKind.ADD_WORK_PERMIT_PARTICIPANT and resolved_personnel_number:
            readiness = query_work_permit_participant_readiness(
                database_path,
                permit_number=draft.permit_number,
                permit_query=draft.permit_query,
            )
            if readiness is not None:
                participant = next(
                    (row for row in readiness.participants if row.personnel_number == resolved_personnel_number),
                    None,
                )
                if participant is not None and not participant.ready:
                    warning_text = f"Увага: {participant.employee_name} не готовий до робіт."
        return AiConfirmationView(
            title="Підтвердьте дію",
            summary="Буде змінено склад наряду.",
            lines=tuple(lines),
            needs_confirmation=True,
            warning_text=warning_text,
        )

    return AiConfirmationView(
        title="Підтвердьте дію",
        summary="Перевірте підготовлену дію.",
        lines=tuple(lines),
        needs_confirmation=draft.needs_confirmation,
    )
