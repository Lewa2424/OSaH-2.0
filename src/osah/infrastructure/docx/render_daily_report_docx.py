from pathlib import Path

from docx import Document
from docx.document import Document as DocumentType
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Cm, Pt
from docx.table import _Cell

from osah.domain.entities.daily_report_section import DailyReportSection
from osah.domain.entities.daily_report_snapshot import DailyReportSnapshot
from osah.domain.entities.daily_report_table_row import DailyReportTableRow

_DEFAULT_FONT_NAME: str = "Calibri"
_HEADING_FONT_SIZE: int = 13
_BODY_FONT_SIZE: int = 10


# ###### РЕНДЕР ЩОДЕННОГО ЗВІТУ У .DOCX / RENDER DAILY REPORT TO .DOCX ######
def render_daily_report_docx(snapshot: DailyReportSnapshot, output_path: Path) -> Path:
    """Створює файл .docx щоденного звіту на основі підготовленого знімка.
    Creates the .docx daily report file from the prepared snapshot.
    """

    output_path.parent.mkdir(parents=True, exist_ok=True)
    document = Document()
    _configure_default_style(document)

    _render_title(document, snapshot.enterprise_name)
    _render_header_section(document, snapshot)

    for section_index, section in enumerate(snapshot.sections, start=1):
        _render_problem_section(document, section_index, section)

    _render_no_remarks_section(document, snapshot)

    document.save(str(output_path))
    return output_path


def _configure_default_style(document: DocumentType) -> None:
    style = document.styles["Normal"]
    style.font.name = _DEFAULT_FONT_NAME
    style.font.size = Pt(_BODY_FONT_SIZE)
    paragraph_format = style.paragraph_format
    paragraph_format.space_before = Pt(0)
    paragraph_format.space_after = Pt(0)
    paragraph_format.line_spacing = 1.0

    for section in document.sections:
        section.left_margin = Cm(2.0)
        section.right_margin = Cm(1.5)


def _render_title(document: DocumentType, enterprise_name: str) -> None:
    title_paragraph = document.add_paragraph()
    title_paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = title_paragraph.add_run("Щоденний звіт з охорони праці")
    run.bold = True
    run.font.size = Pt(_HEADING_FONT_SIZE + 2)

    subtitle_paragraph = document.add_paragraph()
    subtitle_paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    subtitle_run = subtitle_paragraph.add_run(enterprise_name)
    subtitle_run.font.size = Pt(_HEADING_FONT_SIZE)


def _render_header_section(document: DocumentType, snapshot: DailyReportSnapshot) -> None:
    _render_section_heading(document, "Загальні дані")
    rows: tuple[tuple[str, str], ...] = (
        ("Дата формування:", snapshot.created_at_text),
        ("Працівників у системі:", str(snapshot.employee_total)),
        ("Критичних проблем:", str(snapshot.critical_items)),
        ("Проблем, що потребують уваги:", str(snapshot.warning_items)),
        ("Фокус дня:", snapshot.focus_of_the_day),
    )
    _render_label_value_table(document, rows)


def _render_problem_section(
    document: DocumentType,
    section_index: int,
    section: DailyReportSection,
) -> None:
    _render_section_heading(document, f"{section_index}. {section.title}")
    if not section.rows:
        paragraph = document.add_paragraph("Зауважень у цьому контурі не виявлено.")
        paragraph.paragraph_format.space_after = Pt(4)
        return

    table = document.add_table(rows=1, cols=4)
    table.style = "Light Grid Accent 1"
    headers = ("Працівник", "Опис проблеми", "Строки/дати", "Примітки")
    for column_index, header_text in enumerate(headers):
        cell = table.rows[0].cells[column_index]
        _set_cell_text(cell, header_text, bold=True)

    for row in section.rows:
        table_row = table.add_row()
        _set_cell_text(table_row.cells[0], row.subject_block)
        _set_cell_text(table_row.cells[1], row.problem_text)
        _set_cell_text(table_row.cells[2], row.dates_text)
        _set_cell_text(table_row.cells[3], row.notes_text)


def _render_no_remarks_section(document: DocumentType, snapshot: DailyReportSnapshot) -> None:
    _render_section_heading(document, "Без зауважень")

    if snapshot.no_remarks_employees:
        employees_heading = document.add_paragraph()
        employees_run = employees_heading.add_run("Працівники:")
        employees_run.bold = True
        for line in snapshot.no_remarks_employees:
            document.add_paragraph(line, style="List Bullet")

    if snapshot.no_remarks_contractors:
        contractors_heading = document.add_paragraph()
        contractors_run = contractors_heading.add_run("Підрядники:")
        contractors_run.bold = True
        for line in snapshot.no_remarks_contractors:
            document.add_paragraph(line, style="List Bullet")

    if not snapshot.no_remarks_employees and not snapshot.no_remarks_contractors:
        document.add_paragraph("Усі позиції мають зауваження або потребують перевірки.")


def _render_section_heading(document: DocumentType, text: str) -> None:
    paragraph = document.add_paragraph()
    paragraph.paragraph_format.space_before = Pt(6)
    paragraph.paragraph_format.space_after = Pt(2)
    run = paragraph.add_run(text)
    run.bold = True
    run.font.size = Pt(_HEADING_FONT_SIZE)


def _render_label_value_table(document: DocumentType, rows: tuple[tuple[str, str], ...]) -> None:
    table = document.add_table(rows=len(rows), cols=2)
    table.style = "Light Grid Accent 1"
    for row_index, (label_text, value_text) in enumerate(rows):
        label_cell = table.rows[row_index].cells[0]
        value_cell = table.rows[row_index].cells[1]
        _set_cell_text(label_cell, label_text, bold=True)
        _set_cell_text(value_cell, value_text)


def _set_cell_text(cell: _Cell, text: str, *, bold: bool = False) -> None:
    cell.text = ""
    paragraph = cell.paragraphs[0]
    for line_index, line in enumerate(text.split("\n")):
        if line_index > 0:
            paragraph = cell.add_paragraph()
        run = paragraph.add_run(line)
        run.bold = bold
        run.font.name = _DEFAULT_FONT_NAME
        run.font.size = Pt(_BODY_FONT_SIZE)
