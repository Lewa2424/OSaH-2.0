import re

from osah.domain.entities.ai_item_draft import AiItemDraft
from osah.domain.services.ai.ai_relative_date_markers import mentions_current_date
from osah.domain.services.ai.command_verb_tokens import has_nav_verb_lead, sanitize_employee_query
from osah.domain.services.ai.extract_bulk_department_span_from_command import (
    extract_bulk_department_span_from_command,
)
from osah.domain.services.ai.extract_bulk_position_span_from_command import (
    extract_bulk_position_span_from_command,
)
from osah.domain.services.ai.extract_employee_query_from_command import extract_employee_query_from_command
from osah.domain.services.ai.matches_module_status_list_query import matches_module_status_list_query
from osah.domain.entities.ai_semantic_audience_spec import AiSemanticAudienceSpec
from osah.domain.entities.ai_semantic_audience_type import AiSemanticAudienceType
from osah.domain.entities.ai_semantic_condition import AiSemanticCondition
from osah.domain.entities.ai_semantic_condition_type import AiSemanticConditionType
from osah.domain.entities.ai_semantic_draft import AiSemanticDraft
from osah.domain.entities.ai_semantic_intent import AiSemanticIntent
from osah.domain.entities.ai_semantic_mode import AiSemanticMode
from osah.domain.entities.ai_semantic_module import AiSemanticModule
from osah.domain.entities.ai_semantic_payload import AiSemanticPayload


_DEPARTMENT_AUDIENCE_PATTERN = re.compile(
    r"(?:"
    r"(?:подразделени(?:ю|я|е)|отдел(?:у|а)?|участ(?:ку|ка)|служб(?:е|ы)|цех(?:у|а)|"
    r"підрозділ(?:у|а)?|дільниц(?:і|ю)|служб(?:і|и))"
    r"\s+"
    r")"
    r"(.+?)"
    r"(?=\s+(?:по\s+\d|по\s+пар|с\s+сегод|за\s+сегод|сьогодні|з\s+сьогодні|"
    r"каск|ботин|черевик|перчат|рукавиц|роб|спецодяг|инструктаж|інструктаж|мед|$))",
    re.IGNORECASE,
)
_WORK_PERMIT_PARTICIPANTS_PATTERN = re.compile(
    r"(?:участник(?:ам|и|ов)|учасник(?:ам|и|ів)).{0,30}(?:наряд(?:а|у)?|наряду|№)\s*№?\s*(\d+)",
    re.IGNORECASE,
)
_PERMIT_NUMBER_PATTERN = re.compile(r"(?:наряд(?:а|у)?|наряду|№)\s*№?\s*(\d+)", re.IGNORECASE)
_EMPLOYEE_LIST_AFTER_VERB_PATTERN = re.compile(
    r"(?:переведи|перевести|переведи|перевести|обнови|онови)\s+(.+?)\s+"
    r"(?=(?:на\s+участ|на\s+дільниц|прошли|пройшли|:))",
    re.IGNORECASE,
)
_SINGLE_EMPLOYEE_PATTERN = re.compile(
    r"(?:занеси|внеси|добавь|додай|поставь|постав|обнови|онови|выдай|видай|дай|раздай|впиши|выпиши)"
    r"\s+([А-ЯІЇЄҐA-Z][а-яіїєґa-z-]+)",
    re.IGNORECASE,
)
_NEW_EMPLOYEE_PATTERN = re.compile(
    r"нов(?:ого|ий)\s+сотрудник(?:а)?\s*:\s*(.+?)(?=,\s*[^,]+,\s*[^,]+,|\s*$)",
    re.IGNORECASE,
)
_POSITION_AFTER_NAME_PATTERN = re.compile(r"нов(?:ого|ий)\s+сотрудник(?:а)?\s*:\s*[^,]+,\s*([^,]+)", re.IGNORECASE)
_DEPARTMENT_AFTER_POSITION_PATTERN = re.compile(r"нов(?:ого|ий)\s+сотрудник(?:а)?\s*:\s*[^,]+,[^,]+,\s*([^,]+)", re.IGNORECASE)
_TRANSFER_DEPARTMENT_PATTERN = re.compile(
    r"на\s+(?:участ(?:ок|ок)|дільниц(?:ю|ю)|подразделение|підрозділ)\s+(.+?)"
    r"(?=\s+(?:с|з)\s+|,\s*долж|,\s*посад|$)",
    re.IGNORECASE,
)
_PPE_ITEM_PATTERN = re.compile(r"\b(каск\w*|ботинк\w*|черевик\w*|роб\w*|перчат\w*|рукавиц\w*)\b", re.IGNORECASE)
_TRAINING_TYPE_PATTERN = re.compile(r"\b(повторн\w*|первичн\w*|первинн\w*|целев\w*|цільов\w*)\s+инструктаж", re.IGNORECASE)
_CONDUCTED_BY_PATTERN = re.compile(r"пров[её]л\s+([А-ЯІЇЄҐA-Z][а-яіїєґa-z-]+)", re.IGNORECASE)
_TOPIC_PATTERN = re.compile(r"(?:тема|на)\s+(.+?)(?=,\s*дата|,\s*пров|,\s*$|$)", re.IGNORECASE)


def build_ai_semantic_draft_from_command(command_text: str) -> AiSemanticDraft | None:
    """Будує смисловий чернетковий опис AI-команди з живої фрази.
    Builds a semantic AI command draft from a natural-language command.
    """

    raw_command = command_text.strip()
    if not raw_command:
        return None

    lowered = raw_command.lower()
    if _is_employee_cleanup_query(lowered):
        return _build_employee_cleanup(raw_command)
    if _is_employee_create_query(lowered):
        return _build_employee_create(raw_command)
    if has_nav_verb_lead(raw_command):
        return None
    if lowered.startswith(("переведи ", "перевести ")):
        return _build_employee_site_batch(raw_command)
    if _is_medical_query(lowered):
        return _build_medical_semantic(raw_command)
    if _is_training_query(lowered):
        return _build_training_semantic(raw_command)
    if _is_ppe_query(lowered):
        return _build_ppe_semantic(raw_command)
    if _is_work_permit_query(lowered):
        return _build_work_permit_semantic(raw_command)
    return None


def _build_employee_cleanup(raw_command: str) -> AiSemanticDraft:
    filters = []
    lowered = raw_command.lower()
    if "без участка" in lowered or "без дільниц" in lowered or "без підрозділ" in lowered:
        filters.append("missing_department")
    if "должност" in lowered or "посад" in lowered:
        filters.append("missing_position")
    return AiSemanticDraft(
        intent=AiSemanticIntent.PREPARE_EMPLOYEE_DATA_CLEANUP,
        raw_command=raw_command,
        module=AiSemanticModule.EMPLOYEES,
        mode=AiSemanticMode.READ_ONLY,
        audience=AiSemanticAudienceSpec(
            audience_type=AiSemanticAudienceType.EMPLOYEE_FILTER,
            filters=tuple(filters),
        ),
    )


def _build_employee_create(raw_command: str) -> AiSemanticDraft:
    full_name = _first_group(_NEW_EMPLOYEE_PATTERN, raw_command)
    position_name = _first_group(_POSITION_AFTER_NAME_PATTERN, raw_command)
    department_name = _first_group(_DEPARTMENT_AFTER_POSITION_PATTERN, raw_command)
    return AiSemanticDraft(
        intent=AiSemanticIntent.CREATE_EMPLOYEE,
        raw_command=raw_command,
        module=AiSemanticModule.EMPLOYEES,
        mode=AiSemanticMode.DRAFT_ONLY,
        payload=AiSemanticPayload(
            full_name=full_name,
            position_name=position_name,
            department_name=department_name,
            effective_date=_extract_date_marker(raw_command),
        ),
        needs_confirmation=True,
    )


def _build_employee_site_batch(raw_command: str) -> AiSemanticDraft:
    employee_queries = _split_person_names(_first_group(_EMPLOYEE_LIST_AFTER_VERB_PATTERN, raw_command) or "")
    department_query = _first_group(_TRANSFER_DEPARTMENT_PATTERN, raw_command)
    conditions = ()
    if re.search(r"должност[ьи]\s+не\s+менять|посад[ау]\s+не\s+змін", raw_command, re.IGNORECASE):
        conditions = (AiSemanticCondition(AiSemanticConditionType.DO_NOT_CHANGE_POSITION),)
    return AiSemanticDraft(
        intent=AiSemanticIntent.UPDATE_EMPLOYEE_SITE_BATCH,
        raw_command=raw_command,
        module=AiSemanticModule.EMPLOYEES,
        mode=AiSemanticMode.PREVIEW_THEN_CONFIRM,
        audience=AiSemanticAudienceSpec(
            audience_type=AiSemanticAudienceType.EMPLOYEE_LIST,
            employee_queries=employee_queries,
        ),
        payload=AiSemanticPayload(
            department_name=department_query,
            effective_date=_extract_date_marker(raw_command),
        ),
        conditions=conditions,
        needs_confirmation=True,
    )


def _build_training_semantic(raw_command: str) -> AiSemanticDraft:
    permit_number = _first_group(_PERMIT_NUMBER_PATTERN, raw_command)
    department_query = _first_group(_DEPARTMENT_AUDIENCE_PATTERN, raw_command) or extract_bulk_department_span_from_command(raw_command)
    position_query = extract_bulk_position_span_from_command(raw_command)
    training_type = _normalize_training_type(_first_group(_TRAINING_TYPE_PATTERN, raw_command))
    payload = AiSemanticPayload(
        event_date=_extract_date_marker(raw_command),
        training_type=training_type,
        conducted_by=_first_group(_CONDUCTED_BY_PATTERN, raw_command),
        topic=_extract_topic(raw_command),
    )
    if permit_number:
        return AiSemanticDraft(
            intent=AiSemanticIntent.CREATE_TARGET_TRAINING_FOR_WORK_PERMIT,
            raw_command=raw_command,
            module=AiSemanticModule.TRAININGS,
            mode=AiSemanticMode.PREVIEW_THEN_CONFIRM,
            audience=AiSemanticAudienceSpec(
                audience_type=AiSemanticAudienceType.WORK_PERMIT_PARTICIPANTS,
                permit_number=permit_number,
            ),
            payload=payload,
            needs_confirmation=True,
        )
    if department_query or position_query or _has_group_marker(raw_command):
        audience_type = AiSemanticAudienceType.DEPARTMENT if department_query else AiSemanticAudienceType.EMPLOYEE_FILTER
        return AiSemanticDraft(
            intent=AiSemanticIntent.CREATE_TRAINING_BATCH,
            raw_command=raw_command,
            module=AiSemanticModule.TRAININGS,
            mode=AiSemanticMode.PREVIEW_THEN_CONFIRM,
            audience=AiSemanticAudienceSpec(
                audience_type=audience_type,
                department_query=department_query,
                position_query=position_query,
                filters=_extract_employee_filters(raw_command),
            ),
            payload=payload,
            needs_confirmation=True,
        )
    return AiSemanticDraft(
        intent=AiSemanticIntent.CREATE_TRAINING_RECORD,
        raw_command=raw_command,
        module=AiSemanticModule.TRAININGS,
        mode=AiSemanticMode.CONFIRM_THEN_EXECUTE,
        audience=AiSemanticAudienceSpec(
            audience_type=AiSemanticAudienceType.EMPLOYEE,
            employee_queries=(_extract_single_employee_query(raw_command),),
        ),
        payload=payload,
        needs_confirmation=True,
    )


def _build_ppe_semantic(raw_command: str) -> AiSemanticDraft:
    permit_number = _first_group(_WORK_PERMIT_PARTICIPANTS_PATTERN, raw_command)
    department_query = _first_group(_DEPARTMENT_AUDIENCE_PATTERN, raw_command) or extract_bulk_department_span_from_command(raw_command)
    position_query = extract_bulk_position_span_from_command(raw_command)
    items = _extract_ppe_items(raw_command)
    conditions = ()
    if re.search(r"если\s+у\s+них\s+нет|якщо\s+немає|нет\s+действующ", raw_command, re.IGNORECASE):
        conditions = (AiSemanticCondition(AiSemanticConditionType.SKIP_IF_ACTIVE_PPE_EXISTS),)

    if permit_number:
        return AiSemanticDraft(
            intent=AiSemanticIntent.CREATE_PPE_ISSUANCE_FOR_WORK_PERMIT_PARTICIPANTS,
            raw_command=raw_command,
            module=AiSemanticModule.PPE,
            mode=AiSemanticMode.PREVIEW_THEN_CONFIRM,
            audience=AiSemanticAudienceSpec(
                audience_type=AiSemanticAudienceType.WORK_PERMIT_PARTICIPANTS,
                permit_number=permit_number,
            ),
            payload=AiSemanticPayload(
                event_date=_extract_date_marker(raw_command),
                items=items,
                ppe_item_query=items[0].name if items else None,
            ),
            conditions=conditions,
            needs_confirmation=True,
        )
    if department_query:
        return AiSemanticDraft(
            intent=AiSemanticIntent.CREATE_PPE_ISSUANCE,
            raw_command=raw_command,
            module=AiSemanticModule.PPE,
            mode=AiSemanticMode.PREVIEW_THEN_CONFIRM,
            audience=AiSemanticAudienceSpec(
                audience_type=AiSemanticAudienceType.DEPARTMENT,
                department_query=department_query,
            ),
            payload=AiSemanticPayload(
                event_date=_extract_date_marker(raw_command),
                items=items,
                ppe_item_query=items[0].name if items else None,
            ),
            needs_confirmation=True,
        )
    if position_query:
        return AiSemanticDraft(
            intent=AiSemanticIntent.CREATE_PPE_ISSUANCE,
            raw_command=raw_command,
            module=AiSemanticModule.PPE,
            mode=AiSemanticMode.PREVIEW_THEN_CONFIRM,
            audience=AiSemanticAudienceSpec(
                audience_type=AiSemanticAudienceType.EMPLOYEE_FILTER,
                position_query=position_query,
            ),
            payload=AiSemanticPayload(
                event_date=_extract_date_marker(raw_command),
                items=items,
                ppe_item_query=items[0].name if items else None,
            ),
            needs_confirmation=True,
        )
    if re.search(r"\bзамени|заміни|replace\b", raw_command, re.IGNORECASE):
        return AiSemanticDraft(
            intent=AiSemanticIntent.REPLACE_PPE_ITEM,
            raw_command=raw_command,
            module=AiSemanticModule.PPE,
            mode=AiSemanticMode.CONFIRM_THEN_EXECUTE,
            audience=AiSemanticAudienceSpec(
                audience_type=AiSemanticAudienceType.EMPLOYEE,
                employee_queries=(_extract_single_employee_query(raw_command),),
            ),
            payload=AiSemanticPayload(
                event_date=_extract_date_marker(raw_command),
                items=items,
                ppe_item_query=items[0].name if items else None,
                replacement_reason=_extract_replacement_reason(raw_command),
            ),
            conditions=(AiSemanticCondition(AiSemanticConditionType.DO_NOT_DELETE_EXISTING_RECORD),),
            needs_confirmation=True,
        )
    return AiSemanticDraft(
        intent=AiSemanticIntent.CREATE_PPE_ISSUANCE,
        raw_command=raw_command,
        module=AiSemanticModule.PPE,
        mode=AiSemanticMode.CONFIRM_THEN_EXECUTE,
        audience=AiSemanticAudienceSpec(
            audience_type=AiSemanticAudienceType.EMPLOYEE,
            employee_queries=(_extract_single_employee_query(raw_command),),
        ),
        payload=AiSemanticPayload(
            event_date=_extract_date_marker(raw_command),
            items=items,
            ppe_item_query=items[0].name if items else None,
        ),
        needs_confirmation=True,
    )


def _build_medical_semantic(raw_command: str) -> AiSemanticDraft:
    employee_queries = _extract_medical_employee_queries(raw_command)
    payload = AiSemanticPayload(
        event_date=_extract_date_marker(raw_command),
        valid_until_date=_extract_valid_until(raw_command),
        restriction_note=_extract_medical_restriction(raw_command),
    )
    if len(employee_queries) > 1:
        return AiSemanticDraft(
            intent=AiSemanticIntent.UPDATE_MEDICAL_BATCH,
            raw_command=raw_command,
            module=AiSemanticModule.MEDICAL,
            mode=AiSemanticMode.PREVIEW_THEN_CONFIRM,
            audience=AiSemanticAudienceSpec(
                audience_type=AiSemanticAudienceType.EMPLOYEE_LIST,
                employee_queries=employee_queries,
            ),
            payload=payload,
            needs_confirmation=True,
        )
    if payload.restriction_note:
        return AiSemanticDraft(
            intent=AiSemanticIntent.UPDATE_MEDICAL_RESTRICTION,
            raw_command=raw_command,
            module=AiSemanticModule.MEDICAL,
            mode=AiSemanticMode.CONFIRM_THEN_EXECUTE,
            audience=AiSemanticAudienceSpec(
                audience_type=AiSemanticAudienceType.EMPLOYEE,
                employee_queries=employee_queries,
            ),
            payload=payload,
            conditions=(AiSemanticCondition(AiSemanticConditionType.UNTIL_NEXT_MEDICAL_EXAM),)
            if "повторного осмотра" in raw_command.lower()
            else (),
            needs_confirmation=True,
        )
    return AiSemanticDraft(
        intent=AiSemanticIntent.CREATE_OR_UPDATE_MEDICAL_RECORD,
        raw_command=raw_command,
        module=AiSemanticModule.MEDICAL,
        mode=AiSemanticMode.CONFIRM_THEN_EXECUTE,
        audience=AiSemanticAudienceSpec(
            audience_type=AiSemanticAudienceType.EMPLOYEE,
            employee_queries=employee_queries,
        ),
        payload=payload,
        needs_confirmation=True,
    )


def _build_work_permit_semantic(raw_command: str) -> AiSemanticDraft:
    head_command = _head_before_participants_clause(raw_command)
    permit_number = _extract_permit_identifier(head_command) or _extract_permit_identifier(raw_command)
    if re.search(r"(?:додай|добавь).+(?:наряд|наряду)", raw_command, re.IGNORECASE):
        employee_query = _extract_single_employee_query(raw_command)
        return AiSemanticDraft(
            intent=AiSemanticIntent.UPDATE_WORK_PERMIT_PARTICIPANTS,
            raw_command=raw_command,
            module=AiSemanticModule.WORK_PERMITS,
            mode=AiSemanticMode.CONFIRM_THEN_EXECUTE,
            audience=AiSemanticAudienceSpec(permit_number=permit_number),
            payload=AiSemanticPayload(
                add_employee_queries=(employee_query,) if employee_query else (),
            ),
            needs_confirmation=True,
        )
    if re.search(r"(?:прибери|убери).+(?:наряд|наряду|з\s+наряд)", raw_command, re.IGNORECASE):
        employee_query = _extract_single_employee_query(raw_command)
        return AiSemanticDraft(
            intent=AiSemanticIntent.UPDATE_WORK_PERMIT_PARTICIPANTS,
            raw_command=raw_command,
            module=AiSemanticModule.WORK_PERMITS,
            mode=AiSemanticMode.CONFIRM_THEN_EXECUTE,
            audience=AiSemanticAudienceSpec(permit_number=permit_number),
            payload=AiSemanticPayload(
                remove_employee_queries=(employee_query,) if employee_query else (),
            ),
            needs_confirmation=True,
        )
    if re.search(r"\bдобавь\b.+\bубери\b|\bдодай\b.+\bприбери\b", raw_command, re.IGNORECASE):
        return AiSemanticDraft(
            intent=AiSemanticIntent.UPDATE_WORK_PERMIT_PARTICIPANTS,
            raw_command=raw_command,
            module=AiSemanticModule.WORK_PERMITS,
            mode=AiSemanticMode.PREVIEW_THEN_CONFIRM,
            audience=AiSemanticAudienceSpec(permit_number=permit_number),
            payload=AiSemanticPayload(
                add_employee_queries=_extract_names_after_marker(raw_command, "добавь"),
                remove_employee_queries=_extract_names_after_marker(raw_command, "убери"),
            ),
            conditions=(AiSemanticCondition(AiSemanticConditionType.ONLY_IF_WORK_PERMIT_IS_DRAFT),)
            if "чернов" in raw_command.lower()
            else (),
            needs_confirmation=True,
        )
    if re.search(r"мер[ыи]\s+безопасн|заходи\s+безпек", raw_command, re.IGNORECASE):
        return AiSemanticDraft(
            intent=AiSemanticIntent.ADD_WORK_PERMIT_SAFETY_MEASURES,
            raw_command=raw_command,
            module=AiSemanticModule.WORK_PERMITS,
            mode=AiSemanticMode.DRAFT_ONLY,
            payload=AiSemanticPayload(
                work_kind=_extract_work_kind(raw_command),
                safety_measures=_extract_safety_measures(raw_command),
            ),
            needs_confirmation=True,
        )
    return AiSemanticDraft(
        intent=AiSemanticIntent.CREATE_WORK_PERMIT_DRAFT,
        raw_command=raw_command,
        module=AiSemanticModule.WORK_PERMITS,
        mode=AiSemanticMode.DRAFT_ONLY,
        audience=AiSemanticAudienceSpec(
            audience_type=AiSemanticAudienceType.EMPLOYEE_LIST,
            employee_queries=_extract_participants(raw_command),
            permit_number=permit_number,
        ),
        payload=AiSemanticPayload(
            event_date=_extract_date_marker(raw_command),
            starts_at_text=_extract_time(raw_command),
            work_kind=_extract_work_kind(head_command),
            work_location=_first_group(_DEPARTMENT_AUDIENCE_PATTERN, head_command),
        ),
        needs_confirmation=True,
    )


def _is_employee_cleanup_query(lowered: str) -> bool:
    return "найди" in lowered and ("без участка" in lowered or "без должност" in lowered)


def _is_employee_create_query(lowered: str) -> bool:
    return "нового сотрудник" in lowered or "новый сотрудник" in lowered


def _is_training_query(lowered: str) -> bool:
    if matches_module_status_list_query(lowered):
        return False
    return "инструктаж" in lowered or "інструктаж" in lowered


def _is_ppe_query(lowered: str) -> bool:
    if matches_module_status_list_query(lowered):
        return False
    if lowered.startswith(("кому ", "кто ", "хто ", "у кого ", "найди ", "покажи ", "показати ")):
        return False
    return bool(_PPE_ITEM_PATTERN.search(lowered)) or "сиз" in lowered or "зіз" in lowered or "зиз" in lowered


def _is_medical_query(lowered: str) -> bool:
    return "медосмотр" in lowered or "медогляд" in lowered or "ограничение" in lowered


def _is_work_permit_query(lowered: str) -> bool:
    return "наряд" in lowered or "строповк" in lowered or "меры безопасности" in lowered


def _has_group_marker(raw_command: str) -> bool:
    return bool(re.search(r"\b(?:всем|усім|всім|участникам|учасникам|сотрудникам|работникам)\b", raw_command, re.IGNORECASE))


def _extract_ppe_items(raw_command: str) -> tuple[AiItemDraft, ...]:
    names = []
    for match in _PPE_ITEM_PATTERN.finditer(raw_command):
        normalized = _normalize_ppe_item(match.group(1))
        if normalized not in names:
            names.append(normalized)
    return tuple(AiItemDraft(name=name, quantity=1) for name in names)


def _normalize_ppe_item(raw_name: str) -> str:
    lowered = raw_name.lower()
    if lowered.startswith("роб"):
        return "роба"
    if lowered.startswith("ботин"):
        return "ботинки"
    if lowered.startswith("черев"):
        return "черевики"
    if lowered.startswith("перчат"):
        return "перчатки"
    if lowered.startswith("рукав"):
        return "рукавиці"
    if lowered.startswith("каск"):
        return "каска"
    return raw_name.strip()


def _extract_date_marker(raw_command: str) -> str | None:
    lowered = raw_command.lower()
    if mentions_current_date(raw_command):
        return "сьогодні"
    if "вчера" in lowered or "вчора" in lowered:
        return "вчора"
    if "понедельник" in lowered or "понеділок" in lowered:
        return "next_monday"
    if "этой недел" in lowered or "цього тиж" in lowered:
        return "current_week"
    date_match = re.search(r"\b(\d{1,2}\s+[а-яіїєґ]+)\b", raw_command, re.IGNORECASE)
    if date_match:
        return date_match.group(1).strip()
    return None


def _extract_valid_until(raw_command: str) -> str | None:
    lowered = raw_command.lower()
    if "на год" in lowered or "на рік" in lowered:
        return "plus_1_year"
    if "до конца следующего года" in lowered:
        return "end_of_next_year"
    return None


def _extract_single_employee_query(raw_command: str) -> str:
    extracted = sanitize_employee_query(extract_employee_query_from_command(raw_command))
    if extracted:
        return extracted
    match = _SINGLE_EMPLOYEE_PATTERN.search(raw_command)
    if match:
        return sanitize_employee_query(match.group(1).strip()) or ""
    words = re.findall(r"\b[А-ЯІЇЄҐ][а-яіїєґ-]+\b", raw_command)
    for word in words:
        cleaned = sanitize_employee_query(word)
        if cleaned:
            return cleaned
    return ""


def _extract_medical_employee_queries(raw_command: str) -> tuple[str, ...]:
    before_colon = raw_command.split(":", 1)[0]
    names = re.findall(r"\b[А-ЯІЇЄҐ][а-яіїєґ-]+\b", before_colon)
    ignored = {"Обнови", "Онови", "Занеси", "Поставь"}
    cleaned = tuple(name for name in names if name not in ignored)
    return cleaned or (_extract_single_employee_query(raw_command),)


def _split_person_names(raw_value: str) -> tuple[str, ...]:
    if not raw_value.strip():
        return ()
    normalized = re.sub(r"\s+(?:и|та|і)\s+", ",", raw_value)
    return tuple(part.strip(" ,.;:") for part in normalized.split(",") if part.strip(" ,.;:"))


def _extract_topic(raw_command: str) -> str | None:
    topic = _first_group(_TOPIC_PATTERN, raw_command)
    if topic:
        return topic
    if "стандарт" in raw_command.lower():
        return "стандартная"
    return None


def _normalize_training_type(raw_type: str | None) -> str | None:
    if not raw_type:
        return None
    lowered = raw_type.lower()
    if "повтор" in lowered:
        return "repeated"
    if "перв" in lowered:
        return "primary"
    if "цел" in lowered or "ціль" in lowered:
        return "target"
    return raw_type


def _extract_employee_filters(raw_command: str) -> tuple[str, ...]:
    filters = []
    lowered = raw_command.lower()
    if "новым сотрудник" in lowered or "новим працівник" in lowered:
        filters.append("new_employees")
    if "этой недел" in lowered or "цього тиж" in lowered:
        filters.append("accepted_current_week")
    return tuple(filters)


def _extract_replacement_reason(raw_command: str) -> str | None:
    match = re.search(r"стар\w+\s+(.+?)(?=,\s*дат|$)", raw_command, re.IGNORECASE)
    return match.group(1).strip() if match else None


def _extract_medical_restriction(raw_command: str) -> str | None:
    lowered = raw_command.lower()
    if "ограничен" not in lowered and "обмежен" not in lowered:
        return None
    match = re.search(r"ограничение\s*:\s*(.+?)(?=\.|$)", raw_command, re.IGNORECASE)
    if match is not None:
        return match.group(1).strip()
    match = re.search(
        r"(?:ограничен\w*|обмежен\w*)\s*(?::\s*)?(?:по\s+)?(.+?)(?=\.|$)",
        raw_command,
        re.IGNORECASE,
    )
    return match.group(1).strip() if match else None


def _extract_names_after_marker(raw_command: str, marker: str) -> tuple[str, ...]:
    match = re.search(rf"{marker}\s+(.+?)(?=\s+(?:и\s+)?(?:убери|добавь|если|$))", raw_command, re.IGNORECASE)
    return _split_person_names(match.group(1)) if match else ()


def _extract_work_kind(raw_command: str) -> str | None:
    lowered = raw_command.lower()
    if "погрузк" in lowered:
        return "погрузка металлопроката"
    if "строповк" in lowered:
        return "строповка"
    if "допуск" in lowered or "наряд" in lowered:
        return "Наряд-допуск"
    return None


def _head_before_participants_clause(raw_command: str) -> str:
    """Обрізає хвіст з переліком учасників перед витягом імені/виду робіт.
    Truncates the participants tail before extracting permit name or work kind.
    """

    match = re.search(
        r",\s*(?:участник(?:и|ов|ам)|учасник(?:и|ів|ам))\s*:?",
        raw_command,
        re.IGNORECASE,
    )
    if match is None:
        return raw_command
    return raw_command[: match.start()].strip()


def _extract_permit_identifier(raw_command: str) -> str | None:
    """Витягує номер або назву наряду з фрази створення.
    Extracts a work permit number or label from a create phrase.
    """

    named_match = re.search(
        r"(?:именем|названием|номером|назвою|назв[ао]й)\s+([A-ZА-ЯІЇЄҐ0-9][\w-]{2,})",
        raw_command,
        re.IGNORECASE,
    )
    if named_match is not None:
        return named_match.group(1).strip()
    numeric = _first_group(_PERMIT_NUMBER_PATTERN, raw_command)
    if numeric:
        return numeric
    labeled_match = re.search(r"№\s*([A-ZА-ЯІЇЄҐ0-9][\w-]*)", raw_command, re.IGNORECASE)
    if labeled_match is not None:
        return labeled_match.group(1).strip()
    return None


def _extract_safety_measures(raw_command: str) -> tuple[str, ...]:
    if ":" not in raw_command:
        return ()
    tail = raw_command.split(":", 1)[1]
    return tuple(part.strip(" ,.;") for part in tail.split(",") if part.strip(" ,.;"))


def _extract_participants(raw_command: str) -> tuple[str, ...]:
    match = re.search(
        r"(?:участник(?:и|ов|ам)|учасник(?:и|ів|ам))\s*:?\s*(.+?)(?=\.|$)",
        raw_command,
        re.IGNORECASE,
    )
    if match is None:
        return ()
    tail = match.group(1)
    personnel_numbers = re.findall(r"\b(\d{4})\b", tail)
    if personnel_numbers:
        return tuple(personnel_numbers)
    return _split_person_names(tail)


def _extract_time(raw_command: str) -> str | None:
    match = re.search(r"\b(\d{1,2})\s*(?:утра|:00)\b", raw_command, re.IGNORECASE)
    if not match:
        return None
    return f"{int(match.group(1)):02d}:00"


def _first_group(pattern: re.Pattern[str], text: str) -> str | None:
    match = pattern.search(text)
    if match is None:
        return None
    return match.group(1).strip(" ,.;:")
