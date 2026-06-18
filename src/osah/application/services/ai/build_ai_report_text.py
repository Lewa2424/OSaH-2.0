from pathlib import Path

from osah.application.services.build_daily_report_document import build_daily_report_document
from osah.application.services.ai.query_overdue_summary import query_overdue_summary
from osah.domain.services.build_daily_report_email_body_text import build_daily_report_email_body_text


def build_ai_report_text(database_path: Path, report_scope: str | None = None) -> str:
    """Повертає текст звіту для AI-панелі.
    Returns report text for the AI panel.
    """

    normalized_scope = (report_scope or "daily").strip().lower()
    if normalized_scope in {"module", "overdue", "простроч", "просроч"}:
        summary = query_overdue_summary(database_path)
        return (
            "Зведення прострочень:\n"
            f"• ЗІЗ прострочено: {summary.ppe_expired}\n"
            f"• ЗІЗ не видано: {summary.ppe_not_issued}\n"
            f"• ЗІЗ попередження: {summary.ppe_warning}\n"
            f"• Інструктажі прострочено: {summary.training_overdue}\n"
            f"• Медицина прострочена: {summary.medical_expired}\n"
            f"• Наряди прострочені: {summary.work_permit_expired}"
        )

    document = build_daily_report_document(database_path)
    body_text = build_daily_report_email_body_text(document.snapshot)
    sections_preview: list[str] = []
    for section in document.snapshot.sections[:4]:
        if not section.rows:
            continue
        sections_preview.append(f"{section.title}: {len(section.rows)} запис(ів)")
    preview = "\n".join(sections_preview)
    if preview:
        return f"{body_text}\n\nОсновні блоки:\n{preview}"
    return body_text
