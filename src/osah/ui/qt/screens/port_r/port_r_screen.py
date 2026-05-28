from pathlib import Path

from PySide6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QMessageBox,
    QPushButton,
    QSplitter,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)
from PySide6.QtCore import Qt

from osah.application.services.accept_port_site_risk import accept_port_site_risk
from osah.application.services.add_manual_port_site_risk import add_manual_port_site_risk
from osah.application.services.add_port_risk_suggestion_to_passport import add_port_risk_suggestion_to_passport
from osah.application.services.archive_port_site_passport import archive_port_site_passport
from osah.application.services.approve_port_passport import approve_port_passport
from osah.application.services.calculate_port_passport_profile import calculate_port_passport_profile
from osah.application.services.export_port_shift_briefing_to_docx import export_port_shift_briefing_to_docx
from osah.application.services.load_port_risk_suggestions_for_passport import load_port_risk_suggestions_for_passport
from osah.application.services.load_port_site_passport_for_edit import load_port_site_passport_for_edit
from osah.application.services.load_port_site_passport_rows import load_port_site_passport_rows
from osah.application.services.load_port_site_risks_for_passport import load_port_site_risks_for_passport
from osah.application.services.log_port_shift_briefing_copy import log_port_shift_briefing_copy
from osah.application.services.reject_port_site_risk import reject_port_site_risk
from osah.infrastructure.config.application_paths import build_application_paths
from osah.domain.entities.access_role import AccessRole
from osah.domain.entities.port_passport_status import PortPassportStatus
from osah.domain.entities.port_risk_profile import format_port_risk_profile
from osah.domain.entities.port_risk_suggestion import PortRiskSuggestion
from osah.domain.entities.port_site_passport_row import PortSitePassportRow
from osah.domain.entities.port_site_risk import PortSiteRisk
from osah.ui.qt.components.form_feedback_label import FormFeedbackLabel
from osah.ui.qt.components.read_only_banner import ReadOnlyBanner
from osah.ui.qt.components.scrollable_table_frame import ScrollableTableFrame
from osah.ui.qt.components.screen_states import EmptyStateWidget
from osah.ui.qt.components.section_container import SectionContainer
from osah.ui.qt.components.section_header import SectionHeader
from osah.ui.qt.components.show_styled_message_box import show_styled_message_box
from osah.ui.qt.design.tokens import SPACING
from osah.ui.qt.screens.port_r.accept_risk_dialog import AcceptRiskDialog
from osah.ui.qt.screens.port_r.add_manual_risk_dialog import AddManualRiskDialog
from osah.ui.qt.screens.port_r.create_port_site_passport_dialog import CreatePortSitePassportDialog
from osah.ui.qt.screens.port_r.port_risk_suggestions_table import PortRiskSuggestionsTable
from osah.ui.qt.screens.port_r.port_site_passports_table import PortSitePassportsTable
from osah.ui.qt.screens.port_r.port_site_risks_table import PortSiteRisksTable
from osah.ui.qt.screens.port_r.shift_briefing_preview_dialog import ShiftBriefingPreviewDialog


class PortRScreen(QWidget):
    """Стартовий екран розділу ПОРТ-Р зі списком паспортів ділянок.
    PORT-R start screen with a site passport list.
    """

    def __init__(self, database_path: Path, access_role: AccessRole) -> None:
        super().__init__()
        self._database_path = database_path
        self._access_role = access_role
        self._include_archived = False
        self._rows = load_port_site_passport_rows(database_path, include_archived=self._include_archived)
        self._table: PortSitePassportsTable | None = None
        self._selected_passport_row: PortSitePassportRow | None = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(SPACING["xl"], SPACING["lg"], SPACING["xl"], SPACING["lg"])
        layout.setSpacing(SPACING["lg"])

        layout.addWidget(
            SectionHeader(
                "ПОРТ-Р",
                "Паспортизація виробничих ділянок, оцінювання ризиків і контроль статусу паспорта.",
            )
        )

        if not self._can_edit():
            layout.addWidget(ReadOnlyBanner("Режим тільки перегляду: зміни недоступні."))
        self._feedback = FormFeedbackLabel()
        layout.addWidget(self._feedback)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setChildrenCollapsible(False)

        # ── Ліва панель: список паспортів ──
        passports_container = SectionContainer()
        self._content_layout = passports_container.content_layout()
        self._content_layout.setContentsMargins(0, 0, 2, 0)
        splitter.addWidget(passports_container)

        # ── Права панель: вкладки ──
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(2, 0, 0, 0)
        right_layout.setSpacing(SPACING["sm"])

        self._tabs = QTabWidget()

        # Вкладка «Ризики паспорта»
        risks_tab = QWidget()
        risks_tab_layout = QVBoxLayout(risks_tab)
        risks_tab_layout.setContentsMargins(0, SPACING["sm"], 0, 0)
        risks_tab_layout.setSpacing(SPACING["sm"])

        self._risks_table = PortSiteRisksTable()
        self._risks_table.row_selected.connect(self._on_risk_selected)
        risks_tab_layout.addWidget(ScrollableTableFrame(self._risks_table, snap_to_columns=True))

        risk_actions = QWidget()
        risk_actions_layout = self._build_risk_action_buttons(risk_actions)
        risks_tab_layout.addWidget(risk_actions)

        passport_actions = QWidget()
        self._build_passport_action_buttons(passport_actions)
        risks_tab_layout.addWidget(passport_actions)

        self._tabs.addTab(risks_tab, "Ризики паспорта")

        # Вкладка «Рекомендовані»
        suggestions_tab = QWidget()
        suggestions_tab_layout = QVBoxLayout(suggestions_tab)
        suggestions_tab_layout.setContentsMargins(0, SPACING["sm"], 0, 0)
        suggestions_tab_layout.setSpacing(0)
        self._suggestions_table = PortRiskSuggestionsTable()
        self._suggestions_table.add_requested.connect(self._add_suggestion_to_passport)
        suggestions_tab_layout.addWidget(ScrollableTableFrame(self._suggestions_table, snap_to_columns=True))
        self._tabs.addTab(suggestions_tab, "Рекомендовані")

        right_layout.addWidget(self._tabs)
        splitter.addWidget(right_widget)
        splitter.setStretchFactor(0, 2)
        splitter.setStretchFactor(1, 3)
        splitter.setSizes([520, 780])

        layout.addWidget(splitter, stretch=1)
        self._render_passport_list()

    # ──────────────────────────────────────────────────────────────────────
    # Побудова кнопок / Button builders
    # ──────────────────────────────────────────────────────────────────────

    def _build_risk_action_buttons(self, parent: QWidget) -> QHBoxLayout:
        layout = QHBoxLayout(parent)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(SPACING["sm"])

        self._accept_btn = QPushButton("Прийняти ризик")
        self._accept_btn.setProperty("variant", "accent")
        self._accept_btn.setEnabled(False)
        self._accept_btn.clicked.connect(self._on_accept_risk)
        layout.addWidget(self._accept_btn)

        self._reject_btn = QPushButton("Відхилити")
        self._reject_btn.setProperty("variant", "secondary")
        self._reject_btn.setEnabled(False)
        self._reject_btn.clicked.connect(self._on_reject_risk)
        layout.addWidget(self._reject_btn)

        self._manual_btn = QPushButton("+ Додати вручну")
        self._manual_btn.setProperty("variant", "secondary")
        self._manual_btn.setEnabled(False)
        self._manual_btn.clicked.connect(self._on_add_manual_risk)
        layout.addWidget(self._manual_btn)

        layout.addStretch()
        return layout

    def _build_passport_action_buttons(self, parent: QWidget) -> None:
        layout = QHBoxLayout(parent)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(SPACING["sm"])

        self._calculate_btn = QPushButton("Розрахувати профіль")
        self._calculate_btn.setProperty("variant", "accent")
        self._calculate_btn.setEnabled(False)
        self._calculate_btn.clicked.connect(self._on_calculate_profile)
        layout.addWidget(self._calculate_btn)

        self._approve_btn = QPushButton("Затвердити паспорт")
        self._approve_btn.setProperty("variant", "accent")
        self._approve_btn.setEnabled(False)
        self._approve_btn.clicked.connect(self._on_approve_passport)
        layout.addWidget(self._approve_btn)

        self._export_briefing_btn = QPushButton("Оперативний лист зміни (.docx)")
        self._export_briefing_btn.setProperty("variant", "accent")
        self._export_briefing_btn.setEnabled(False)
        self._export_briefing_btn.clicked.connect(self._on_export_shift_briefing)
        layout.addWidget(self._export_briefing_btn)

        layout.addStretch()

    # ──────────────────────────────────────────────────────────────────────
    # Права/доступ
    # ──────────────────────────────────────────────────────────────────────

    def _can_edit(self) -> bool:
        return self._access_role == AccessRole.INSPECTOR

    # ──────────────────────────────────────────────────────────────────────
    # Паспорти / Passports
    # ──────────────────────────────────────────────────────────────────────

    def _open_create_passport_dialog(self) -> None:
        dialog = CreatePortSitePassportDialog(self._database_path, self._access_role, self)
        dialog.passport_created.connect(lambda _: self._reload_passports())
        dialog.exec()

    def _reload_passports(self) -> None:
        self._rows = load_port_site_passport_rows(
            self._database_path,
            include_archived=self._include_archived,
        )
        self._render_passport_list()
        if self._selected_passport_row is not None:
            self._reload_right_panel(self._selected_passport_row.passport_id)

    def _render_passport_list(self) -> None:
        _clear_layout(self._content_layout)
        self._table = None

        controls = QWidget()
        controls_layout = QHBoxLayout(controls)
        controls_layout.setContentsMargins(0, 0, 0, 0)
        controls_layout.setSpacing(SPACING["sm"])

        if self._can_edit():
            create_btn = QPushButton("+ Створити паспорт ділянки")
            create_btn.setProperty("variant", "accent")
            create_btn.clicked.connect(self._open_create_passport_dialog)
            controls_layout.addWidget(create_btn)

        self._archive_filter = QComboBox()
        self._archive_filter.addItem("Активні паспорти", False)
        self._archive_filter.addItem("Усі паспорти", True)
        self._archive_filter.setCurrentIndex(1 if self._include_archived else 0)
        self._archive_filter.currentIndexChanged.connect(self._on_archive_filter_changed)
        controls_layout.addStretch()
        controls_layout.addWidget(self._archive_filter)
        self._content_layout.addWidget(controls)

        if self._rows:
            self._table = PortSitePassportsTable()
            self._table.set_rows(self._rows)
            self._table.row_selected.connect(self._on_passport_selected)
            self._table.edit_requested.connect(self._on_passport_edit_requested)
            self._table.archive_requested.connect(self._on_passport_archive_requested)
            self._content_layout.addWidget(ScrollableTableFrame(self._table, snap_to_columns=True))
            self._table.select_first()
            return

        empty_state = EmptyStateWidget()
        empty_state.show_state(
            "Паспорти ділянок ще не створені.",
            "Створіть перший паспорт, щоб почати формувати профіль ризику ділянки.",
        )
        self._content_layout.addWidget(empty_state)
        self._content_layout.addStretch()
        self._selected_passport_row = None
        self._risks_table.set_rows(())
        self._suggestions_table.set_rows(())
        self._update_button_states(passport_selected=False, risk_selected=False)

    def _on_passport_selected(self, row: PortSitePassportRow) -> None:
        self._selected_passport_row = row
        self._reload_right_panel(row.passport_id)

    def _on_passport_edit_requested(self, row: PortSitePassportRow) -> None:
        if row.status == PortPassportStatus.ARCHIVED:
            self._feedback.show_error("Архівний паспорт не можна редагувати.")
            return
        self._selected_passport_row = row
        self._reload_right_panel(row.passport_id)
        try:
            initial_input = load_port_site_passport_for_edit(self._database_path, row.passport_id)
        except Exception as error:  # noqa: BLE001
            self._feedback.show_error(f"Не вдалося завантажити паспорт: {error}")
            return
        dialog = CreatePortSitePassportDialog(
            self._database_path,
            self._access_role,
            self,
            passport_id=row.passport_id,
            initial_input=initial_input,
        )
        dialog.passport_saved.connect(lambda _: self._reload_passports())
        dialog.exec()

    def _on_passport_archive_requested(self, row: PortSitePassportRow) -> None:
        if not self._can_edit():
            self._feedback.show_error("Режим read-only: архівація недоступна.")
            return
        if row.status == PortPassportStatus.ARCHIVED:
            self._feedback.show_error("Паспорт уже в архіві.")
            return
        answer = show_styled_message_box(
            self,
            "Підтвердження архівації",
            "Отправить в архив?",
            QMessageBox.Icon.Question,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if answer != QMessageBox.StandardButton.Yes:
            return
        try:
            archive_port_site_passport(
                self._database_path,
                row.passport_id,
                access_role=self._access_role,
            )
        except Exception as error:  # noqa: BLE001
            self._feedback.show_error(f"Не вдалося архівувати паспорт: {error}")
            return
        self._feedback.show_success("Паспорт відправлено в архів.")
        self._selected_passport_row = None
        self._reload_passports()

    def _on_archive_filter_changed(self, *_: object) -> None:
        if not hasattr(self, "_archive_filter"):
            return
        self._include_archived = bool(self._archive_filter.currentData())
        self._selected_passport_row = None
        self._reload_passports()

    def _reload_right_panel(self, passport_id: int) -> None:
        risks = load_port_site_risks_for_passport(self._database_path, passport_id)
        self._risks_table.set_rows(risks)
        suggestions = load_port_risk_suggestions_for_passport(self._database_path, passport_id)
        self._suggestions_table.set_rows(suggestions)
        self._update_button_states(passport_selected=True, risk_selected=False)

    # ──────────────────────────────────────────────────────────────────────
    # Ризики / Risks
    # ──────────────────────────────────────────────────────────────────────

    def _on_risk_selected(self, risk: PortSiteRisk) -> None:
        self._update_button_states(passport_selected=True, risk_selected=True)

    def _update_button_states(self, *, passport_selected: bool, risk_selected: bool) -> None:
        selected_is_mutable = (
            self._selected_passport_row is not None
            and self._selected_passport_row.status != PortPassportStatus.ARCHIVED
        )
        can = self._can_edit() and selected_is_mutable
        self._accept_btn.setEnabled(can and risk_selected)
        self._reject_btn.setEnabled(can and risk_selected)
        self._manual_btn.setEnabled(can and passport_selected)
        self._calculate_btn.setEnabled(can and passport_selected)
        self._approve_btn.setEnabled(can and passport_selected)
        self._export_briefing_btn.setEnabled(can and passport_selected)

    def _on_accept_risk(self) -> None:
        risk = self._risks_table.current_risk()
        if risk is None or self._selected_passport_row is None:
            return
        dialog = AcceptRiskDialog(risk.risk_situation, self)
        if dialog.exec() != AcceptRiskDialog.DialogCode.Accepted:
            return
        try:
            accept_port_site_risk(
                self._database_path,
                risk.risk_id,
                dialog.selected_level(),
                assessment_reason=dialog.assessment_reason(),
                inspector_comment=dialog.inspector_comment(),
                access_role=self._access_role,
            )
        except Exception as error:  # noqa: BLE001
            self._feedback.show_error(f"Помилка прийняття: {error}")
            return
        self._feedback.show_success("Ризик прийнято.")
        self._reload_right_panel(self._selected_passport_row.passport_id)

    def _on_reject_risk(self) -> None:
        risk = self._risks_table.current_risk()
        if risk is None or self._selected_passport_row is None:
            return
        try:
            reject_port_site_risk(
                self._database_path,
                risk.risk_id,
                access_role=self._access_role,
            )
        except Exception as error:  # noqa: BLE001
            self._feedback.show_error(f"Помилка відхилення: {error}")
            return
        self._feedback.show_success("Ризик відхилено.")
        self._reload_right_panel(self._selected_passport_row.passport_id)

    def _on_add_manual_risk(self) -> None:
        if self._selected_passport_row is None:
            return
        dialog = AddManualRiskDialog(self)
        if dialog.exec() != AddManualRiskDialog.DialogCode.Accepted:
            return
        try:
            add_manual_port_site_risk(
                self._database_path,
                self._selected_passport_row.passport_id,
                risk_situation=dialog.risk_situation(),
                hazard_source=dialog.hazard_source(),
                occurrence_conditions=dialog.occurrence_conditions(),
                consequences=dialog.consequences(),
                access_role=self._access_role,
            )
        except Exception as error:  # noqa: BLE001
            self._feedback.show_error(f"Помилка додавання: {error}")
            return
        self._feedback.show_success("Ризик додано вручну.")
        self._reload_right_panel(self._selected_passport_row.passport_id)

    # ──────────────────────────────────────────────────────────────────────
    # Suggestions
    # ──────────────────────────────────────────────────────────────────────

    def _add_suggestion_to_passport(self, suggestion: PortRiskSuggestion) -> None:
        if not self._can_edit():
            self._feedback.show_error("Режим read-only: додавання ризиків недоступне.")
            return
        if self._selected_passport_row is None:
            self._feedback.show_error("Спочатку оберіть паспорт зі списку.")
            return
        if self._selected_passport_row.status == PortPassportStatus.ARCHIVED:
            self._feedback.show_error("Архівний паспорт не можна змінювати.")
            return
        try:
            add_port_risk_suggestion_to_passport(
                self._database_path,
                self._selected_passport_row.passport_id,
                suggestion.registry_risk_id,
                suggestion_reason=suggestion.suggestion_reason,
                access_role=self._access_role,
            )
        except Exception as error:  # noqa: BLE001
            self._feedback.show_error(f"Не вдалося додати ризик: {error}")
            return
        self._feedback.show_success("Рекомендований ризик додано до паспорта.")
        self._reload_right_panel(self._selected_passport_row.passport_id)

    # ──────────────────────────────────────────────────────────────────────
    # Профіль і затвердження / Profile & Approve
    # ──────────────────────────────────────────────────────────────────────

    def _on_calculate_profile(self) -> None:
        if self._selected_passport_row is None:
            return
        try:
            profile = calculate_port_passport_profile(
                self._database_path,
                self._selected_passport_row.passport_id,
                actor_name="inspector",
                access_role=self._access_role,
            )
        except Exception as error:  # noqa: BLE001
            self._feedback.show_error(f"Помилка розрахунку: {error}")
            return
        self._feedback.show_success(f"Профіль розраховано: {format_port_risk_profile(profile)}.")
        self._reload_passports()

    def _on_approve_passport(self) -> None:
        if self._selected_passport_row is None:
            return
        try:
            approve_port_passport(
                self._database_path,
                self._selected_passport_row.passport_id,
                actor_name="inspector",
                access_role=self._access_role,
            )
        except ValueError as error:
            self._feedback.show_error(str(error))
            return
        except Exception as error:  # noqa: BLE001
            self._feedback.show_error(f"Помилка затвердження: {error}")
            return
        self._feedback.show_success("Паспорт затверджено.")
        self._reload_passports()

    # ──────────────────────────────────────────────────────────────────────
    # Експорт оперативного листа / Shift briefing export
    # ──────────────────────────────────────────────────────────────────────

    def _on_export_shift_briefing(self) -> None:
        if self._selected_passport_row is None:
            return
        if self._selected_passport_row.status == PortPassportStatus.ARCHIVED:
            self._feedback.show_error("Архівний паспорт не можна експортувати.")
            return
        project_root = build_application_paths().project_root
        try:
            export_result = export_port_shift_briefing_to_docx(
                self._database_path,
                project_root,
                self._selected_passport_row.passport_id,
                actor_name="inspector",
                access_role=self._access_role,
            )
        except Exception as error:  # noqa: BLE001
            self._feedback.show_error(f"Помилка експорту: {error}")
            return

        self._feedback.show_success("Оперативний лист зміни сформовано.")
        passport_id = self._selected_passport_row.passport_id
        passport_code = self._selected_passport_row.passport_code
        dialog = ShiftBriefingPreviewDialog(
            export_result.file_path,
            passport_code,
            export_result.key_risks_count,
            self,
        )
        dialog.copy_requested.connect(
            lambda source, destination, pid=passport_id: self._on_briefing_copied(pid, source, destination)
        )
        dialog.exec()

    def _on_briefing_copied(self, passport_id: int, source_path: Path, destination_path: Path) -> None:
        try:
            log_port_shift_briefing_copy(
                self._database_path,
                passport_id,
                source_path,
                destination_path,
                actor_name="inspector",
                access_role=self._access_role,
            )
        except Exception as error:  # noqa: BLE001
            self._feedback.show_error(f"Не вдалося зафіксувати копіювання: {error}")
            return
        self._feedback.show_success(f"Копію збережено: {destination_path}")


def _clear_layout(layout: QVBoxLayout) -> None:
    while layout.count():
        item = layout.takeAt(0)
        widget = item.widget()
        if widget is not None:
            widget.deleteLater()
