from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtSvgWidgets import QSvgWidget
from PySide6.QtWidgets import (
    QFrame,
    QHeaderView,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from osah.ui.qt.design.tokens import COLOR, SPACING

_ASSETS_DIR = Path(__file__).resolve().parent.parent.parent / "assets" / "instructions"


def instruction_assets_dir() -> Path:
    """Повертає каталог SVG/PNG для інструкцій.
    Returns the assets directory for instruction diagrams.
    """

    return _ASSETS_DIR


def build_instruction_page(*sections: QWidget) -> QWidget:
    """Збирає сторінку інструкції з блоків-карток.
    Assembles an instruction page from card widgets.
    """

    page = QWidget()
    layout = QVBoxLayout(page)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(SPACING["lg"])
    for section in sections:
        layout.addWidget(section)
    layout.addStretch()
    return page


def InstructionCard(title: str, paragraphs: tuple[str, ...]) -> QFrame:
    """Текстова картка інструкції з заголовком і абзацами.
    Instruction text card with a title and body paragraphs.
    """

    card = _base_card()
    layout = card.layout()
    layout.addWidget(_card_title(title))
    for paragraph in paragraphs:
        layout.addWidget(_body_label(paragraph))
    return card


def InstructionBulletList(title: str, items: tuple[str, ...]) -> QFrame:
    """Картка з маркованим списком.
    Instruction card with a bullet list.
    """

    card = _base_card()
    layout = card.layout()
    layout.addWidget(_card_title(title))
    list_html = "".join(f"<li>{item}</li>" for item in items)
    label = QLabel(f"<ul style='margin-top:0;margin-bottom:0;padding-left:20px;'>{list_html}</ul>")
    label.setWordWrap(True)
    label.setStyleSheet("font-size: 13px;")
    layout.addWidget(label)
    return card


def InstructionDiagram(relative_path: str, caption: str = "", max_width: int = 760) -> QWidget:
    """Відображає SVG-схему з підписом.
    Displays an SVG diagram with an optional caption.
    """

    wrapper = QWidget()
    layout = QVBoxLayout(wrapper)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(SPACING["xs"])

    svg_path = _ASSETS_DIR / relative_path
    if svg_path.is_file():
        svg = QSvgWidget(str(svg_path))
        renderer = svg.renderer()
        if renderer.isValid():
            view_box = renderer.viewBoxF()
            if view_box.width() > 0 and view_box.height() > 0:
                height = max(1, round(max_width * view_box.height() / view_box.width()))
                svg.setFixedSize(max_width, height)
            else:
                svg.setFixedWidth(max_width)
            layout.addWidget(svg, alignment=Qt.AlignmentFlag.AlignHCenter)
        else:
            missing = QLabel(f"[Схему не вдалося відобразити: {relative_path}]")
            missing.setWordWrap(True)
            missing.setStyleSheet(f"color: {COLOR['text_muted']}; font-style: italic;")
            layout.addWidget(missing)
    else:
        missing = QLabel(f"[Схема недоступна: {relative_path}]")
        missing.setStyleSheet(f"color: {COLOR['text_muted']}; font-style: italic;")
        layout.addWidget(missing)

    if caption.strip():
        caption_label = QLabel(caption)
        caption_label.setWordWrap(True)
        caption_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        caption_label.setStyleSheet(f"color: {COLOR['text_secondary']}; font-size: 12px;")
        layout.addWidget(caption_label)

    return wrapper


def InstructionTable(
    title: str,
    headers: tuple[str, ...],
    rows: tuple[tuple[str, ...], ...],
) -> QFrame:
    """Таблиця для методичних матеріалів (зони, статуси тощо).
    Read-only table for methodological reference data.
    """

    card = _base_card()
    layout = card.layout()
    layout.addWidget(_card_title(title))

    table = QTableWidget(len(rows), len(headers))
    table.setHorizontalHeaderLabels(list(headers))
    table.verticalHeader().setVisible(False)
    table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
    table.setSelectionMode(QTableWidget.SelectionMode.NoSelection)
    table.setAlternatingRowColors(True)
    table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
    table.setMaximumHeight(40 + len(rows) * 36)

    for row_index, row in enumerate(rows):
        for col_index, cell in enumerate(row):
            item = QTableWidgetItem(cell)
            item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            table.setItem(row_index, col_index, item)

    layout.addWidget(table)
    return card


def InstructionExample(title: str, lines: tuple[str, ...]) -> QFrame:
    """Виділений блок з числовим або сценарним прикладом.
    Highlighted block for a numeric or scenario example.
    """

    card = QFrame()
    card.setProperty("card", "true")
    card.setStyleSheet(
        f"QFrame[card='true'] {{ background: {COLOR['accent_soft']}; "
        f"border: 1px solid {COLOR['border_soft']}; border-radius: 8px; }}"
    )
    layout = QVBoxLayout(card)
    layout.setContentsMargins(SPACING["lg"], SPACING["md"], SPACING["lg"], SPACING["md"])
    layout.setSpacing(SPACING["xs"])
    layout.addWidget(_card_title(title))
    for line in lines:
        mono = QLabel(line)
        mono.setWordWrap(True)
        mono.setFont(QFont("Consolas", 12))
        layout.addWidget(mono)
    return card


def InstructionWorkflow(title: str, steps: tuple[tuple[str, str], ...]) -> QFrame:
    """Покроковий сценарій роботи.
    Step-by-step workflow card.
    """

    card = _base_card()
    layout = card.layout()
    layout.addWidget(_card_title(title))
    for index, (step_title, step_body) in enumerate(steps, start=1):
        step_label = QLabel(f"<b>{index}. {step_title}</b><br>{step_body}")
        step_label.setWordWrap(True)
        step_label.setStyleSheet("font-size: 13px; margin-bottom: 6px;")
        layout.addWidget(step_label)
    return card


def InstructionActionGuide(
    *,
    tracks: tuple[tuple[str, tuple[tuple[str, str], ...]], ...] = (),
    branches: tuple[tuple[str, str], ...] = (),
) -> QFrame:
    """Алгоритм дій: один або кілька треків і опційні розгалуження.
    Action guide with one or more tracks and optional decision branches.
    """

    card = QFrame()
    card.setProperty("card", "true")
    card.setStyleSheet(
        f"QFrame[card='true'] {{ background: {COLOR['accent_soft']}; "
        f"border: 1px solid {COLOR['border_soft']}; border-radius: 8px; }}"
    )
    layout = QVBoxLayout(card)
    layout.setContentsMargins(SPACING["lg"], SPACING["md"], SPACING["lg"], SPACING["md"])
    layout.setSpacing(SPACING["sm"])
    layout.addWidget(_card_title("Алгоритм дій"))

    for track_title, steps in tracks:
        if track_title.strip():
            track_label = QLabel(track_title)
            track_label.setWordWrap(True)
            track_font = QFont("Segoe UI", 13)
            track_font.setBold(True)
            track_label.setFont(track_font)
            layout.addWidget(track_label)
        for index, (step_title, step_body) in enumerate(steps, start=1):
            step_label = QLabel(f"<b>{index}. {step_title}</b><br>{step_body}")
            step_label.setWordWrap(True)
            step_label.setStyleSheet("font-size: 13px; margin-bottom: 6px;")
            layout.addWidget(step_label)

    if branches:
        branch_title = QLabel("Можливі розгалуження")
        branch_font = QFont("Segoe UI", 13)
        branch_font.setBold(True)
        branch_title.setFont(branch_font)
        layout.addWidget(branch_title)
        branch_html = "".join(
            f"<li><b>{condition}</b> — {action}</li>" for condition, action in branches
        )
        branch_label = QLabel(
            f"<ul style='margin-top:0;margin-bottom:0;padding-left:20px;'>{branch_html}</ul>"
        )
        branch_label.setWordWrap(True)
        branch_label.setStyleSheet("font-size: 13px;")
        layout.addWidget(branch_label)

    return card


def InstructionDiagramCard(title: str, relative_path: str, caption: str = "") -> QFrame:
    """Картка зі схемою всередині.
    Card wrapping a diagram with a section title.
    """

    card = _base_card()
    layout = card.layout()
    layout.addWidget(_card_title(title))
    layout.addWidget(InstructionDiagram(relative_path, caption))
    return card


def _base_card() -> QFrame:
    card = QFrame()
    card.setProperty("card", "true")
    layout = QVBoxLayout(card)
    layout.setContentsMargins(SPACING["lg"], SPACING["lg"], SPACING["lg"], SPACING["lg"])
    layout.setSpacing(SPACING["sm"])
    return card


def _card_title(text: str) -> QLabel:
    label = QLabel(text)
    label.setWordWrap(True)
    font = QFont("Segoe UI", 15)
    font.setBold(True)
    label.setFont(font)
    return label


def _body_label(text: str) -> QLabel:
    label = QLabel(text)
    label.setWordWrap(True)
    label.setFont(QFont("Segoe UI", 13))
    return label
