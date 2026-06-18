from osah.domain.entities.ai_intent_kind import AiIntentKind

_FORBIDDEN_WRITE_INTENTS = frozenset(
    {
        "delete_record",
        "approve_port_r",
        "close_critical_risk",
        "change_access_role",
    }
)

_NAVIGATION_INTENTS = frozenset(
    {
        AiIntentKind.NAVIGATE_SECTION,
        AiIntentKind.SHOW_OVERDUE,
        AiIntentKind.OPEN_EMPLOYEE_CARD,
    }
)

_QUERY_INTENTS = frozenset(
    {
        AiIntentKind.QUERY_MISSING_PPE,
        AiIntentKind.QUERY_DAILY_FOCUS,
        AiIntentKind.QUERY_EMPLOYEE_READINESS,
        AiIntentKind.QUERY_OVERDUE_SUMMARY,
        AiIntentKind.QUERY_SECTION_PROBLEMS,
        AiIntentKind.QUERY_EMPLOYEE_RECORDS,
        AiIntentKind.QUERY_EMPLOYEES_FILTER,
        AiIntentKind.QUERY_MODULE_STATUS,
        AiIntentKind.QUERY_WORK_PERMIT_LIST,
        AiIntentKind.QUERY_WORK_PERMIT_READINESS,
        AiIntentKind.QUERY_PORT_R_GAPS,
    }
)

_ANSWER_INTENTS = _QUERY_INTENTS | {AiIntentKind.GENERATE_REPORT_TEXT, AiIntentKind.EXPLAIN_HELP}

_BULK_WRITE_INTENTS = frozenset(
    {
        AiIntentKind.BULK_CREATE_TRAINING_RECORD,
        AiIntentKind.BULK_CREATE_PPE_ISSUANCE,
        AiIntentKind.BULK_CREATE_MEDICAL_RECORD,
        AiIntentKind.BULK_UPDATE_EMPLOYEE_FIELDS,
        AiIntentKind.BULK_ADD_WORK_PERMIT_PARTICIPANTS,
    }
)

_WRITE_INTENTS = frozenset(
    {
        AiIntentKind.CREATE_PPE_ISSUANCE,
        AiIntentKind.CREATE_TRAINING_RECORD,
        AiIntentKind.CREATE_MEDICAL_RECORD,
        AiIntentKind.UPDATE_PPE_RECORD,
        AiIntentKind.UPDATE_TRAINING_RECORD,
        AiIntentKind.UPDATE_MEDICAL_RECORD,
        AiIntentKind.UPDATE_EMPLOYEE_FIELDS,
        AiIntentKind.CREATE_WORK_PERMIT_DRAFT,
        AiIntentKind.ADD_WORK_PERMIT_PARTICIPANT,
        AiIntentKind.REMOVE_WORK_PERMIT_PARTICIPANT,
    }
) | _BULK_WRITE_INTENTS


def is_ai_navigation_intent(intent: AiIntentKind) -> bool:
    """Перевіряє, чи intent лише відкриває екран.
    Checks whether the intent only opens a screen.
    """

    return intent in _NAVIGATION_INTENTS


def is_ai_query_intent(intent: AiIntentKind) -> bool:
    """Перевіряє, чи intent повертає текстову відповідь із даних.
    Checks whether the intent returns a text answer from data.
    """

    return intent in _QUERY_INTENTS


def is_ai_answer_intent(intent: AiIntentKind) -> bool:
    """Перевіряє, чи intent формує текстову відповідь без запису в БД.
    Checks whether the intent produces a text answer without DB writes.
    """

    return intent in _ANSWER_INTENTS


def is_ai_bulk_intent(intent: AiIntentKind) -> bool:
    """Перевіряє, чи intent — масова write-дія.
    Checks whether the intent is a bulk write action.
    """

    return intent in _BULK_WRITE_INTENTS


def is_ai_write_intent(intent: AiIntentKind) -> bool:
    """Перевіряє, чи intent потребує підтвердження та запису в БД.
    Checks whether the intent requires confirmation and a DB write.
    """

    return intent in _WRITE_INTENTS


def is_ai_read_only_intent(intent: AiIntentKind) -> bool:
    """Перевіряє read-only навігаційні intent (зворотна сумісність).
    Checks read-only navigation intents for backward compatibility.
    """

    return intent in _NAVIGATION_INTENTS


def ensure_ai_intent_is_allowed(intent: AiIntentKind) -> None:
    """Забороняє небезпечні AI-intent, які не підтримуються ClearWork AI.
    Rejects unsafe AI intents that ClearWork AI must never execute.
    """

    if intent.value in _FORBIDDEN_WRITE_INTENTS:
        raise ValueError(f"Intent '{intent.value}' заборонений для AI.")

    if intent == AiIntentKind.UNKNOWN:
        raise ValueError("Намір команди не розпізнано.")
