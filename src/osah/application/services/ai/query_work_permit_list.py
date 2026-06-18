from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path

from osah.application.services.load_work_permit_registry import load_work_permit_registry
from osah.domain.entities.work_permit_status import WorkPermitStatus
from osah.domain.services.parse_service_datetime_text import parse_service_datetime_text


@dataclass(slots=True, frozen=True)
class WorkPermitListRow:
    """Короткий рядок наряду для AI-відповіді.
    Compact work permit row for AI answers.
    """

    permit_number: str
    work_kind: str
    starts_at: str
    ends_at: str
    status: WorkPermitStatus


def query_work_permit_list(database_path: Path, filter_key: str | None = None) -> tuple[WorkPermitListRow, ...]:
    """Повертає список нарядів за фільтром.
    Returns work permits matching the filter key.
    """

    normalized = (filter_key or "open").strip().lower()
    today = date.today()
    tomorrow = today + timedelta(days=1)
    rows: list[WorkPermitListRow] = []

    for record in load_work_permit_registry(database_path):
        if normalized in {"open", "відкрит", "открыт", "active", "активн"}:
            if record.status not in {WorkPermitStatus.ACTIVE, WorkPermitStatus.WARNING}:
                continue
        elif normalized in {"today", "сьогодні", "сегодня"}:
            if not _matches_day(record.starts_at, today):
                continue
        elif normalized in {"tomorrow", "завтра"}:
            if not _matches_day(record.starts_at, tomorrow):
                continue
        else:
            if record.status in {WorkPermitStatus.CLOSED, WorkPermitStatus.CANCELED, WorkPermitStatus.REISSUED}:
                continue
        rows.append(
            WorkPermitListRow(
                permit_number=record.permit_number,
                work_kind=record.work_kind,
                starts_at=record.starts_at,
                ends_at=record.ends_at,
                status=record.status,
            )
        )

    return tuple(rows)


def _matches_day(starts_at_text: str, target_day: date) -> bool:
    try:
        parsed = parse_service_datetime_text(starts_at_text)
    except ValueError:
        return False
    return parsed.date() == target_day
