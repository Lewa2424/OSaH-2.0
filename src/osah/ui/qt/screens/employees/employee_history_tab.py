from pathlib import Path

from PySide6.QtWidgets import QLabel, QFrame, QVBoxLayout, QWidget

from osah.application.services.load_employee_audit_history import load_employee_audit_history
from osah.domain.entities.employee_workspace_row import EmployeeWorkspaceRow
from osah.ui.qt.components.scrollable_table_frame import ScrollableTableFrame
from osah.ui.qt.design.tokens import COLOR, RADIUS, SPACING
from osah.ui.qt.screens.employees.employee_history_detail_panel import EmployeeHistoryDetailPanel
from osah.ui.qt.screens.employees.employee_history_table import EmployeeHistoryTable


class EmployeeHistoryTab(QWidget):
    """Audit history tab inside an employee card. / Вкладка історії змін у картці працівника."""

    def __init__(self, database_path: Path, employee_row: EmployeeWorkspaceRow) -> None:
        super().__init__()
        self.setStyleSheet(
            f"""
            QLabel#historyTitle {{
                color: {COLOR['text_primary']};
                font-size: 21px;
                font-weight: 900;
            }}
            QLabel#historySubtitle {{
                color: {COLOR['text_secondary']};
                font-size: 14px;
                font-weight: 600;
            }}
            QFrame#historyHero {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #F7FAFD, stop:1 #EEF5FB);
                border: 1px solid #D9E2EC;
                border-radius: {RADIUS['xl']}px;
            }}
            """
        )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(SPACING["lg"], SPACING["lg"], SPACING["lg"], SPACING["lg"])
        layout.setSpacing(SPACING["lg"])

        layout.addWidget(self._build_header())

        audit_entries = load_employee_audit_history(database_path, employee_row)
        if not audit_entries:
            empty_label = QLabel("Зафіксованих подій ще немає.")
            empty_label.setWordWrap(True)
            empty_label.setStyleSheet(f"color: {COLOR['text_muted']}; font-size: 15px; font-weight: 700;")
            layout.addWidget(empty_label)
            layout.addStretch()
            return

        self._history_table = EmployeeHistoryTable()
        self._history_table.set_entries(audit_entries)
        self._history_table.setStyleSheet(
            f"""
            QTableWidget {{
                background: #FFFFFF;
                border: 1px solid #D9E2EC;
                border-radius: {RADIUS['xl']}px;
                gridline-color: #E5ECF2;
                font-size: 13px;
                color: {COLOR['text_primary']};
            }}
            QHeaderView::section {{
                background: #EEF3F8;
                color: {COLOR['text_secondary']};
                border: none;
                border-bottom: 1px solid #D9E2EC;
                padding: 10px 12px;
                font-size: 12px;
                font-weight: 900;
            }}
            QTableWidget::item {{
                padding: 8px;
            }}
            QTableWidget::item:selected {{
                background: #EAF1F8;
                color: {COLOR['text_primary']};
            }}
            """
        )
        table_frame = ScrollableTableFrame(self._history_table)
        table_frame.setMaximumHeight(290)
        layout.addWidget(table_frame, stretch=1)

        self._detail_panel = EmployeeHistoryDetailPanel()
        self._history_table.entry_selected.connect(self._sync_detail_panel)
        layout.addWidget(self._detail_panel, stretch=0)
        self._sync_detail_panel(-1)

    def _build_header(self) -> QWidget:
        hero = QFrame()
        hero.setObjectName("historyHero")
        layout = QVBoxLayout(hero)
        layout.setContentsMargins(SPACING["lg"], SPACING["md"], SPACING["lg"], SPACING["md"])
        layout.setSpacing(SPACING["xs"])

        title = QLabel("Історія змін")
        title.setObjectName("historyTitle")
        layout.addWidget(title)

        subtitle = QLabel("Журнал аудиту показує, коли і в якому модулі змінювався стан працівника.")
        subtitle.setObjectName("historySubtitle")
        subtitle.setWordWrap(True)
        layout.addWidget(subtitle)
        return hero

    def _sync_detail_panel(self, _entry_id: int) -> None:
        """Updates the detail panel from the selected table row. / Оновлює панель деталей за вибраним рядком."""

        current_entry = self._history_table.current_entry()
        if current_entry is None:
            self._detail_panel.show_placeholder()
            return
        self._detail_panel.set_entry(current_entry)
