import re

from osah.domain.entities.work_permit_participant_role import WorkPermitParticipantRole
from osah.domain.entities.work_permit_target_training_status import WorkPermitTargetTrainingStatus
from osah.domain.services.format_work_permit_participant_role_label import format_work_permit_participant_role_label
from osah.domain.services.format_work_permit_target_training_status_label import (
    format_work_permit_target_training_status_label,
)

_EMPLOYEE_FIELD_LABELS: dict[str, str] = {
    "full_name": "ПІБ",
    "department": "Підрозділ",
    "position": "Посада",
    "status": "Статус",
    "photo": "Фото",
}

_COMMON_FIELD_LABELS: dict[str, str] = {
    **_EMPLOYEE_FIELD_LABELS,
    "id": "Запис",
    "employee": "Табельний №",
    "type": "Тип інструктажу",
    "event_date": "Дата проведення",
    "next_control": "Наступний контроль",
    "conducted_by": "Проводив",
    "note": "Примітка",
    "ppe": "ЗІЗ",
    "required": "Обов'язковий",
    "issued": "Видано",
    "issue_date": "Дата видачі",
    "replacement": "Дата заміни",
    "quantity": "Кількість",
    "valid_from": "Дійсний з",
    "valid_until": "Дійсний до",
    "decision": "Рішення",
    "restriction": "Обмеження",
    "permit_number": "№ наряду",
    "work_kind": "Вид робіт",
    "starts_at": "Початок",
    "ends_at": "Завершення",
    "extended_at": "Продовжено",
    "extension_reason_text": "Підстава продовження",
    "participants": "Учасники",
    "target_training_status": "Цільовий інструктаж",
    "target_training_date": "Дата цільового інструктажу",
    "target_training_by": "Провів цільовий інструктаж",
    "target_training_note": "Примітка до цільового інструктажу",
    "closed_at": "Закрито",
    "canceled_at": "Скасовано",
    "closed_at_tail": "Час закриття",
}

_ALWAYS_HIDDEN_KEYS = frozenset(
    {
        "base_ends_at",
        "extension_count",
        "reissued_from_record_id",
        "reissued_to_record_id",
        "reissue_reason_text",
        "daily_check_count",
        "basis_text",
        "basis_note",
        "person_category",
        "requires_primary",
        "risk",
        "basis",
        "knowledge_result",
        "admission",
        "knowledge_note",
        "is_current",
        "archived_at",
        "archive_reason",
        "replaced_by_record_id",
        "source_module",
        "source_record_id",
        "source_key",
    }
)

_VALUE_LABELS: dict[str, dict[str, str]] = {
    "status": {
        "active": "активний",
        "archived": "архівний",
        "inactive": "неактивний",
        "dismissed": "звільнений",
    },
    "photo": {
        "set": "додано",
        "none": "відсутнє",
    },
    "required": {
        "1": "так",
        "0": "ні",
        "true": "так",
        "false": "ні",
    },
    "issued": {
        "1": "так",
        "0": "ні",
        "true": "так",
        "false": "ні",
    },
}

_KNOWN_MESSAGES: dict[str, str] = {
    "Status changed to archived via UI": "Статус змінено на «архівний» через інтерфейс.",
    "Archived employee reactivated from archive registry.": "Працівника повернено з архіву.",
}

_SECTION_PATTERN = re.compile(
    r"(?P<label>created|old|new|before|after|deleted|training|new_record)=?\((?P<body>.*?)\)(?:\s|$|;)",
    re.IGNORECASE,
)
_SECTION_TITLES: dict[str, str] = {
    "created": "Створено",
    "old": "Було",
    "new": "Стало",
    "before": "Стан до події",
    "after": "Стан після події",
    "deleted": "Видалено",
    "training": "Інструктаж",
    "new_record": "Новий наряд",
}

_USER_FACING_KEY_ORDER: tuple[str, ...] = (
    "permit_number",
    "work_kind",
    "starts_at",
    "ends_at",
    "participants",
    "target_training_status",
    "target_training_date",
    "target_training_by",
    "target_training_note",
    "extended_at",
    "extension_reason_text",
    "closed_at",
    "canceled_at",
    "full_name",
    "department",
    "position",
    "status",
    "photo",
    "employee",
    "id",
    "type",
    "event_date",
    "next_control",
    "conducted_by",
    "note",
    "ppe",
    "required",
    "issued",
    "issue_date",
    "replacement",
    "quantity",
    "valid_from",
    "valid_until",
    "decision",
    "restriction",
)


# ###### ФОРМАТ ОПИСУ AUDIT / FORMAT EMPLOYEE AUDIT DESCRIPTION ######
def format_employee_audit_description_text(description_text: str) -> str:
    """Перетворює технічний audit-опис на зрозумілий текст для картки працівника.
    Converts a technical audit description into readable text for the employee card.
    """

    normalized_description = description_text.strip()
    if not normalized_description:
        return "Опис події відсутній."

    if normalized_description in _KNOWN_MESSAGES:
        return _KNOWN_MESSAGES[normalized_description]

    sections, tail_pairs = _parse_description_sections(normalized_description)
    if sections or tail_pairs:
        return _format_parsed_description(sections, tail_pairs)

    if ";" in normalized_description and "=" in normalized_description:
        return _format_key_value_block(normalized_description)

    return normalized_description


# ###### КОРОТКИЙ ОПИС AUDIT / BUILD EMPLOYEE AUDIT SUMMARY ######
def build_employee_audit_summary_text(description_text: str) -> str:
    """Повертає короткий опис для колонки таблиці історії.
    Returns a short description for the employee history table column.
    """

    formatted_text = format_employee_audit_description_text(description_text)
    for line in formatted_text.splitlines():
        normalized_line = line.strip()
        if not normalized_line or normalized_line.endswith(":"):
            continue
        if len(normalized_line) <= 120:
            return normalized_line
        return f"{normalized_line[:117]}..."
    return "—"


def _parse_description_sections(description_text: str) -> tuple[dict[str, list[tuple[str, str]]], list[tuple[str, str]]]:
    sections: dict[str, list[tuple[str, str]]] = {}
    consumed_spans: list[tuple[int, int]] = []
    for match in _SECTION_PATTERN.finditer(description_text):
        section_label = match.group("label").lower()
        section_body = match.group("body").strip()
        if section_body:
            sections[section_label] = _parse_key_value_pairs(section_body)
        consumed_spans.append(match.span())

    tail_text = description_text
    for start, end in reversed(consumed_spans):
        tail_text = tail_text[:start] + tail_text[end:]
    tail_pairs = _parse_key_value_pairs(tail_text.strip().strip(";"))
    return sections, tail_pairs


def _format_parsed_description(
    sections: dict[str, list[tuple[str, str]]],
    tail_pairs: list[tuple[str, str]],
) -> str:
    blocks: list[str] = []

    left_section = sections.get("old") or sections.get("before")
    right_section = sections.get("new") or sections.get("after")
    if left_section is not None and right_section is not None:
        diff_text = _format_section_diff(left_section, right_section)
        if diff_text:
            blocks.append(f"Зміни:\n{diff_text}")

    handled_labels = {"old", "new", "before", "after"}
    for section_label, section_pairs in sections.items():
        if section_label in handled_labels and left_section is not None and right_section is not None:
            continue
        section_title = _SECTION_TITLES.get(section_label, section_label)
        section_text = _format_compact_snapshot(section_pairs)
        if section_text:
            blocks.append(f"{section_title}:\n{section_text}")

    if tail_pairs:
        tail_text = _format_compact_snapshot(tail_pairs)
        if tail_text:
            blocks.append(tail_text)

    return "\n\n".join(blocks) if blocks else "Опис події відсутній."


def _format_section_diff(
    left_pairs: list[tuple[str, str]],
    right_pairs: list[tuple[str, str]],
) -> str:
    left_map = dict(left_pairs)
    right_map = dict(right_pairs)
    all_keys = set(left_map) | set(right_map)
    lines: list[str] = []

    for key in _ordered_keys(all_keys):
        if not _should_show_field(key, left_map.get(key, ""), right_map.get(key, ""), left_map | right_map):
            continue
        old_value = _format_field_value(key, left_map.get(key, ""))
        new_value = _format_field_value(key, right_map.get(key, ""))
        if old_value == new_value:
            continue
        label = _COMMON_FIELD_LABELS.get(key, key.replace("_", " "))
        if key == "participants":
            lines.append(f"• {label}:")
            lines.append(_format_participants_diff(left_map.get(key, ""), right_map.get(key, "")))
            continue
        lines.append(f"• {label}: {old_value} → {new_value}")

    return "\n".join(line for line in lines if line)


def _format_compact_snapshot(pairs: list[tuple[str, str]]) -> str:
    pair_map = dict(pairs)
    visible_pairs = [
        (key, value)
        for key, value in pairs
        if _should_show_field(key, value, value, pair_map)
    ]
    return _format_key_value_block_from_pairs(visible_pairs)


def _format_key_value_block(raw_text: str) -> str:
    pairs = _parse_key_value_pairs(raw_text)
    if not pairs:
        return raw_text
    return _format_compact_snapshot(pairs)


def _format_key_value_block_from_pairs(pairs: list[tuple[str, str]]) -> str:
    if not pairs:
        return ""

    lines: list[str] = []
    for key, value in _ordered_pairs(pairs):
        label = _COMMON_FIELD_LABELS.get(key, key.replace("_", " "))
        if key == "participants":
            participant_lines = _format_participants_lines(value)
            if not participant_lines:
                continue
            lines.append(f"• {label}:")
            lines.extend(participant_lines)
            continue

        display_value = _format_field_value(key, value)
        if display_value and display_value != "—":
            lines.append(f"• {label}: {display_value}")
    return "\n".join(lines)


def _parse_key_value_pairs(raw_text: str) -> list[tuple[str, str]]:
    pairs: list[tuple[str, str]] = []
    for token in raw_text.split(";"):
        normalized_token = token.strip()
        if not normalized_token or "=" not in normalized_token:
            continue
        key, value = normalized_token.split("=", 1)
        pairs.append((key.strip(), value.strip()))
    return pairs


def _should_show_field(
    key: str,
    left_value: str,
    right_value: str,
    pair_map: dict[str, str],
) -> bool:
    if key in _ALWAYS_HIDDEN_KEYS:
        return False

    normalized_value = (right_value or left_value).strip()
    if key == "extended_at" or key == "extension_reason_text":
        return pair_map.get("extension_count", "0") not in {"", "0"}

    if key in {"target_training_date", "target_training_by", "target_training_note"}:
        status = pair_map.get("target_training_status", "").casefold()
        return status not in {"", "legacy_not_tracked", "not_done"} and bool(normalized_value)

    if key == "target_training_status":
        return normalized_value.casefold() not in {"", "legacy_not_tracked"}

    if key == "closed_at" or key == "canceled_at":
        return bool(normalized_value)

    if not normalized_value or normalized_value in {"0", "-", "—"}:
        return False

    return True


def _format_field_value(key: str, value: str) -> str:
    normalized_value = value.strip()
    if not normalized_value:
        return "—"

    if key == "participants":
        participant_lines = _format_participants_lines(normalized_value)
        return "\n".join(participant_lines) if participant_lines else "—"

    if key == "target_training_status":
        return _format_target_training_status_value(normalized_value)

    mapped_value = _VALUE_LABELS.get(key, {}).get(normalized_value.casefold())
    if mapped_value is not None:
        return mapped_value
    return normalized_value


def _format_target_training_status_value(raw_status: str) -> str:
    try:
        target_training_status = WorkPermitTargetTrainingStatus(raw_status)
    except ValueError:
        return raw_status
    return format_work_permit_target_training_status_label(target_training_status)


def _format_participants_lines(raw_participants: str) -> list[str]:
    lines: list[str] = []
    for token in raw_participants.split(","):
        normalized_token = token.strip()
        if not normalized_token or ":" not in normalized_token:
            continue
        personnel_number, participant_role = normalized_token.split(":", 1)
        role_label = _format_participant_role_label(participant_role.strip())
        lines.append(f"  - №{personnel_number.strip()} — {role_label}")
    return lines


def _format_participants_diff(old_participants: str, new_participants: str) -> str:
    old_lines = _format_participants_lines(old_participants)
    new_lines = _format_participants_lines(new_participants)
    if old_lines == new_lines:
        return ""
    old_text = "\n".join(old_lines) if old_lines else "  - —"
    new_text = "\n".join(new_lines) if new_lines else "  - —"
    return f"  Було:\n{old_text}\n  Стало:\n{new_text}"


def _format_participant_role_label(raw_role: str) -> str:
    try:
        participant_role = WorkPermitParticipantRole(raw_role)
    except ValueError:
        return raw_role
    return format_work_permit_participant_role_label(participant_role)


def _ordered_keys(keys: set[str]) -> list[str]:
    ordered = [key for key in _USER_FACING_KEY_ORDER if key in keys]
    remaining = sorted(key for key in keys if key not in _USER_FACING_KEY_ORDER)
    return ordered + remaining


def _ordered_pairs(pairs: list[tuple[str, str]]) -> list[tuple[str, str]]:
    pair_map = dict(pairs)
    return [(key, pair_map[key]) for key in _ordered_keys(set(pair_map))]
