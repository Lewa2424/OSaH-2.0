from pathlib import Path

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from osah.application.services.create_port_site_passport import create_port_site_passport
from osah.application.services.load_port_calibration_for_passport import load_port_calibration_for_passport
from osah.application.services.save_port_calibration_for_passport import save_port_calibration_for_passport
from osah.application.services.update_port_site_passport import update_port_site_passport
from osah.domain.entities.access_role import AccessRole
from osah.domain.entities.port_compensating_barrier_item import PortCompensatingBarrierItem
from osah.domain.entities.port_macrovariable_threshold import PortMacrovariableThreshold
from osah.domain.entities.port_passport_calibration import PortPassportCalibration
from osah.domain.entities.port_site_passport_input import PortSitePassportInput
from osah.ui.qt.components.form_feedback_label import FormFeedbackLabel
from osah.ui.qt.design.tokens import COLOR, SPACING
from osah.ui.qt.screens.port_r.port_calibration_panel import PortBarriersPanel, PortThresholdsPanel
from osah.ui.qt.screens.port_r.port_calibration_simulator_dialog import PortCalibrationSimulatorDialog


class CreatePortSitePassportDialog(QDialog):
    """Діалог створення паспорта виробничої ділянки ПОРТ-Р.
    Dialog for creating a PORT-R production site passport.
    """

    passport_created = Signal(int)
    passport_saved = Signal(int)

    def __init__(
        self,
        database_path: Path,
        access_role: AccessRole,
        parent=None,
        *,
        passport_id: int | None = None,
        initial_input: PortSitePassportInput | None = None,
        initial_tab_index: int = 0,
    ) -> None:
        super().__init__(parent)
        self._database_path = database_path
        self._access_role = access_role
        self._passport_id = passport_id
        self._initial_input = initial_input
        self.setWindowTitle("Редагування паспорта ділянки" if passport_id is not None else "Створення паспорта ділянки")
        self.setModal(True)
        self.resize(760, 760)
        self.setStyleSheet(f"QDialog {{ background: {COLOR['bg_card']}; }}")

        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(SPACING["lg"], SPACING["lg"], SPACING["lg"], SPACING["lg"])
        root_layout.setSpacing(SPACING["md"])

        self._tabs = QTabWidget()

        # ── Вкладка 1: Загальні відомості ──
        general_tab = QWidget()
        general_tab_layout = QVBoxLayout(general_tab)
        general_tab_layout.setContentsMargins(0, SPACING["sm"], 0, 0)
        general_tab_layout.setSpacing(0)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QScrollArea.Shape.NoFrame)
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(SPACING["md"])

        self._build_identification_section(content_layout)
        self._build_work_section(content_layout)
        self._build_cargo_section(content_layout)
        self._build_equipment_section(content_layout)
        self._build_people_section(content_layout)
        self._build_conditions_section(content_layout)
        self._build_barriers_section(content_layout)
        content_layout.addStretch()

        scroll_area.setWidget(content)
        general_tab_layout.addWidget(scroll_area)
        self._tabs.addTab(general_tab, "Загальні відомості")

        # ── Вкладка 2: Пороги Т-П-С-В-Б ──
        thresholds_scroll = QScrollArea()
        thresholds_scroll.setWidgetResizable(True)
        thresholds_scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        self._thresholds_panel = PortThresholdsPanel()
        thresholds_scroll.setWidget(self._thresholds_panel)

        if passport_id is None:
            self._thresholds_panel.setEnabled(False)
            self._thresholds_panel.setToolTip("Доступне після збереження паспорта")

        self._tabs.addTab(thresholds_scroll, "Пороги Т-П-С-В-Б")

        # ── Вкладка 3: Компенсуючі бар'єри ──
        barriers_scroll = QScrollArea()
        barriers_scroll.setWidgetResizable(True)
        barriers_scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        self._barriers_panel = PortBarriersPanel()
        barriers_scroll.setWidget(self._barriers_panel)

        if passport_id is None:
            self._barriers_panel.setEnabled(False)
            self._barriers_panel.setToolTip("Доступне після збереження паспорта")

        self._tabs.addTab(barriers_scroll, "Компенсуючі бар'єри")

        root_layout.addWidget(self._tabs, stretch=1)

        if 0 <= initial_tab_index < self._tabs.count():
            self._tabs.setCurrentIndex(initial_tab_index)

        if passport_id is not None:
            self._load_calibration(passport_id)

        self._feedback_label = FormFeedbackLabel()
        root_layout.addWidget(self._feedback_label)

        buttons_layout = QHBoxLayout()
        self._clear_button = QPushButton("Очистити")
        self._clear_button.setProperty("variant", "secondary")
        self._clear_button.clicked.connect(self._clear_form)
        buttons_layout.addWidget(self._clear_button)

        self._simulator_button = QPushButton("Симулятор калібрування")
        self._simulator_button.setProperty("variant", "secondary")
        self._simulator_button.setEnabled(passport_id is not None)
        if passport_id is None:
            self._simulator_button.setToolTip("Доступне після збереження паспорта")
        self._simulator_button.clicked.connect(self._open_simulator)
        buttons_layout.addWidget(self._simulator_button)

        buttons_layout.addStretch()

        self._cancel_button = QPushButton("Скасувати")
        self._cancel_button.setProperty("variant", "secondary")
        self._cancel_button.clicked.connect(self.reject)
        buttons_layout.addWidget(self._cancel_button)

        self._save_button = QPushButton("Зберегти")
        self._save_button.setProperty("variant", "accent")
        self._save_button.clicked.connect(self._save)
        buttons_layout.addWidget(self._save_button)
        root_layout.addLayout(buttons_layout)
        if self._initial_input is not None:
            self._fill_form(self._initial_input)

    def _open_simulator(self) -> None:
        if self._passport_id is None:
            return
        passport_label = self._passport_code_input.text().strip() or self._site_name_input.text().strip()
        dialog = PortCalibrationSimulatorDialog(
            self._database_path,
            self._passport_id,
            passport_label,
            self,
        )
        dialog.exec()

    def _build_identification_section(self, parent_layout: QVBoxLayout) -> None:
        form = QFormLayout()
        form.setSpacing(SPACING["sm"])

        self._passport_code_input = QLineEdit()
        self._passport_code_input.setPlaceholderText("Напр.: PORT-R-2026-001")
        form.addRow("Код / номер паспорта", self._passport_code_input)

        self._site_name_input = QLineEdit()
        self._site_name_input.setPlaceholderText("Назва виробничої ділянки")
        form.addRow("Назва ділянки", self._site_name_input)

        self._site_type_input = QComboBox()
        self._site_type_input.setEditable(True)
        self._site_type_input.addItems(["", "Причал", "Склад", "Залізничний фронт", "Автофронт", "Кранова зона"])
        form.addRow("Тип ділянки", self._site_type_input)

        self._site_location_input = QLineEdit()
        self._site_location_input.setPlaceholderText("Місцезнаходження")
        form.addRow("Місцезнаходження", self._site_location_input)

        self._site_description_input = _make_text_edit("Короткий опис меж, призначення та особливостей ділянки")
        form.addRow("Опис ділянки", self._site_description_input)

        parent_layout.addWidget(_wrap_group("1. Ідентифікація", form))

    def _build_work_section(self, parent_layout: QVBoxLayout) -> None:
        form = QFormLayout()
        form.setSpacing(SPACING["sm"])

        self._work_kind_input = QComboBox()
        self._work_kind_input.setEditable(True)
        self._work_kind_input.addItems(["", "Вантажно-розвантажувальні роботи", "Складування", "Транспортування"])
        form.addRow("Вид робіт", self._work_kind_input)

        self._typical_operations_input = _make_text_edit("Типові операції на ділянці")
        form.addRow("Типові операції", self._typical_operations_input)

        self._work_mode_input = QComboBox()
        self._work_mode_input.addItem("", "")
        self._work_mode_input.addItem("День", "day")
        self._work_mode_input.addItem("Ніч", "night")
        self._work_mode_input.addItem("Цілодобово", "round_the_clock")
        self._work_mode_input.addItem("Змінний", "shift")
        form.addRow("Режим роботи", self._work_mode_input)

        parent_layout.addWidget(_wrap_group("2. Роботи", form))

    def _build_cargo_section(self, parent_layout: QVBoxLayout) -> None:
        form = QFormLayout()
        form.setSpacing(SPACING["sm"])

        self._typical_cargo_input = QComboBox()
        self._typical_cargo_input.setEditable(True)
        self._typical_cargo_input.addItems(["", "Металопродукція", "Контейнери", "Навалочні вантажі", "Небезпечні вантажі"])
        form.addRow("Типові вантажі", self._typical_cargo_input)

        self._cargo_features_input = _make_text_edit("Особливості вантажу, пакування, стійкості або маркування")
        form.addRow("Особливості вантажу", self._cargo_features_input)

        parent_layout.addWidget(_wrap_group("3. Вантажі", form))

    def _build_equipment_section(self, parent_layout: QVBoxLayout) -> None:
        form = QFormLayout()
        form.setSpacing(SPACING["sm"])

        self._main_equipment_input = _make_text_edit("Основна техніка на ділянці")
        form.addRow("Основна техніка", self._main_equipment_input)

        self._lifting_devices_input = _make_text_edit("Стропи, траверси, захвати, спредери тощо")
        form.addRow("ВЗП", self._lifting_devices_input)

        zone_row = QHBoxLayout()
        self._has_railway_zone_input = QCheckBox("Залізнична зона")
        self._has_auto_zone_input = QCheckBox("Автозона")
        self._has_crane_zone_input = QCheckBox("Кранова зона")
        zone_row.addWidget(self._has_railway_zone_input)
        zone_row.addWidget(self._has_auto_zone_input)
        zone_row.addWidget(self._has_crane_zone_input)
        zone_row.addStretch()
        form.addRow("Зони", _wrap_layout(zone_row))

        parent_layout.addWidget(_wrap_group("4. Техніка", form))

    def _build_people_section(self, parent_layout: QVBoxLayout) -> None:
        form = QFormLayout()
        form.setSpacing(SPACING["sm"])

        self._crew_composition_input = QLineEdit()
        form.addRow("Склад бригади", self._crew_composition_input)

        self._responsible_person_input = QLineEdit()
        form.addRow("Відповідальний", self._responsible_person_input)

        self._has_contractors_input = QCheckBox("Є підрядники / сторонні особи")
        form.addRow("Підрядники", self._has_contractors_input)

        self._contractors_note_input = QLineEdit()
        self._contractors_note_input.setPlaceholderText("Коментар щодо підрядників або сторонніх осіб")
        form.addRow("Коментар", self._contractors_note_input)

        parent_layout.addWidget(_wrap_group("5. Люди", form))

    def _build_conditions_section(self, parent_layout: QVBoxLayout) -> None:
        form = QFormLayout()
        form.setSpacing(SPACING["sm"])

        self._zone_kind_input = QComboBox()
        self._zone_kind_input.setEditable(True)
        self._zone_kind_input.addItems(["", "Відкрита зона", "Закрита зона", "Комбінована зона"])
        form.addRow("Відкрита / закрита зона", self._zone_kind_input)

        condition_row = QHBoxLayout()
        self._has_night_works_input = QCheckBox("Нічні роботи")
        self._has_limited_visibility_input = QCheckBox("Обмежена видимість")
        self._has_height_work_input = QCheckBox("Робота на висоті")
        condition_row.addWidget(self._has_night_works_input)
        condition_row.addWidget(self._has_limited_visibility_input)
        condition_row.addWidget(self._has_height_work_input)
        condition_row.addStretch()
        form.addRow("Фактори", _wrap_layout(condition_row))

        edge_row = QHBoxLayout()
        self._has_water_edge_work_input = QCheckBox("Біля води")
        self._has_stack_edge_work_input = QCheckBox("Біля краю штабеля")
        edge_row.addWidget(self._has_water_edge_work_input)
        edge_row.addWidget(self._has_stack_edge_work_input)
        edge_row.addStretch()
        form.addRow("Крайові зони", _wrap_layout(edge_row))

        self._weather_features_input = QLineEdit()
        self._weather_features_input.setPlaceholderText("Вітер, опади, ожеледь, туман тощо")
        form.addRow("Погодні особливості", self._weather_features_input)

        parent_layout.addWidget(_wrap_group("6. Умови", form))

    def _build_barriers_section(self, parent_layout: QVBoxLayout) -> None:
        form = QFormLayout()
        form.setSpacing(SPACING["sm"])

        self._has_communication_barrier_input = QCheckBox("Зв'язок наявний")
        self._communication_barrier_input = QLineEdit()
        self._communication_barrier_input.setPlaceholderText("Рації, канали зв'язку, резерв")
        form.addRow("Зв'язок", _with_checkbox(self._has_communication_barrier_input, self._communication_barrier_input))

        self._has_fencing_barrier_input = QCheckBox("Огородження наявні")
        self._fencing_barrier_input = QLineEdit()
        self._fencing_barrier_input.setPlaceholderText("Тип огороджень або зонування")
        form.addRow("Огородження", _with_checkbox(self._has_fencing_barrier_input, self._fencing_barrier_input))

        self._has_signalman_input = QCheckBox("Сигнальник наявний")
        form.addRow("Сигнальник", self._has_signalman_input)

        self._has_lighting_barrier_input = QCheckBox("Освітлення наявне")
        self._lighting_barrier_input = QLineEdit()
        self._lighting_barrier_input.setPlaceholderText("Стаціонарне / мобільне освітлення")
        form.addRow("Освітлення", _with_checkbox(self._has_lighting_barrier_input, self._lighting_barrier_input))

        self._ppe_text_input = QLineEdit()
        self._ppe_text_input.setPlaceholderText("ЗІЗ для ділянки")
        form.addRow("ЗІЗ", self._ppe_text_input)

        self._additional_barriers_input = _make_text_edit("Додаткові бар'єри та заходи контролю")
        form.addRow("Додаткові бар'єри", self._additional_barriers_input)

        parent_layout.addWidget(_wrap_group("7. Бар'єри", form))

    def _clear_form(self) -> None:
        for line_edit in self.findChildren(QLineEdit):
            line_edit.clear()
        for text_edit in self.findChildren(QTextEdit):
            text_edit.clear()
        for checkbox in self.findChildren(QCheckBox):
            checkbox.setChecked(False)
        for combo_box in self.findChildren(QComboBox):
            combo_box.setCurrentIndex(0)
            if combo_box.isEditable():
                combo_box.setEditText("")
        self._feedback_label.setVisible(False)

    def _load_calibration(self, passport_id: int) -> None:
        try:
            calibration = load_port_calibration_for_passport(self._database_path, passport_id)
            self._thresholds_panel.load_thresholds(calibration.thresholds)
            self._barriers_panel.load_barriers(calibration.compensating_barriers)
        except Exception:
            pass

    def _save(self) -> None:
        try:
            if self._passport_id is None:
                passport_id = create_port_site_passport(
                    self._database_path,
                    self._build_passport_input(),
                    access_role=self._access_role,
                )
                self.passport_created.emit(passport_id)
            else:
                update_port_site_passport(
                    self._database_path,
                    self._passport_id,
                    self._build_passport_input(),
                    access_role=self._access_role,
                )
                passport_id = self._passport_id
                self._save_calibration(passport_id)
                self.passport_saved.emit(passport_id)
        except ValueError as error:
            self._feedback_label.show_error(str(error))
            return

        self.accept()

    def _save_calibration(self, passport_id: int) -> None:
        threshold_data = self._thresholds_panel.collect_thresholds()
        barrier_data = self._barriers_panel.collect_barriers()

        thresholds = tuple(
            PortMacrovariableThreshold(
                threshold_id=0,
                passport_id=passport_id,
                macrovariable=mv,
                trigger_text=text,
                k_value=k,
                is_stop_trigger=is_stop,
            )
            for mv, text, k, is_stop in threshold_data
        )
        barriers = tuple(
            PortCompensatingBarrierItem(
                barrier_id=0,
                passport_id=passport_id,
                barrier_name=name,
                description=desc,
                k_comp=k_comp,
                macrovariable=mv,
            )
            for mv, name, desc, k_comp in barrier_data
        )
        calibration = PortPassportCalibration(
            passport_id=passport_id,
            r_base=1.0,
            thresholds=thresholds,
            compensating_barriers=barriers,
        )
        try:
            save_port_calibration_for_passport(
                self._database_path,
                calibration,
                actor_name="inspector",
                access_role=self._access_role,
            )
        except Exception:
            pass

    def _build_passport_input(self) -> PortSitePassportInput:
        return PortSitePassportInput(
            passport_code=self._passport_code_input.text(),
            site_name=self._site_name_input.text(),
            site_type=self._site_type_input.currentText(),
            site_location=self._site_location_input.text(),
            site_description=self._site_description_input.toPlainText(),
            work_kind=self._work_kind_input.currentText(),
            typical_operations=self._typical_operations_input.toPlainText(),
            work_mode=str(self._work_mode_input.currentData() or ""),
            typical_cargo=self._typical_cargo_input.currentText(),
            cargo_features=self._cargo_features_input.toPlainText(),
            main_equipment=self._main_equipment_input.toPlainText(),
            lifting_devices=self._lifting_devices_input.toPlainText(),
            has_railway_zone=self._has_railway_zone_input.isChecked(),
            has_auto_zone=self._has_auto_zone_input.isChecked(),
            has_crane_zone=self._has_crane_zone_input.isChecked(),
            crew_composition=self._crew_composition_input.text(),
            responsible_person=self._responsible_person_input.text(),
            has_contractors=self._has_contractors_input.isChecked(),
            contractors_note=self._contractors_note_input.text(),
            zone_kind=self._zone_kind_input.currentText(),
            has_night_works=self._has_night_works_input.isChecked(),
            weather_features=self._weather_features_input.text(),
            has_limited_visibility=self._has_limited_visibility_input.isChecked(),
            has_height_work=self._has_height_work_input.isChecked(),
            has_water_edge_work=self._has_water_edge_work_input.isChecked(),
            has_stack_edge_work=self._has_stack_edge_work_input.isChecked(),
            has_communication_barrier=self._has_communication_barrier_input.isChecked(),
            communication_barrier=self._communication_barrier_input.text(),
            has_fencing_barrier=self._has_fencing_barrier_input.isChecked(),
            fencing_barrier=self._fencing_barrier_input.text(),
            has_signalman=self._has_signalman_input.isChecked(),
            has_lighting_barrier=self._has_lighting_barrier_input.isChecked(),
            lighting_barrier=self._lighting_barrier_input.text(),
            ppe_text=self._ppe_text_input.text(),
            additional_barriers=self._additional_barriers_input.toPlainText(),
        )

    def _fill_form(self, value: PortSitePassportInput) -> None:
        self._passport_code_input.setText(value.passport_code)
        self._site_name_input.setText(value.site_name)
        _set_combo_text(self._site_type_input, value.site_type)
        self._site_location_input.setText(value.site_location)
        self._site_description_input.setPlainText(value.site_description)
        _set_combo_text(self._work_kind_input, value.work_kind)
        self._typical_operations_input.setPlainText(value.typical_operations)
        _set_combo_data(self._work_mode_input, value.work_mode)
        _set_combo_text(self._typical_cargo_input, value.typical_cargo)
        self._cargo_features_input.setPlainText(value.cargo_features)
        self._main_equipment_input.setPlainText(value.main_equipment)
        self._lifting_devices_input.setPlainText(value.lifting_devices)
        self._has_railway_zone_input.setChecked(value.has_railway_zone)
        self._has_auto_zone_input.setChecked(value.has_auto_zone)
        self._has_crane_zone_input.setChecked(value.has_crane_zone)
        self._crew_composition_input.setText(value.crew_composition)
        self._responsible_person_input.setText(value.responsible_person)
        self._has_contractors_input.setChecked(value.has_contractors)
        self._contractors_note_input.setText(value.contractors_note)
        _set_combo_text(self._zone_kind_input, value.zone_kind)
        self._has_night_works_input.setChecked(value.has_night_works)
        self._weather_features_input.setText(value.weather_features)
        self._has_limited_visibility_input.setChecked(value.has_limited_visibility)
        self._has_height_work_input.setChecked(value.has_height_work)
        self._has_water_edge_work_input.setChecked(value.has_water_edge_work)
        self._has_stack_edge_work_input.setChecked(value.has_stack_edge_work)
        self._has_communication_barrier_input.setChecked(value.has_communication_barrier)
        self._communication_barrier_input.setText(value.communication_barrier)
        self._has_fencing_barrier_input.setChecked(value.has_fencing_barrier)
        self._fencing_barrier_input.setText(value.fencing_barrier)
        self._has_signalman_input.setChecked(value.has_signalman)
        self._has_lighting_barrier_input.setChecked(value.has_lighting_barrier)
        self._lighting_barrier_input.setText(value.lighting_barrier)
        self._ppe_text_input.setText(value.ppe_text)
        self._additional_barriers_input.setPlainText(value.additional_barriers)


def _make_text_edit(placeholder_text: str) -> QTextEdit:
    text_edit = QTextEdit()
    text_edit.setPlaceholderText(placeholder_text)
    text_edit.setMaximumHeight(76)
    return text_edit


def _wrap_group(title_text: str, form: QFormLayout) -> QGroupBox:
    group = QGroupBox(title_text)
    layout = QVBoxLayout(group)
    layout.setContentsMargins(SPACING["md"], SPACING["sm"], SPACING["md"], SPACING["md"])
    layout.addLayout(form)
    return group


def _wrap_layout(layout: QHBoxLayout) -> QWidget:
    widget = QWidget()
    widget.setLayout(layout)
    return widget


def _with_checkbox(checkbox: QCheckBox, line_edit: QLineEdit) -> QWidget:
    row = QHBoxLayout()
    row.setContentsMargins(0, 0, 0, 0)
    row.addWidget(checkbox)
    row.addWidget(line_edit, stretch=1)
    return _wrap_layout(row)


def _set_combo_text(combo_box: QComboBox, value: str) -> None:
    index = combo_box.findText(value)
    if index >= 0:
        combo_box.setCurrentIndex(index)
    elif combo_box.isEditable():
        combo_box.setEditText(value)


def _set_combo_data(combo_box: QComboBox, value: str) -> None:
    for index in range(combo_box.count()):
        if str(combo_box.itemData(index) or "") == value:
            combo_box.setCurrentIndex(index)
            return
    combo_box.setCurrentIndex(0)
