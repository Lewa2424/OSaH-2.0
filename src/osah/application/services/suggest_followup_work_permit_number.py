from pathlib import Path
import re

from osah.application.services.load_work_permit_registry import load_work_permit_registry


def suggest_followup_work_permit_number(database_path: Path, source_permit_number: str) -> str:
    """Повертає вільний номер для нового наряду на основі поточного.
    Returns an available permit number for a new permit based on the current one.
    """

    existing_numbers = {
        record.permit_number.strip()
        for record in load_work_permit_registry(database_path)
        if record.permit_number.strip()
    }
    root_number, next_index = _split_followup_permit_number(source_permit_number)
    while True:
        candidate = f"{root_number}-R{next_index}"
        if candidate not in existing_numbers:
            return candidate
        next_index += 1


def _split_followup_permit_number(source_permit_number: str) -> tuple[str, int]:
    match = re.fullmatch(r"(?P<root>.+)-R(?P<index>\d+)", source_permit_number.strip())
    if match is None:
        return source_permit_number.strip(), 1
    return match.group("root"), int(match.group("index")) + 1
