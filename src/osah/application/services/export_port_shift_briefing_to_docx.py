from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from osah.application.services.load_port_site_passport_for_edit import load_port_site_passport_for_edit
from osah.application.services.load_port_site_risks_for_passport import load_port_site_risks_for_passport
from osah.application.services.security.ensure_write_access import ensure_write_access
from osah.domain.entities.access_role import AccessRole
from osah.domain.services.build_port_shift_briefing import build_port_shift_briefing
from osah.infrastructure.database.commands.insert_audit_log import insert_audit_log
from osah.infrastructure.database.create_database_connection import create_database_connection
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
    briefing = build_port_shift_briefing(passport_row, passport_input, risks)

    exports_directory = build_port_r_exports_directory(project_root)
    file_name = _build_file_name(passport_row.passport_code)
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


def _build_file_name(passport_code: str) -> str:
    creation_date = datetime.now().strftime("%Y-%m-%d")
    sanitized_code = _sanitize_filename_part(passport_code) or "passport"
    return f"{sanitized_code}_{creation_date}.docx"


def _sanitize_filename_part(raw_text: str) -> str:
    cleaned_characters = (character for character in (raw_text or "").strip() if character not in _INVALID_FILENAME_CHARS)
    return "".join(cleaned_characters).replace(" ", "_")
