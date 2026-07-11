from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QAbstractItemView,
    QDialog,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
)

from osah.domain.entities.employee_import_draft import EmployeeImportDraft
from osah.domain.entities.employee_import_draft_status import EmployeeImportDraftStatus
from osah.domain.entities.import_batch_summary import ImportBatchSummary
from osah.ui.qt.components.scrollable_table_frame import ScrollableTableFrame
from osah.ui.qt.design.tokens import COLOR, SIZE, SPACING
from osah.ui.qt.screens.settings.format_employee_import_draft_status_label import (
    format_employee_import_draft_status_label,
)


class EmployeeImportReviewDialog(QDialog):
    """Modal review step for employee import before applying valid rows."""

    def __init__(
        self,
        batch_summary: ImportBatchSummary,
        employee_import_drafts: tuple[EmployeeImportDraft, ...],
        parent=None,
    ) -> None:
        super().__init__(parent)
        self._batch_summary = batch_summary
        self._employee_import_drafts = employee_import_drafts

        self.setWindowTitle("Перевірка імпорту працівників")
        self.setModal(True)
        self.resize(1180, 720)
        self.setMinimumSize(SIZE["window_min_w"], 640)
        self.setStyleSheet(
            f"""
            QDialog {{
                background:
                    qlineargradient(x1:0, y1:0, x2:1, y2:1,
                        stop:0 rgba(255, 255, 255, 248),
                        stop:1 rgba(232, 240, 248, 234));
                color: {COLOR['text_primary']};
            }}
            QLabel {{
                font-size: 14px;
            }}
            QLabel[role="section_title"] {{
                font-size: 24px;
                font-weight: 800;
            }}
            QTableWidget {{
                background: rgba(255, 255, 255, 0.9);
                border: 1px solid {COLOR['border_soft']};
                border-radius: 18px;
                gridline-color: #E2EAF2;
                font-size: 14px;
            }}
            QHeaderView::section {{
                background: #EAF1F7;
                color: #17365D;
                padding: 11px 8px;
                border: none;
                font-size: 13px;
                font-weight: 800;
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
        layout.setContentsMargins(SPACING["xl"], SPACING["lg"], SPACING["xl"], SPACING["lg"])
        layout.setSpacing(SPACING["md"])

        title = QLabel("Перевірка імпорту працівників")
        title.setProperty("role", "section_title")
        layout.addWidget(title)

        subtitle = QLabel(self._build_subtitle_text())
        subtitle.setProperty("role", "section_header_subtitle")
        subtitle.setWordWrap(True)
        layout.addWidget(subtitle)

        summary = QLabel(self._build_summary_text())
        summary.setWordWrap(True)
        layout.addWidget(summary)

        self._table = QTableWidget(0, 8)
        self._table.setAlternatingRowColors(True)
        self._table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self._table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self._table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self._table.verticalHeader().setVisible(False)
        self._table.setHorizontalHeaderLabels(
            [
                "Рядок",
                "Таб. №",
                "ПІБ",
                "Посада",
                "Підрозділ",
                "Статус",
                "Результат",
                "Пояснення",
            ]
        )
        header = self._table.horizontalHeader()
        header.setStretchLastSection(False)
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(7, QHeaderView.ResizeMode.Stretch)
        self._fill_table()
        layout.addWidget(ScrollableTableFrame(self._table), stretch=1)

        footer = QHBoxLayout()
        footer.addStretch()

        close_button = QPushButton("Скасувати")
        close_button.setProperty("variant", "secondary")
        close_button.clicked.connect(self.reject)
        footer.addWidget(close_button)

        apply_button = QPushButton("Застосувати імпорт")
        apply_button.setProperty("variant", "accent")
        apply_button.setEnabled(self._batch_summary.valid_total > 0 and not self._batch_summary.applied_at)
        apply_button.clicked.connect(self.accept)
        footer.addWidget(apply_button)

        layout.addLayout(footer)

    def _build_subtitle_text(self) -> str:
        if self._batch_summary.applied_at:
            return "Цю партію вже застосовано. Нижче показано, що було імпортовано."
        if self._batch_summary.valid_total <= 0:
            return "У файлі немає валідних рядків для імпорту. Виправте помилки та завантажте файл знову."
        return "Перевірте, що саме буде створено або оновлено, і підтвердьте імпорт."

    def _build_summary_text(self) -> str:
        new_total = self._count_drafts(EmployeeImportDraftStatus.NEW)
        update_total = self._count_drafts(EmployeeImportDraftStatus.UPDATE)
        unchanged_total = self._count_drafts(EmployeeImportDraftStatus.UNCHANGED)
        invalid_total = self._count_drafts(EmployeeImportDraftStatus.INVALID)
        return (
            f"Файл: {self._batch_summary.source_name} | "
            f"Усього рядків: {self._batch_summary.draft_total} | "
            f"Нових: {new_total} | "
            f"Оновлень: {update_total} | "
            f"Без змін: {unchanged_total} | "
            f"З помилками: {invalid_total}"
        )

    def _count_drafts(self, status: EmployeeImportDraftStatus) -> int:
        return sum(1 for draft in self._employee_import_drafts if draft.resolution_status == status)

    def _fill_table(self) -> None:
        self._table.setRowCount(len(self._employee_import_drafts))
        for row_index, draft in enumerate(self._employee_import_drafts):
            values = (
                str(draft.source_row_number),
                draft.personnel_number,
                draft.full_name,
                draft.position_name,
                draft.department_name,
                draft.employment_status,
                format_employee_import_draft_status_label(draft.resolution_status),
                draft.issue_text,
            )
            for column_index, value in enumerate(values):
                item = QTableWidgetItem(value)
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                if column_index == 6:
                    self._apply_status_color(item, draft.resolution_status)
                self._table.setItem(row_index, column_index, item)
            self._table.setRowHeight(row_index, 44)
        if self._employee_import_drafts:
            self._table.selectRow(0)

    def _apply_status_color(self, item: QTableWidgetItem, status: EmployeeImportDraftStatus) -> None:
        if status == EmployeeImportDraftStatus.NEW:
            item.setForeground(QColor(COLOR["success"]))
            return
        if status == EmployeeImportDraftStatus.UPDATE:
            item.setForeground(QColor(COLOR["accent"]))
            return
        if status == EmployeeImportDraftStatus.UNCHANGED:
            item.setForeground(QColor(COLOR["text_muted"]))
            return
        item.setForeground(QColor(COLOR["critical"]))
