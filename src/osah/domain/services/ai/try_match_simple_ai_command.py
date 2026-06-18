import re

from osah.domain.entities.ai_command_draft import AiCommandDraft
from osah.domain.entities.ai_intent_kind import AiIntentKind
from osah.domain.services.ai.detect_ai_command_track import extract_ppe_token_from_command
from osah.domain.services.ai.matches_missing_ppe_list_query import matches_missing_ppe_list_query


_PERSONNEL_NUMBER_PATTERN = re.compile(r"(?:таб(?:ельний)?\.?\s*№?\s*|№\s*)(\d{1,6})", re.IGNORECASE)
_PPE_ITEM_PATTERN = re.compile(
    r"(?:"
    r"каск(?:а|у|и|ов)?|касок|"
    r"черевик(?:и|ів|и|ов)?|"
    r"рукавиц(?:і|ь|и|ей|ь)?|"
    r"ботинк(?:и|и|ов)?|ботинок|"
    r"перчатк(?:и|и|ов)?|перчаток|"
    r"роб(?:а|у|и)?"
    r")",
    re.IGNORECASE,
)
_NAV_VERB = (
    r"покажи|показати|показать|"
    r"відкрий|відкрити|"
    r"открой|открыть|откройте|"
    r"выведи|вывести|виведи|"
    r"open"
)
_PPE_SECTION = r"зіз|зиз|зі[зс]|сиз|ppe"
_TRAINING_SECTION = r"інструктаж(?:и|і|ів|ами)?|инструктаж(?:и|и|ов|ами)?|trainings?"
_EMPLOYEE_SECTION = r"працівник|сотрудник|employees?"
_EMPLOYEE_NAV_TAIL_BLOCK = r"проблемн|інструктаж|инструктаж|критич|просроч|простроч|не\s+закрыт|не\s+закрит|звільнен|уволен|стропаль|без\s+посад|без\s+должност|активн"

_SIMPLE_RULES: tuple[tuple[re.Pattern[str], AiIntentKind, dict[str, str | None]], ...] = (
    (re.compile(rf"^\s*(?:{_NAV_VERB})\s+просроч", re.IGNORECASE), AiIntentKind.SHOW_OVERDUE, {}),
    (re.compile(rf"^\s*(?:{_NAV_VERB}).{{0,40}}простроч", re.IGNORECASE), AiIntentKind.SHOW_OVERDUE, {}),
    (re.compile(r"^\s*просроч", re.IGNORECASE), AiIntentKind.SHOW_OVERDUE, {}),
    (re.compile(r"^\s*простроч", re.IGNORECASE), AiIntentKind.SHOW_OVERDUE, {}),
    (re.compile(rf"^\s*(?:{_NAV_VERB})\s+(?:головн|дашборд|dashboard)", re.IGNORECASE), AiIntentKind.NAVIGATE_SECTION, {"section_key": "dashboard"}),
    (re.compile(rf"^\s*(?:{_NAV_VERB})\s+(?:раздел|розділ)\s+(?:{_PPE_SECTION})", re.IGNORECASE), AiIntentKind.NAVIGATE_SECTION, {"section_key": "ppe"}),
    (re.compile(rf"^\s*(?:{_NAV_VERB})\s+(?:раздел|розділ)\s+(?:{_TRAINING_SECTION})", re.IGNORECASE), AiIntentKind.NAVIGATE_SECTION, {"section_key": "trainings"}),
    (re.compile(rf"^\s*(?:{_NAV_VERB})\s+(?:{_PPE_SECTION})", re.IGNORECASE), AiIntentKind.NAVIGATE_SECTION, {"section_key": "ppe"}),
    (re.compile(rf"^\s*(?:{_NAV_VERB})\s+(?:{_TRAINING_SECTION})", re.IGNORECASE), AiIntentKind.NAVIGATE_SECTION, {"section_key": "trainings"}),
    (re.compile(rf"^\s*(?:{_NAV_VERB})\s+(?:мед(?:ицин|осмотр|огляд)?|medical)", re.IGNORECASE), AiIntentKind.NAVIGATE_SECTION, {"section_key": "medical"}),
    (re.compile(r"^\s*(?:покажи|показати).{0,30}(?:наряд|наряди).{0,20}(?:сьогодні|сегодня)", re.IGNORECASE), AiIntentKind.QUERY_WORK_PERMIT_LIST, {"module_key": "today"}),
    (re.compile(r"^\s*(?:покажи|показати).{0,30}(?:наряд|наряди).{0,20}завтра", re.IGNORECASE), AiIntentKind.QUERY_WORK_PERMIT_LIST, {"module_key": "tomorrow"}),
    (re.compile(r"^\s*(?:покажи|показати).{0,30}(?:активн).{0,20}(?:наряд|наряди)", re.IGNORECASE), AiIntentKind.QUERY_WORK_PERMIT_LIST, {"module_key": "open"}),
    (re.compile(r"^\s*(?:список).{0,20}(?:наряд|наряди)", re.IGNORECASE), AiIntentKind.QUERY_WORK_PERMIT_LIST, {"module_key": "open"}),
    (re.compile(rf"^\s*(?:{_NAV_VERB})\s+(?:наряд|наряди|work[_\s-]?permits?)", re.IGNORECASE), AiIntentKind.NAVIGATE_SECTION, {"section_key": "work_permits"}),
    (re.compile(r"^\s*(?:покажи|показати).{0,30}(?:звільнен|уволен).{0,30}(?:працівник|работник|сотрудник)", re.IGNORECASE), AiIntentKind.QUERY_EMPLOYEES_FILTER, {"filter_key": "terminated"}),
    (re.compile(r"^\s*(?:покажи|показати).{0,30}стропаль", re.IGNORECASE), AiIntentKind.QUERY_EMPLOYEES_FILTER, {"filter_key": "slinger"}),
    (re.compile(r"^\s*(?:покажи|показати).{0,40}(?:працівник|работник|сотрудник).{0,20}(?:без\s+посад|без\s+должност)", re.IGNORECASE), AiIntentKind.QUERY_EMPLOYEES_FILTER, {"filter_key": "without_position"}),
    (re.compile(r"^\s*(?:покажи|показати).{0,30}(?:активн).{0,20}(?:працівник|работник|сотрудник)", re.IGNORECASE), AiIntentKind.QUERY_EMPLOYEES_FILTER, {"filter_key": "active"}),
    (
        re.compile(
            rf"^\s*(?:{_NAV_VERB})\s+(?:{_EMPLOYEE_SECTION}).{{0,80}}(?:{_EMPLOYEE_NAV_TAIL_BLOCK})",
            re.IGNORECASE,
        ),
        AiIntentKind.QUERY_MODULE_STATUS,
        {"module_key": "trainings", "filter_key": "warning"},
    ),
    (
        re.compile(
            rf"^\s*(?:{_NAV_VERB})\s+(?:{_EMPLOYEE_SECTION})(?!.{{0,80}}(?:{_EMPLOYEE_NAV_TAIL_BLOCK}))",
            re.IGNORECASE,
        ),
        AiIntentKind.NAVIGATE_SECTION,
        {"section_key": "employees"},
    ),
    (re.compile(rf"^\s*(?:{_NAV_VERB})\s+(?:port[\s-]?r|порт[\s-]?р|оцінк(?:у|и)\s+ризик)", re.IGNORECASE), AiIntentKind.NAVIGATE_SECTION, {"section_key": "port_r"}),
    (re.compile(r"^\s*(?:що|что)\s+(?:закрити|закрыть).{0,30}(?:сьогодні|сегодня)", re.IGNORECASE), AiIntentKind.QUERY_DAILY_FOCUS, {}),
    (re.compile(r"^\s*(?:покажи|показати).{0,40}(?:закрити|закрыть).{0,30}(?:сьогодні|сегодня)", re.IGNORECASE), AiIntentKind.QUERY_DAILY_FOCUS, {}),
    (re.compile(r"^\s*(?:дай|покажи|показати).{0,25}(?:зведен|сводк|картин|стан\s+систем)", re.IGNORECASE), AiIntentKind.QUERY_DAILY_FOCUS, {}),
    (re.compile(r"^\s*(?:що|что).{0,20}(?:на\s+)?(?:повестк|повістк|порядок\s+дня|agenda)", re.IGNORECASE), AiIntentKind.QUERY_DAILY_FOCUS, {}),
    (re.compile(r"^\s*(?:що|что).{0,20}(?:важлив|важн|пріоритет|почати|делать\s+первым)", re.IGNORECASE), AiIntentKind.QUERY_DAILY_FOCUS, {}),
    (re.compile(r"^\s*(?:які|какие|якие).{0,30}(?:проблемн|критичн).{0,30}(?:розділ|раздел)", re.IGNORECASE), AiIntentKind.QUERY_SECTION_PROBLEMS, {}),
    (re.compile(r"^\s*(?:проблемн|критичн).{0,30}(?:розділ|раздел)", re.IGNORECASE), AiIntentKind.QUERY_SECTION_PROBLEMS, {}),
    (re.compile(r"^\s*(?:покажи|скільки|сколько).{0,35}(?:критичн|проблем|незакрит|просроч|простроч)", re.IGNORECASE), AiIntentKind.QUERY_OVERDUE_SUMMARY, {}),
    (re.compile(r"^\s*(?:збери|сформуй|собери|підготуй|подготовь).{0,30}(?:звіт|отчёт|отчет)", re.IGNORECASE), AiIntentKind.GENERATE_REPORT_TEXT, {}),
    (re.compile(r"^\s*(?:що|что)\s+(?:потрібно|нужно|не\s+вистачає|не\s+хватает)\s+для\s+(.+)$", re.IGNORECASE), AiIntentKind.QUERY_EMPLOYEE_READINESS, {"employee_query": "__capture__"}),
    (re.compile(r"^\s*(?:готовий|готов)\s+(.+?)\s+до\s+роб", re.IGNORECASE), AiIntentKind.QUERY_EMPLOYEE_READINESS, {"employee_query": "__capture__"}),
    (re.compile(r"^\s*(?:покажи|найди|виведи|показати|знайди).{0,40}(?:працівник|работник|сотрудник).{0,40}(?:статус|со\s+статусом).{0,20}(?:увага|внимание|warning)", re.IGNORECASE), AiIntentKind.QUERY_EMPLOYEES_FILTER, {"filter_key": "warning"}),
    (re.compile(r"^\s*(?:покажи|найди|виведи|показати|знайди).{0,40}(?:працівник|работник|сотрудник).{0,40}(?:статус|со\s+статусом).{0,20}(?:критич|critical)", re.IGNORECASE), AiIntentKind.QUERY_EMPLOYEES_FILTER, {"filter_key": "critical"}),
    (re.compile(r"^\s*(?:покажи|найди|виведи|показати|знайди).{0,40}(?:працівник|работник|сотрудник).{0,40}(?:статус|со\s+статусом).{0,20}(?:обмежен|ограничен|restricted)", re.IGNORECASE), AiIntentKind.QUERY_EMPLOYEES_FILTER, {"filter_key": "restricted"}),
    (re.compile(r"^\s*(?:готовність|готовность).{0,40}(?:учасник|участник).{0,20}(?:наряд|№)\s*(\d+)", re.IGNORECASE), AiIntentKind.QUERY_WORK_PERMIT_READINESS, {"permit_number": "__capture__"}),
    (re.compile(r"^\s*(?:хто\s+не\s+готов|готовий).{0,40}(?:наряд|№)\s*(\d+)", re.IGNORECASE), AiIntentKind.QUERY_WORK_PERMIT_READINESS, {"permit_number": "__capture__"}),
    (re.compile(r"^\s*(?:покажи|показати).{0,35}(?:пробел|прогалин|незаповнен).{0,30}(?:port[\s-]?r|порт[\s-]?р|паспорт)", re.IGNORECASE), AiIntentKind.QUERY_PORT_R_GAPS, {}),
    (re.compile(r"^\s*(?:незаповнен|не\s+заповнен).{0,30}(?:паспорт|port[\s-]?r)", re.IGNORECASE), AiIntentKind.QUERY_PORT_R_GAPS, {}),
    (re.compile(r"^\s*(?:покажи|найди|виведи|показати|знайди).{0,40}(?:працівник|работник|сотрудник).{0,40}(?:без\s+участк|без\s+дільниц|без\s+підрозділ)", re.IGNORECASE), AiIntentKind.QUERY_EMPLOYEES_FILTER, {"filter_key": "without_department"}),
    (re.compile(r"^\s*(?:покажи|показати|дай).{0,30}(?:загальн|стан\s+систем|контроль\s+на|задач)", re.IGNORECASE), AiIntentKind.QUERY_DAILY_FOCUS, {}),
    (re.compile(r"^\s*з\s+чого\s+почати", re.IGNORECASE), AiIntentKind.QUERY_DAILY_FOCUS, {}),
    (re.compile(r"^\s*(?:покажи|показати).{0,25}(?:пріоритет)", re.IGNORECASE), AiIntentKind.QUERY_DAILY_FOCUS, {}),
    (re.compile(r"^\s*(?:покажи|показати).{0,35}(?:жовт|жёлт|желт).{0,20}(?:статус)", re.IGNORECASE), AiIntentKind.QUERY_OVERDUE_SUMMARY, {}),
    (re.compile(r"^\s*(?:покажи|показати).{0,25}(?:всі\s+)?проблем", re.IGNORECASE), AiIntentKind.QUERY_OVERDUE_SUMMARY, {}),
    (re.compile(r"^\s*у\s+кого\s+простроч", re.IGNORECASE), AiIntentKind.QUERY_OVERDUE_SUMMARY, {}),
    (re.compile(r"^\s*(?:чому|почему).{0,30}(?:статус|червон|жовт)", re.IGNORECASE), AiIntentKind.EXPLAIN_HELP, {"explain_topic": "status"}),
    (re.compile(r"^\s*(?:що|что)\s+таке.{0,40}(?:наряд|інструктаж|port)", re.IGNORECASE), AiIntentKind.EXPLAIN_HELP, {"explain_topic": "domain"}),
    (re.compile(r"^\s*(?:як\s+працює|как\s+работает)", re.IGNORECASE), AiIntentKind.EXPLAIN_HELP, {"explain_topic": "domain"}),
    (re.compile(r"^\s*(?:що\s+означає|что\s+означает).{0,20}поле", re.IGNORECASE), AiIntentKind.EXPLAIN_HELP, {"explain_topic": "ui"}),
    (re.compile(r"^\s*(?:додай|добавь).{0,60}(?:до\s+)?(?:наряд|наряду).{0,15}№?\s*(\d+)", re.IGNORECASE), AiIntentKind.ADD_WORK_PERMIT_PARTICIPANT, {"permit_number": "__capture__"}),
    (re.compile(r"^\s*(?:прибери|убери).{0,60}(?:з|из).{0,15}(?:наряд|наряду).{0,15}№?\s*(\d+)", re.IGNORECASE), AiIntentKind.REMOVE_WORK_PERMIT_PARTICIPANT, {"permit_number": "__capture__"}),
    (re.compile(r"^\s*(?:заміни|замени).{0,30}(?:каск|ботинк|черевик|перчат|рукавиц)", re.IGNORECASE), AiIntentKind.UPDATE_PPE_RECORD, {}),
    (re.compile(r"^\s*(?:онови|обнови).{0,30}(?:повторн|інструктаж|инструктаж)", re.IGNORECASE), AiIntentKind.UPDATE_TRAINING_RECORD, {}),
    (re.compile(r"^\s*(?:продовж|продли).{0,30}(?:медогляд|медосмотр)", re.IGNORECASE), AiIntentKind.UPDATE_MEDICAL_RECORD, {}),
    (re.compile(r"^\s*(?:постав|поставь).{0,30}звільн", re.IGNORECASE), AiIntentKind.UPDATE_EMPLOYEE_FIELDS, {}),
    (re.compile(r"^\s*(?:зміни|измени|переведи).{0,30}(?:дільниц|участок|підрозділ)", re.IGNORECASE), AiIntentKind.UPDATE_EMPLOYEE_FIELDS, {}),
)
def try_match_simple_ai_command(command_text: str) -> AiCommandDraft | None:
    """Розпізнає прості однозначні команди без LLM.
    Matches simple unambiguous commands without LLM.
    """

    normalized_command = command_text.strip()
    if not normalized_command:
        return None

    personnel_match = _PERSONNEL_NUMBER_PATTERN.search(normalized_command)
    if personnel_match is not None and re.search(r"(?:картк|карточ|card)", normalized_command, re.IGNORECASE):
        return AiCommandDraft(
            intent=AiIntentKind.OPEN_EMPLOYEE_CARD,
            raw_command=normalized_command,
            source="rule_router",
            personnel_number=personnel_match.group(1).zfill(4),
            needs_confirmation=False,
        )

    if matches_missing_ppe_list_query(normalized_command):
        ppe_token = extract_ppe_token_from_command(normalized_command)
        return AiCommandDraft(
            intent=AiIntentKind.QUERY_MISSING_PPE,
            raw_command=normalized_command,
            source="rule_router",
            ppe_item_query=ppe_token or "каска",
            needs_confirmation=False,
        )

    for pattern, intent, extras in _SIMPLE_RULES:
        match = pattern.search(normalized_command)
        if match is None:
            continue
        draft_kwargs: dict[str, object] = {
            "intent": intent,
            "raw_command": normalized_command,
            "source": "rule_router",
            "needs_confirmation": False,
        }
        for key, value in extras.items():
            if value == "__capture__" and match.lastindex:
                captured = match.group(1).strip()
                captured = captured.rstrip("?!").strip()
                draft_kwargs[key] = captured
            elif value == "__ppe__":
                item_match = _PPE_ITEM_PATTERN.search(normalized_command)
                draft_kwargs["ppe_item_query"] = item_match.group(0) if item_match else "каска"
            elif value is not None:
                draft_kwargs[key] = value
        return AiCommandDraft(**draft_kwargs)

    return None
