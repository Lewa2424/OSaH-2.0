import re

from osah.domain.entities.ai_command_draft import AiCommandDraft
from osah.domain.entities.ai_command_track import AiCommandTrack
from osah.domain.entities.ai_intent_kind import AiIntentKind
from osah.domain.services.ai.ensure_ai_intent_is_allowed import (
    is_ai_bulk_intent,
    is_ai_navigation_intent,
    is_ai_write_intent,
)
from osah.domain.services.ai.extract_employee_query_from_command import (
    extract_employee_query_from_command,
    extract_personnel_number_from_command,
)
from osah.domain.services.ai.matches_employee_problems_query import matches_employee_problems_query
from osah.domain.services.ai.matches_module_status_list_query import matches_module_status_list_query
from osah.domain.services.ai.ai_relative_date_markers import mentions_current_date

_WRITE_VERB_PATTERN = re.compile(
    r"\b(?:"
    r"занеси|занести|видай|выдай|выдать|впиши|забей|оформи|"
    r"продли|продлить|продовж|подовж|"
    r"додай|добавь|добав|проведи|постав|поставь|"
    r"онови|обнови|зміни|измени|створи|создай"
    r")\b",
    re.IGNORECASE,
)
_QUERY_LEAD_PATTERN = re.compile(
    r"(?:^|\s)(?:"
    r"кому|у кого|хто|скільки|сколько|які|какие|"
    r"що потрібно|что нужно|что потрібно|покажи список|"
    r"де є|где есть|які зараз|какие сейчас"
    r")\b",
    re.IGNORECASE,
)
_SECTION_PROBLEMS_PATTERN = re.compile(
    r"(?:"
    r"проблемн|критичн|червон|жовт|"
    r"проблемные|критические|проблемні"
    r").{0,30}(?:"
    r"розділ|раздел|модул|напрям|секці"
    r")|"
    r"(?:"
    r"які|какие|якие"
    r").{0,20}(?:"
    r"розділ|раздел"
    r").{0,20}(?:"
    r"проблемн|критичн|червон"
    r")",
    re.IGNORECASE,
)
_PPE_TOKEN_PATTERN = re.compile(
    r"\b(?:"
    r"каск\w*|касок|"
    r"черевик\w*|черевиков|"
    r"ботинк\w*|ботинок|"
    r"рукавиц\w*|рукавиць|"
    r"перчат\w*|перчаток|"
    r"жилет\w*|жилетов|"
    r"комбінезон\w*|комбинезонов|"
    r"каску|каски|"
    r"взутт\w*|обув\w*|"
    r"спецодяг\w*"
    r")\b",
    re.IGNORECASE,
)
_TRAINING_TOKEN_PATTERN = re.compile(r"\b(?:інструктаж\w*|инструктаж\w*)\b", re.IGNORECASE)
_MEDICAL_TOKEN_PATTERN = re.compile(r"\b(?:мед(?:огляд|осмотр)?\w*)\b", re.IGNORECASE)
from osah.domain.services.ai.ai_relative_date_markers import mentions_current_date


def matches_section_problems_query(raw_command: str) -> bool:
    """Перевіряє запит про проблемні розділи.
    Checks whether the phrase asks for problematic sections.
    """

    text = raw_command.strip()
    if matches_employee_problems_query(text):
        return False
    if re.search(r"проблем", text, re.IGNORECASE) and extract_employee_query_from_command(text):
        return False
    return bool(_SECTION_PROBLEMS_PATTERN.search(text))


def detect_ai_command_track(draft: AiCommandDraft) -> AiCommandTrack | None:
    """Визначає головний рельс READ/WRITE/NAV для чернетки.
    Detects the top-level READ/WRITE/NAV track for a draft.
    """

    if is_ai_navigation_intent(draft.intent):
        return AiCommandTrack.NAV
    if is_ai_write_intent(draft.intent) or is_ai_bulk_intent(draft.intent):
        return AiCommandTrack.WRITE

    raw_command = draft.raw_command.strip()
    if not raw_command:
        return None

    if matches_section_problems_query(raw_command):
        return AiCommandTrack.READ
    if matches_module_status_list_query(raw_command):
        return AiCommandTrack.READ

    has_write_verb = bool(_WRITE_VERB_PATTERN.search(raw_command))
    has_query_lead = bool(_QUERY_LEAD_PATTERN.search(raw_command))
    has_personal_target = _has_personal_target(draft, raw_command)

    if has_write_verb and has_personal_target and not _is_list_query(raw_command):
        return AiCommandTrack.WRITE
    if has_query_lead or (has_write_verb and not has_personal_target):
        return AiCommandTrack.READ
    if draft.intent in {
        AiIntentKind.QUERY_MISSING_PPE,
        AiIntentKind.QUERY_DAILY_FOCUS,
        AiIntentKind.QUERY_EMPLOYEE_READINESS,
        AiIntentKind.QUERY_OVERDUE_SUMMARY,
        AiIntentKind.QUERY_SECTION_PROBLEMS,
        AiIntentKind.QUERY_MODULE_STATUS,
        AiIntentKind.EXPLAIN_HELP,
        AiIntentKind.GENERATE_REPORT_TEXT,
    }:
        return AiCommandTrack.READ
    return None


def extract_ppe_token_from_command(raw_command: str) -> str | None:
    """Витягує фрагмент предмета ЗІЗ з тексту команди.
    Extracts a PPE item token from the command text.
    """

    match = _PPE_TOKEN_PATTERN.search(raw_command)
    if match is None:
        return None
    return match.group(0).strip()


def infer_write_module_key(raw_command: str, draft: AiCommandDraft) -> str | None:
    """Визначає модуль для write-команди за текстом.
    Infers the target module key for a write command.
    """

    lowered = raw_command.lower()
    if draft.ppe_item_query or _PPE_TOKEN_PATTERN.search(raw_command) or any(
        token in lowered for token in ("зіз", "сиз", "ppe", "спецодяг")
    ):
        return "ppe"
    if draft.training_type or _TRAINING_TOKEN_PATTERN.search(raw_command):
        return "trainings"
    if draft.medical_decision or _MEDICAL_TOKEN_PATTERN.search(raw_command):
        return "medical"
    if any(token in lowered for token in ("посад", "дільниц", "участок", "підрозділ", "звільн")):
        return "employees"
    if any(token in lowered for token in ("наряд", "учасник", "бригад")):
        return "work_permits"
    return None


def has_today_date_marker(raw_command: str) -> bool:
    """Перевіряє, чи в команді є маркер сьогоднішньої дати.
    Checks whether the command mentions today's date.
    """

    return mentions_current_date(raw_command)


def _has_personal_target(draft: AiCommandDraft, raw_command: str) -> bool:
    if draft.personnel_number or draft.employee_query:
        return True
    if extract_personnel_number_from_command(raw_command):
        return True
    return extract_employee_query_from_command(raw_command) is not None


def _is_list_query(raw_command: str) -> bool:
    return bool(
        re.search(
            r"(?:^|\s)(?:кому|у кого|хто)\b",
            raw_command,
            re.IGNORECASE,
        )
    )
