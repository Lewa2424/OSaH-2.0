from pathlib import Path

from docx import Document
from docx.document import Document as DocumentType
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Cm, Pt
from docx.table import Table, _Cell

from osah.domain.entities.port_passport_status import PortPassportStatus
from osah.domain.entities.port_risk_level import PortRiskLevel
from osah.domain.entities.port_risk_profile import PortRiskProfile
from osah.domain.entities.port_shift_briefing import (
    PortShiftBriefing,
    PortShiftBriefingBarrier,
    PortShiftBriefingRisk,
)


_CHECKBOX_EMPTY: str = "\u2610"
_CHECKBOX_CHECKED: str = "\u2611"
_KEY_RISKS_COUNT: int = 5
_DYNAMIC_EVENTS_COUNT: int = 5
_DEFAULT_FONT_NAME: str = "Calibri"
_HEADING_FONT_SIZE: int = 13
_BODY_FONT_SIZE: int = 10


# ###### РЕНДЕР ОПЕРАТИВНОГО ЛИСТА ЗМІНИ У .DOCX / RENDER SHIFT BRIEFING TO .DOCX ######
def render_port_shift_briefing_docx(briefing: PortShiftBriefing, output_path: Path) -> Path:
    """Створює файл .docx оперативного листа зміни на основі підготовлених даних.
    Creates the .docx shift briefing file based on the prepared data.
    """

    output_path.parent.mkdir(parents=True, exist_ok=True)
    document = Document()
    _configure_default_style(document)

    _render_title(document, briefing.passport_code)
    _render_general_data_section(document, briefing)
    _render_base_profile_section(document, briefing)
    _render_key_risks_section(document, briefing.key_risks)
    _render_tpsvb_section(document)
    _render_barriers_section(document, briefing.barriers)
    _render_dynamic_events_section(document)
    _render_shift_summary_section(document)
    _render_signature_section(document)

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


def _render_title(document: DocumentType, passport_code: str) -> None:
    title_text = f"Паспорт ділянки {passport_code}".rstrip()
    title_paragraph = document.add_paragraph()
    title_paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = title_paragraph.add_run(title_text)
    run.bold = True
    run.font.size = Pt(_HEADING_FONT_SIZE + 2)


def _render_section_heading(document: DocumentType, text: str) -> None:
    paragraph = document.add_paragraph()
    paragraph.paragraph_format.space_before = Pt(6)
    paragraph.paragraph_format.space_after = Pt(0)
    run = paragraph.add_run(text)
    run.bold = True
    run.font.size = Pt(_HEADING_FONT_SIZE)


def _render_general_data_section(document: DocumentType, briefing: PortShiftBriefing) -> None:
    _render_section_heading(document, "1. ЗАГАЛЬНІ ДАНІ")

    work_kind_combined = _combine_two_lines(briefing.work_kind, briefing.typical_operations)
    cargo_combined = _combine_two_lines(briefing.typical_cargo, briefing.cargo_features)
    equipment_combined = _combine_two_lines(briefing.main_equipment, briefing.lifting_devices)
    site_combined = _combine_two_lines(briefing.site_name, briefing.site_location)

    rows: tuple[tuple[str, str], ...] = (
        ("Підприємство:", ""),
        ("Ділянка / причал / зона робіт:", site_combined),
        ("Дата:", ""),
        ("Зміна:", f"{_CHECKBOX_EMPTY} денна   {_CHECKBOX_EMPTY} нічна   {_CHECKBOX_EMPTY} інша: ____________"),
        ("Час робіт:", "з ________ до ________"),
        ("Вид робіт / операція:", work_kind_combined),
        ("Вантаж:", cargo_combined),
        ("Основна техніка:", equipment_combined),
        ("Відповідальний зміни (ПІБ):", ""),
        ("Посада:", ""),
    )
    _render_label_value_table(document, rows)


def _render_base_profile_section(document: DocumentType, briefing: PortShiftBriefing) -> None:
    _render_section_heading(document, "2. БАЗОВИЙ ПРОФІЛЬ ДІЛЯНКИ")

    profile_line = _build_profile_checkbox_line(briefing.final_profile)
    status_line = _build_status_checkbox_line(briefing.status)

    rows: tuple[tuple[str, str], ...] = (
        ("Профіль ризику за паспортом:", profile_line),
        ("Статус паспорта:", status_line),
        ("Дата актуалізації паспорта:", briefing.passport_updated_at),
        ("Паспорт актуальний для цієї зміни:", f"{_CHECKBOX_EMPTY} так   {_CHECKBOX_EMPTY} ні"),
        ("Якщо ні, причина:", ""),
    )
    _render_label_value_table(document, rows)


def _render_key_risks_section(document: DocumentType, key_risks: tuple[PortShiftBriefingRisk, ...]) -> None:
    _render_section_heading(document, "3. КЛЮЧОВІ РИЗИКИ ДІЛЯНКИ")

    table = document.add_table(rows=1, cols=4)
    table.style = "Light Grid Accent 1"
    header_cells = table.rows[0].cells
    header_cells[0].text = "№"
    header_cells[1].text = "Ризик-ситуація"
    header_cells[2].text = "Джерело небезпеки"
    header_cells[3].text = "Рівень"
    _format_table_header(table)

    for index in range(_KEY_RISKS_COUNT):
        row = table.add_row().cells
        row[0].text = str(index + 1)
        if index < len(key_risks):
            row[1].text = key_risks[index].risk_situation
            row[2].text = key_risks[index].hazard_source
            row[3].text = _build_risk_level_checkbox_line(key_risks[index].level)
        else:
            row[1].text = ""
            row[2].text = ""
            row[3].text = _build_risk_level_checkbox_line(None)

    _set_columns_widths(table, (Cm(0.8), Cm(7.0), Cm(5.5), Cm(4.0)))

    legend = document.add_paragraph()
    legend.paragraph_format.space_before = Pt(4)
    legend_run = legend.add_run("Позначення: Н — низький, С — середній, В — високий, К — критичний.")
    legend_run.italic = True


def _render_tpsvb_section(document: DocumentType) -> None:
    _render_section_heading(document, "4. ПЕРЕВІРКА Т-П-С-В-Б ПЕРЕД ПОЧАТКОМ РОБІТ")

    table = document.add_table(rows=1, cols=3)
    table.style = "Light Grid Accent 1"
    header_cells = table.rows[0].cells
    header_cells[0].text = "Змінна"
    header_cells[1].text = "Стан"
    header_cells[2].text = "Коментар / відхилення"
    _format_table_header(table)

    variables = ("Техніка", "Персонал", "Умови", "Вантаж", "Бар'єри")
    for variable in variables:
        row = table.add_row().cells
        row[0].text = variable
        row[1].text = f"{_CHECKBOX_EMPTY} зелена   {_CHECKBOX_EMPTY} жовта   {_CHECKBOX_EMPTY} червона"
        row[2].text = ""

    _set_columns_widths(table, (Cm(2.5), Cm(7.5), Cm(7.0)))

    decision_paragraph = document.add_paragraph()
    decision_paragraph.paragraph_format.space_before = Pt(6)
    decision_run = decision_paragraph.add_run("Рішення перед початком робіт:")
    decision_run.bold = True
    document.add_paragraph(
        f"{_CHECKBOX_EMPTY} допустити до роботи   "
        f"{_CHECKBOX_EMPTY} допустити після посилення бар'єрів   "
        f"{_CHECKBOX_EMPTY} зупинити / не допускати"
    )
    document.add_paragraph("Коментар: ____________________________________________________________")


def _render_barriers_section(
    document: DocumentType,
    barriers: tuple[PortShiftBriefingBarrier, ...],
) -> None:
    _render_section_heading(document, "5. ПЕРЕВІРКА КРИТИЧНИХ БАР'ЄРІВ")

    table = document.add_table(rows=1, cols=3)
    table.style = "Light Grid Accent 1"
    header_cells = table.rows[0].cells
    header_cells[0].text = "Бар'єр"
    header_cells[1].text = "Стан перед початком"
    header_cells[2].text = "Коментар"
    _format_table_header(table)

    for barrier in barriers:
        row = table.add_row().cells
        row[0].text = barrier.name
        row[1].text = _build_barrier_state_placeholder(barrier.name)
        row[2].text = barrier.comment

    _set_columns_widths(table, (Cm(4.0), Cm(7.0), Cm(6.0)))

    conclusion_paragraph = document.add_paragraph()
    conclusion_paragraph.paragraph_format.space_before = Pt(4)
    conclusion_run = conclusion_paragraph.add_run("Висновок щодо бар'єрів:")
    conclusion_run.bold = True
    document.add_paragraph(
        f"{_CHECKBOX_EMPTY} бар'єри забезпечені   "
        f"{_CHECKBOX_EMPTY} потрібне посилення бар'єрів   "
        f"{_CHECKBOX_EMPTY} втрачено критичний бар'єр, роботи зупинити"
    )


def _render_dynamic_events_section(document: DocumentType) -> None:
    _render_section_heading(document, "6. ФАКТИЧНІ ЗМІНИ ПІД ЧАС ЗМІНИ")

    hint = document.add_paragraph()
    hint_run = hint.add_run("Заповнюється тільки у разі відхилення від штатного режиму.")
    hint_run.italic = True

    table = document.add_table(rows=1, cols=5)
    table.style = "Light Grid Accent 1"
    header_cells = table.rows[0].cells
    header_cells[0].text = "Час"
    header_cells[1].text = "Що змінилось / що сталося"
    header_cells[2].text = "Змінна Т-П-С-В-Б"
    header_cells[3].text = "Дія / бар'єр"
    header_cells[4].text = "Рішення"
    _format_table_header(table)

    for _ in range(_DYNAMIC_EVENTS_COUNT):
        row = table.add_row().cells
        row[0].text = ""
        row[1].text = ""
        row[2].text = ""
        row[3].text = ""
        row[4].text = (
            f"{_CHECKBOX_EMPTY} допустити   "
            f"{_CHECKBOX_EMPTY} посилити   "
            f"{_CHECKBOX_EMPTY} зупинити"
        )

    _set_columns_widths(table, (Cm(1.6), Cm(5.0), Cm(2.6), Cm(3.5), Cm(4.3)))

    document.add_paragraph()
    legend_heading = document.add_paragraph()
    legend_heading_run = legend_heading.add_run("Розшифровка Т-П-С-В-Б:")
    legend_heading_run.bold = True
    legend_lines = (
        "Т — Техніка: крани, навантажувачі, тягачі, транспорт, ВЗП, стропи, захвати, технічний стан обладнання.",
        "П — Персонал: склад бригади, сторонні особи, підрядники, екіпаж, тальмани, сюрвеєри, перебування людей у небезпечній зоні.",
        "С — Середовище / умови: погода, вітер, дощ, туман, ожеледь, стан покриття, видимість, хвилювання, освітлення.",
        "В — Вантаж: стан вантажу, пакування, маркування, стійкість, центр ваги, пошкодження, розлив, задимлення, невідповідність документам.",
        "Б — Бар'єри: зв'язок, огородження, зонування, сигнальник, ЗІЗ, маршрути руху, попереджувальні знаки, контроль доступу.",
    )
    for line in legend_lines:
        document.add_paragraph(line)


def _render_shift_summary_section(document: DocumentType) -> None:
    _render_section_heading(document, "7. ПІДСУМОК ЗМІНИ")

    document.add_paragraph("Роботи виконані:")
    document.add_paragraph(
        f"{_CHECKBOX_EMPTY} без відхилень   "
        f"{_CHECKBOX_EMPTY} з відхиленнями, усуненими під час зміни   "
        f"{_CHECKBOX_EMPTY} з відхиленнями, що потребують подальших заходів   "
        f"{_CHECKBOX_EMPTY} роботи були зупинені"
    )

    document.add_paragraph("Чи були застосовані додаткові бар'єри:")
    document.add_paragraph(f"{_CHECKBOX_EMPTY} ні   {_CHECKBOX_EMPTY} так")
    document.add_paragraph("Якщо так, які саме: ____________________________________________________")

    document.add_paragraph("Чи потрібно передати інформацію до служби охорони праці / інспектора:")
    document.add_paragraph(f"{_CHECKBOX_EMPTY} ні   {_CHECKBOX_EMPTY} так")
    document.add_paragraph("Що передати: __________________________________________________________")


def _render_signature_section(document: DocumentType) -> None:
    _render_section_heading(document, "8. ПІДПИС ВІДПОВІДАЛЬНОГО ЗМІНИ")
    document.add_paragraph(
        "Відповідальний зміни підтверджує, що ознайомився з паспортом ділянки, перевірив "
        "критичні бар'єри, зафіксував відхилення під час зміни та прийняв рішення відповідно "
        "до фактичного стану робочої зони."
    )

    rows: tuple[tuple[str, str], ...] = (
        ("ПІБ:", ""),
        ("Посада:", ""),
        ("Підпис:", ""),
        ("Дата:", ""),
        ("Час:", ""),
    )
    _render_label_value_table(document, rows)


def _render_label_value_table(document: DocumentType, rows: tuple[tuple[str, str], ...]) -> None:
    table = document.add_table(rows=len(rows), cols=2)
    table.style = "Light List Accent 1"
    for index, (label_text, value_text) in enumerate(rows):
        label_cell = table.rows[index].cells[0]
        value_cell = table.rows[index].cells[1]
        _set_label_cell(label_cell, label_text)
        value_cell.text = value_text
    _set_columns_widths(table, (Cm(6.5), Cm(10.5)))


def _set_label_cell(cell: _Cell, label_text: str) -> None:
    cell.text = ""
    paragraph = cell.paragraphs[0]
    run = paragraph.add_run(label_text)
    run.bold = True


def _format_table_header(table: Table) -> None:
    header_row = table.rows[0]
    for cell in header_row.cells:
        paragraph = cell.paragraphs[0]
        for run in paragraph.runs:
            run.bold = True


def _set_columns_widths(table: Table, widths: tuple) -> None:
    for column_index, width in enumerate(widths):
        for row in table.rows:
            row.cells[column_index].width = width


def _build_profile_checkbox_line(profile: PortRiskProfile) -> str:
    return (
        f"{_render_checkbox(profile == PortRiskProfile.LOW)} низький   "
        f"{_render_checkbox(profile == PortRiskProfile.MEDIUM)} середній   "
        f"{_render_checkbox(profile == PortRiskProfile.HIGH)} високий   "
        f"{_render_checkbox(profile == PortRiskProfile.CRITICAL)} критичний"
    )


def _build_status_checkbox_line(status: PortPassportStatus) -> str:
    return (
        f"{_render_checkbox(status == PortPassportStatus.ACTIVE)} діючий   "
        f"{_render_checkbox(status == PortPassportStatus.NEEDS_ACTIONS)} потребує заходів   "
        f"{_CHECKBOX_EMPTY} не актуальний для цієї зміни"
    )


def _build_risk_level_checkbox_line(level: PortRiskLevel | None) -> str:
    return (
        f"{_render_checkbox(level == PortRiskLevel.LOW)} Н   "
        f"{_render_checkbox(level == PortRiskLevel.MEDIUM)} С   "
        f"{_render_checkbox(level == PortRiskLevel.HIGH)} В   "
        f"{_render_checkbox(level == PortRiskLevel.CRITICAL)} К"
    )


def _build_barrier_state_placeholder(barrier_name: str) -> str:
    if barrier_name == "Освітлення":
        return (
            f"{_CHECKBOX_EMPTY} достатнє   "
            f"{_CHECKBOX_EMPTY} недостатнє   "
            f"{_CHECKBOX_EMPTY} не потрібне"
        )
    if barrier_name == "ЗІЗ":
        return f"{_CHECKBOX_EMPTY} забезпечено   {_CHECKBOX_EMPTY} не повністю"
    if barrier_name == "ВЗП / стропи / захвати":
        return f"{_CHECKBOX_EMPTY} справні   {_CHECKBOX_EMPTY} є зауваження"
    if barrier_name == "Проходи / проїзди":
        return f"{_CHECKBOX_EMPTY} вільні   {_CHECKBOX_EMPTY} обмежені"
    if barrier_name == "Сигнальник":
        return f"{_CHECKBOX_EMPTY} є   {_CHECKBOX_EMPTY} немає   {_CHECKBOX_EMPTY} не потрібен"
    return f"{_CHECKBOX_EMPTY} є   {_CHECKBOX_EMPTY} немає   {_CHECKBOX_EMPTY} частково"


def _render_checkbox(is_checked: bool) -> str:
    return _CHECKBOX_CHECKED if is_checked else _CHECKBOX_EMPTY


def _combine_two_lines(primary: str, secondary: str) -> str:
    primary_text = primary.strip() if primary else ""
    secondary_text = secondary.strip() if secondary else ""
    if not primary_text:
        return secondary_text
    if not secondary_text:
        return primary_text
    if primary_text.casefold() == secondary_text.casefold():
        return primary_text
    return f"{primary_text}\n{secondary_text}"
