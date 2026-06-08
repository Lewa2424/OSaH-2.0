from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from osah.application.services.load_port_calibration_for_passport import load_port_calibration_for_passport
from osah.application.services.load_port_site_passport_for_edit import load_port_site_passport_for_edit
from osah.application.services.load_port_site_risks_for_passport import load_port_site_risks_for_passport
from osah.application.services.security.ensure_write_access import ensure_write_access
from osah.domain.entities.access_role import AccessRole
from osah.domain.entities.port_shift_zone import PortShiftZone
from osah.domain.services.build_port_shift_briefing import build_port_shift_briefing
from osah.infrastructure.database.commands.insert_audit_log import insert_audit_log
from osah.infrastructure.database.create_database_connection import create_database_connection
from osah.infrastructure.database.queries.list_port_shift_checklists import list_port_shift_checklists
from osah.infrastructure.database.queries.load_port_shift_checklist_detail import (
    load_port_shift_checklist_detail,
)
from osah.infrastructure.database.queries.select_port_site_passport_row_by_id import (
    select_port_site_passport_row_by_id,
)
from osah.infrastructure.docx.render_port_shift_briefing_docx import render_port_shift_briefing_docx
from osah.infrastructure.paths.build_port_r_exports_directory import build_port_r_exports_directory


_INVALID_FILENAME_CHARS: str = '<>:"/\\|?*'


@dataclass(slots=True)
class PortShiftBriefingExportResult:
    """Результат експорту оперативного листа зміни ПОРТ-Р.
    Result of a PORT-R shift briefing export.
    """

    file_path: Path
    key_risks_count: int


# ###### ЕКСПОРТ ОПЕРАТИВНОГО ЛИСТА ЗМІНИ ПОРТ-Р / EXPORT PORT-R SHIFT BRIEFING ######
def export_port_shift_briefing_to_docx(
    database_path: Path,
    project_root: Path,
    passport_id: int,
    *,
    actor_name: str,
    access_role: AccessRole,
    checklist_id: int | None = None,
) -> PortShiftBriefingExportResult:
    """Формує .docx оперативного листа зміни для паспорта і повертає шлях разом із підсумками.
    Builds the shift briefing .docx for the passport and returns the path with summary counts.
    """

    ensure_write_access(access_role, "export_port_shift_briefing_to_docx")

    connection = create_database_connection(database_path)
    try:
        passport_row = select_port_site_passport_row_by_id(connection, passport_id)
    finally:
        connection.close()

    passport_input = load_port_site_passport_for_edit(database_path, passport_id)
    risks = load_port_site_risks_for_passport(database_path, passport_id)
    calibration = load_port_calibration_for_passport(database_path, passport_id)

    record_detail = None
    last_r_dyn: float | None = None
    last_zone: PortShiftZone | None = None
    connection = create_database_connection(database_path)
    try:
        if checklist_id is not None:
            record_detail = load_port_shift_checklist_detail(connection, checklist_id)
        if record_detail is None:
            checklists = list_port_shift_checklists(connection, passport_id=passport_id)
            if checklists:
                latest = checklists[0]
                last_r_dyn = latest.r_dyn
                last_zone = latest.zone
    finally:
        connection.close()

    briefing = build_port_shift_briefing(
        passport_row,
        passport_input,
        risks,
        calibration=calibration,
        last_r_dyn=last_r_dyn,
        last_zone=last_zone,
        record_detail=record_detail,
    )

    exports_directory = build_port_r_exports_directory(project_root)
    file_name = _build_file_name(passport_row.passport_code, briefing.record_shift_date)
    output_path = exports_directory / file_name
    render_port_shift_briefing_docx(briefing, output_path)

    connection = create_database_connection(database_path)
    try:
        insert_audit_log(
            connection,
            event_type="port_r.shift_briefing.exported",
            module_name="port_r",
            event_level="info",
            actor_name=actor_name,
            entity_name=f"port_site_passport:{passport_id}",
            result_status="success",
            description_text=f"path={output_path};risks={len(briefing.key_risks)}",
        )
        connection.commit()
    finally:
        connection.close()

    return PortShiftBriefingExportResult(file_path=output_path, key_risks_count=len(briefing.key_risks))


def _build_file_name(passport_code: str, record_shift_date: str = "") -> str:
    creation_date = datetime.now().strftime("%Y-%m-%d")
    sanitized_code = _sanitize_filename_part(passport_code) or "passport"
    if record_shift_date:
        sanitized_date = _sanitize_filename_part(record_shift_date)
        return f"{sanitized_code}_зміна_{sanitized_date}_{creation_date}.docx"
    return f"{sanitized_code}_{creation_date}.docx"


def _sanitize_filename_part(raw_text: str) -> str:
    cleaned_characters = (character for character in (raw_text or "").strip() if character not in _INVALID_FILENAME_CHARS)
    return "".join(cleaned_characters).replace(" ", "_")
