from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
)

from osah.domain.entities.port_risk_level import PORT_RISK_LEVEL_LABELS, PortRiskLevel
from osah.ui.qt.design.tokens import COLOR, SPACING


class AcceptRiskDialog(QDialog):
    """Діалог прийняття ризику з вибором рівня.
    Dialog for accepting a risk and assigning a risk level.
    """

    def __init__(self, risk_situation: str, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Прийняти ризик")
        self.setModal(True)
        self.setMinimumWidth(500)
        self.setStyleSheet(
            f"""
            QDialog {{
                background:
                    qlineargradient(x1:0, y1:0, x2:1, y2:1,
                        stop:0 rgba(255, 255, 255, 248),
                        stop:1 rgba(232, 240, 248, 234));
            }}
            QLabel {{
                font-size: 15px;
                color: {COLOR['text_primary']};
            }}
            QComboBox,
            QLineEdit {{
                min-height: 40px;
                background: #FFFFFF;
                border: 1px solid #C8D6E5;
                border-radius: 14px;
                padding: 0 12px;
                font-size: 14px;
                font-weight: 600;
            }}
            QPushButton {{
                min-height: 40px;
                border-radius: 14px;
                font-size: 14px;
                font-weight: 800;
            }}
            """
        )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(SPACING["lg"], SPACING["lg"], SPACING["lg"], SPACING["lg"])
        layout.setSpacing(SPACING["md"])

        situation_label = QLabel(risk_situation)
        situation_label.setWordWrap(True)
        situation_label.setStyleSheet("font-weight: bold; font-size: 12px;")
        layout.addWidget(situation_label)

        level_label = QLabel("Рівень ризику:")
        layout.addWidget(level_label)
        self._level_combo = QComboBox()
        for level, label in PORT_RISK_LEVEL_LABELS.items():
            self._level_combo.addItem(label, level.value)
        layout.addWidget(self._level_combo)

        reason_label = QLabel("Обгрунтування (необов'язково):")
        layout.addWidget(reason_label)
        self._reason_input = QLineEdit()
        self._reason_input.setPlaceholderText("Опис підстав для оцінки рівня ризику")
        layout.addWidget(self._reason_input)

        comment_label = QLabel("Коментар інспектора (необов'язково):")
        layout.addWidget(comment_label)
        self._comment_input = QLineEdit()
        self._comment_input.setPlaceholderText("Додатковий коментар")
        layout.addWidget(self._comment_input)

        buttons = QHBoxLayout()
        cancel_btn = QPushButton("Скасувати")
        cancel_btn.setProperty("variant", "secondary")
        cancel_btn.clicked.connect(self.reject)
        buttons.addWidget(cancel_btn)
        buttons.addStretch()
        accept_btn = QPushButton("Прийняти ризик")
        accept_btn.setProperty("variant", "accent")
        accept_btn.clicked.connect(self.accept)
        buttons.addWidget(accept_btn)
        layout.addLayout(buttons)

    def selected_level(self) -> PortRiskLevel:
        return PortRiskLevel(self._level_combo.currentData())

    def assessment_reason(self) -> str:
        return self._reason_input.text().strip()

    def inspector_comment(self) -> str:
        return self._comment_input.text().strip()
