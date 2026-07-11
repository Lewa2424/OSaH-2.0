from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget

from osah.domain.entities.work_permit_workspace_row import WorkPermitWorkspaceRow
from osah.domain.services.build_work_permit_conflict_guidance import build_work_permit_conflict_guidance
from osah.ui.qt.design.tokens import COLOR, RADIUS, SPACING


class PermitParticipantsPanel(QWidget):
    """Panel with work permit participants and conflicts. / Панель учасників і конфліктів наряду."""

    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("permitParticipantsPanel")
        self.setStyleSheet(
            f"""
            QWidget#permitParticipantsPanel {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(250,252,254,0.98),
                    stop:1 rgba(243,247,251,0.98));
                border: 1px solid #D9E2EC;
                border-radius: {RADIUS['xl']}px;
            }}
            QLabel {{
                font-size: 14px;
            }}
            """
        )
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(SPACING["lg"], SPACING["md"], SPACING["lg"], SPACING["md"])
        self._layout.setSpacing(SPACING["sm"])

    def set_row(self, row: WorkPermitWorkspaceRow | None) -> None:
        while self._layout.count():
            item = self._layout.takeAt(0)
            if widget := item.widget():
                widget.deleteLater()
        if row is None:
            self._layout.addWidget(_label("Оберіть наряд у таблиці зліва.", COLOR["text_muted"], bold=False))
            return

        self._layout.addWidget(_workflow_label())
        if row.participant_count > 0:
            self._layout.addWidget(_label(f"Бригада ({row.participant_count}): {row.participant_names}", COLOR["text_secondary"], bold=True))
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
    label = QLabel(
        "Порядок: 1) бригада -> 2) цільовий інструктаж -> 3) зберегти зміни -> 4) щоденна перевірка, якщо роботи тривають кілька днів."
    )
    label.setWordWrap(True)
    label.setStyleSheet(
        f"color: {COLOR['text_secondary']}; background: #F5F8FC; border-radius: {RADIUS['md']}px; padding: 10px 12px; font-weight: 700;"
    )
    return label


def _guidance_box(text: str) -> QLabel:
    label = QLabel(f"Що зробити: {text}")
    label.setWordWrap(True)
    label.setStyleSheet(
        f"color: {COLOR['text_primary']}; background: {COLOR['warning_subtle']}; border: 1px solid {COLOR['warning']}; "
        f"border-radius: {RADIUS['md']}px; padding: 10px 12px; font-weight: 800;"
    )
    return label


def _label(text: str, color: str, *, bold: bool) -> QLabel:
    label = QLabel(text)
    label.setWordWrap(True)
    weight = "800" if bold else "500"
    label.setStyleSheet(f"color: {color}; font-weight: {weight};")
    return label
