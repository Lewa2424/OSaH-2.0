from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget

from osah.domain.entities.work_permit_workspace_row import WorkPermitWorkspaceRow
from osah.domain.services.build_work_permit_conflict_guidance import build_work_permit_conflict_guidance
from osah.ui.qt.design.tokens import COLOR, RADIUS, SPACING


class PermitParticipantsPanel(QWidget):
    """Панель учасників і конфліктів наряду.
    Panel with work permit participants and conflicts.
    """

    def __init__(self) -> None:
        super().__init__()
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(SPACING["xs"])

    def set_row(self, row: WorkPermitWorkspaceRow | None) -> None:
        """Показує учасників і причини конфліктів вибраного наряду.
        Shows participants and conflict reasons for the selected work permit.
        """

        while self._layout.count():
            item = self._layout.takeAt(0)
            if widget := item.widget():
                widget.deleteLater()
        if row is None:
            self._layout.addWidget(_label("Оберіть наряд у таблиці зліва.", COLOR["text_muted"], bold=False))
            return

        self._layout.addWidget(_workflow_label())
        if row.participant_count > 0:
            self._layout.addWidget(
                _label(f"Бригада ({row.participant_count}): {row.participant_names}", COLOR["text_secondary"], bold=True)
            )
        else:
            self._layout.addWidget(_label("Бригада: ще не задана", COLOR["warning"], bold=True))

        guidance = build_work_permit_conflict_guidance(row)
        if row.conflict_reasons:
            for reason in row.conflict_reasons:
                self._layout.addWidget(_label(f"Увага: {reason}", COLOR["critical"], bold=True))
            self._layout.addWidget(_guidance_box(guidance))
        else:
            self._layout.addWidget(_label("Допуск: критичних перешкод немає.", COLOR["success"], bold=True))
            if guidance:
                self._layout.addWidget(_label(guidance, COLOR["text_muted"], bold=False))


def _workflow_label() -> QLabel:
    """Короткий порядок дій для інспектора.
    Short workflow reminder for the inspector.
    """

    label = QLabel(
        "Порядок: 1) бригада → 2) цільовий інструктаж → 3) «Зберегти зміни» → "
        "4) щоденна перевірка (якщо роботи кілька днів)."
    )
    label.setWordWrap(True)
    label.setStyleSheet(
        f"color: {COLOR['text_secondary']}; background: {COLOR['bg_workspace']}; "
        f"border-radius: {RADIUS['md']}px; padding: 8px 10px;"
    )
    return label


def _guidance_box(text: str) -> QLabel:
    """Підказка «що зробити далі».
    Next-step guidance box.
    """

    label = QLabel(f"Що зробити: {text}")
    label.setWordWrap(True)
    label.setStyleSheet(
        f"color: {COLOR['text_primary']}; background: {COLOR['warning_subtle']}; "
        f"border: 1px solid {COLOR['warning']}; border-radius: {RADIUS['md']}px; "
        f"padding: 8px 10px; font-weight: 700;"
    )
    return label


def _label(text: str, color: str, *, bold: bool) -> QLabel:
    """Створює службовий текстовий рядок панелі.
    Creates a helper text line for the panel.
    """

    label = QLabel(text)
    label.setWordWrap(True)
    weight = "800" if bold else "500"
    label.setStyleSheet(f"color: {color}; font-weight: {weight};")
    return label
