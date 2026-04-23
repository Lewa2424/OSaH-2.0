"""
QSS-стилізація для Qt UI-шару OSaH 2.0.
Генерується з дизайн-токенів. Застосовується через QApplication.setStyleSheet().
QSS styling for OSaH 2.0 Qt UI — generated from design tokens.
"""
from osah.ui.qt.design.tokens import COLOR, RADIUS


def build_global_stylesheet() -> str:
    """Повертає глобальний QSS-рядок для застосунку.
    Returns the global QSS string for the application.
    """
    c = COLOR
    r = RADIUS

    return f"""
/* ── Загальна скидання / Global reset ── */
* {{
    font-family: "Segoe UI";
    font-size: 11px;
    color: {c["text_primary"]};
    outline: none;
}}

/* ── Головне вікно / Main window ── */
QMainWindow {{
    background: {c["bg_app"]};
}}

QWidget {{
    background: transparent;
}}

/* ── Скролбари / Scrollbars ── */
QScrollBar:vertical {{
    background: transparent;
    width: 6px;
    margin: 0px 0px 0px 0px;
}}
QScrollBar::handle:vertical {{
    background: {c["border_strong"]};
    border-radius: 3px;
    min-height: 30px;
}}
QScrollBar::handle:vertical:hover {{
    background: {c["text_muted"]};
}}
QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical {{
    height: 0px;
}}
QScrollBar::add-page:vertical,
QScrollBar::sub-page:vertical {{
    background: transparent;
}}
QScrollBar:horizontal {{
    background: {c["bg_panel"]};
    height: 8px;
    border-radius: 4px;
    margin: 2px 4px 2px 4px;
}}
QScrollBar::handle:horizontal {{
    background: {c["border_strong"]};
    border-radius: 4px;
    min-width: 30px;
}}
QScrollBar::handle:horizontal:hover {{
    background: {c["text_muted"]};
}}
QScrollBar::add-line:horizontal,
QScrollBar::sub-line:horizontal {{
    width: 0px;
}}

/* ── QLabel базовий / Base QLabel ── */
QLabel {{
    background: transparent;
    color: {c["text_primary"]};
}}

/* ── QFrame-картка / Card frame ── */
QFrame[card="true"] {{
    background: {c["bg_card"]};
    border-radius: {r["xl"]}px;
    border: 1px solid {c["card_border"]};
}}

/* ── QFrame-інсет (вставлений блок) / Inset frame ── */
QFrame[inset="true"] {{
    background: {c["bg_panel"]};
    border-radius: {r["md"]}px;
    border: 1px solid {c["border_soft"]};
}}

/* ── Кнопка акценту / Accent button ── */
QPushButton[variant="accent"] {{
    background: {c["button_primary_bg"]};
    color: {c["button_primary_text"]};
    border: 1px solid {c["button_primary_border"]};
    border-radius: {r["md"]}px;
    padding: 8px 20px;
    font-size: 12px;
    font-weight: bold;
}}
QPushButton[variant="accent"]:hover {{
    background: {c["button_primary_hover"]};
}}
QPushButton[variant="accent"]:pressed {{
    background: {c["button_primary_active"]};
}}
QPushButton[variant="accent"]:disabled {{
    background: {c["button_disabled_bg"]};
    color: {c["button_disabled_text"]};
    border-color: {c["button_disabled_border"]};
}}

/* ── Вторинна кнопка / Secondary button ── */
QPushButton[variant="secondary"] {{
    background: {c["button_secondary_bg"]};
    color: {c["button_secondary_text"]};
    border: 1px solid {c["button_secondary_border"]};
    border-radius: {r["md"]}px;
    padding: 8px 20px;
    font-size: 12px;
}}
QPushButton[variant="secondary"]:hover {{
    background: {c["button_secondary_hover"]};
    border-color: {c["input_border_hover"]};
}}
QPushButton[variant="secondary"]:pressed {{
    background: {c["button_secondary_active"]};
}}

/* ── NavButton (idle) ── */
QPushButton[nav="true"] {{
    background: transparent;
    color: {c["nav_item_text"]};
    border: 1px solid {c["border_default"]};
    border-radius: {r["md"]}px;
    padding: 8px 12px;
    text-align: left;
    font-size: 12px;
    font-weight: bold;
}}
QPushButton[nav="true"]:hover {{
    background: {c["nav_item_hover_bg"]};
    border-color: {c["input_border_hover"]};
}}
QPushButton[nav="true"]:pressed {{
    background: {c["button_secondary_active"]};
}}
QPushButton[nav="true"]:checked {{
    background: {c["nav_item_active_bg"]};
    color: {c["nav_item_active_text"]};
    border-color: {c["nav_item_active_bg"]};
}}

/* NavButton — Warning (рівень уваги) */
QPushButton[nav="true"][alert="warning"] {{
    background: {c["status_warning_bg"]};
    border: 1px solid {c["status_warning"]};
    color: {c["text_primary"]};
}}
QPushButton[nav="true"][alert="warning"]:hover {{
    background: {c["warning_bg"]};
}}

/* NavButton — Critical (критичний рівень) */
QPushButton[nav="true"][alert="critical"] {{
    background: {c["status_critical_bg"]};
    border: 2px solid {c["nav_item_problem_border"]};
    color: {c["text_primary"]};
}}
QPushButton[nav="true"][alert="critical"]:hover {{
    background: {c["error_bg"]};
}}

/* ── QSplitter ── */
QSplitter::handle {{
    background: {c["border_soft"]};
}}
QSplitter::handle:horizontal {{
    width: 1px;
}}
QSplitter::handle:vertical {{
    height: 1px;
}}

/* ── Pill badge / Badge-label ── */
QLabel[pill="true"] {{
    border-radius: 9px;
    padding: 2px 10px;
    font-size: 9px;
    font-weight: bold;
}}
QLabel[pill="critical"] {{
    background: {c["status_critical"]};
    color: {c["text_on_accent"]};
    border-radius: 9px;
    padding: 2px 10px;
    font-size: 9px;
    font-weight: bold;
}}
QLabel[pill="warning"] {{
    background: {c["status_warning"]};
    color: {c["text_on_accent"]};
    border-radius: 9px;
    padding: 2px 10px;
    font-size: 9px;
    font-weight: bold;
}}
QLabel[pill="info"] {{
    background: {c["status_info"]};
    color: {c["text_on_accent"]};
    border-radius: 9px;
    padding: 2px 10px;
    font-size: 9px;
    font-weight: bold;
}}
QLabel[pill="success"] {{
    background: {c["status_ok"]};
    color: {c["text_on_accent"]};
    border-radius: 9px;
    padding: 2px 10px;
    font-size: 9px;
    font-weight: bold;
}}

/* ── TopCommandBar фон / TopCommandBar bg ── */
QWidget[role="topbar"] {{
    background: {c["bg_panel"]};
    border-bottom: 1px solid {c["divider"]};
}}

/* ── SideNav фон / SideNav bg ── */
QWidget[role="sidenav"] {{
    background: {c["nav_bg"]};
    border-right: 1px solid {c["divider"]};
}}

/* ── StatusStrip фон / StatusStrip bg ── */
QWidget[role="statusbar"] {{
    background: {c["bg_panel"]};
    border-top: 1px solid {c["divider"]};
}}

/* ── General Elements ── */
QLabel[role="section_title"] {{
    color: {c["text_primary"]};
    font-size: 16px;
    font-weight: bold;
}}
QLabel[role="section_header_title"] {{
    color: {c["text_primary"]};
    font-size: 22px;
    font-weight: 900;
}}
QLabel[role="section_header_subtitle"] {{
    color: {c["text_secondary"]};
    font-size: 11px;
    font-weight: 500;
}}
QLabel[role="state_title"] {{
    color: {c["text_secondary"]};
    font-size: 12px;
    font-weight: 800;
}}
QLabel[role="state_subtitle"] {{
    color: {c["text_muted"]};
    font-size: 10px;
}}
QLabel[role="state_loading"] {{
    color: {c["accent"]};
    font-size: 11px;
    font-weight: 700;
}}
QLabel[role="state_error"] {{
    color: {c["status_critical_text"]};
    background: {c["error_bg"]};
    border: 1px solid {c["status_critical"]};
    border-radius: 10px;
    padding: 8px 10px;
    font-weight: 700;
}}
QLabel[role="readonly_banner"] {{
    color: {c["readonly_text"]};
    background: {c["readonly_bg"]};
    border: 1px dashed {c["border_default"]};
    border-radius: {r["md"]}px;
    padding: 8px 10px;
    font-weight: 700;
}}
QWidget[role="section_bg"] {{
    background: {c["bg_workspace"]};
}}

/* Employees module */
QLineEdit,
QComboBox {{
    background: {c["input_bg"]};
    color: {c["input_text"]};
    border: 1px solid {c["input_border"]};
    border-radius: {r["md"]}px;
    padding: 8px 10px;
    min-height: 24px;
}}
QLineEdit:focus,
QComboBox:focus {{
    border: 1px solid {c["input_border_focus"]};
}}
QCheckBox {{
    spacing: 6px;
    color: {c["text_secondary"]};
    font-weight: 600;
}}
QTreeWidget,
QTableWidget {{
    background: {c["table_bg"]};
    alternate-background-color: {c["table_row_alt_bg"]};
    border: 1px solid {c["table_border"]};
    border-radius: {r["lg"]}px;
    gridline-color: {c["table_border"]};
    selection-background-color: {c["table_row_selected_bg"]};
    selection-color: {c["table_text"]};
}}
QHeaderView::section {{
    background: {c["table_header_bg"]};
    border: none;
    border-bottom: 1px solid {c["table_border"]};
    color: {c["table_header_text"]};
    font-weight: 800;
    padding: 8px;
}}
QTreeWidget::item,
QTableWidget::item {{
    padding: 6px;
}}
QTreeWidget::item:hover,
QTableWidget::item:hover {{
    background: {c["table_row_hover_bg"]};
}}
QTreeWidget::item:selected,
QTableWidget::item:selected {{
    background: {c["table_row_selected_bg"]};
    color: {c["table_text"]};
}}
QTabWidget::pane {{
    border: 1px solid {c["border_default"]};
    border-radius: {r["lg"]}px;
    background: {c["bg_card"]};
}}
QTabBar::tab {{
    background: {c["bg_panel"]};
    border: 1px solid {c["border_default"]};
    border-bottom: none;
    border-top-left-radius: {r["md"]}px;
    border-top-right-radius: {r["md"]}px;
    padding: 8px 12px;
    margin-right: 4px;
}}
QTabBar::tab:selected {{
    background: {c["bg_card"]};
    color: {c["accent"]};
    font-weight: 800;
}}

/* ── SideNav / Logo ── */
QLabel[role="logo"] {{
    color: {c["accent"]};
}}

/* ── TopCommandBar / StatusStrip ── */
QLabel[role="title"] {{
    color: {c["text_primary"]};
}}
QLabel[role="subtitle"] {{
    color: {c["text_muted"]};
    font-size: 11px;
}}
QLabel[role="status_muted"] {{
    color: {c["text_muted"]};
    font-size: 9px;
}}
QLabel[role="status_success"] {{
    color: {c["success"]};
    font-size: 9px;
}}

/* ── Dashboard / MetricCard ── */
QLabel[role="metric_title"] {{
    color: {c["metric_title"]};
    font-size: 10px;
    font-weight: bold;
}}
QLabel[role="metric_value"] {{
    color: {c["text_primary"]};
}}
QLabel[role="metric_subtitle"] {{
    color: {c["text_secondary"]};
    font-size: 9px;
}}

/* ── AlertCard ── */
QLabel[role="alert_title"] {{
    color: {c["text_primary"]};
    font-size: 13px;
    font-weight: bold;
}}
QLabel[role="alert_body"] {{
    color: {c["text_secondary"]};
    font-size: 10px;
}}
QLabel[role="empty_state"] {{
    color: {c["status_ok_text"]};
    padding: 16px;
}}

/* ── ScrollArea viewport ── */
QScrollArea {{
    background: transparent;
    border: none;
}}
QScrollArea > QWidget > QWidget {{
    background: {c["bg_workspace"]};
}}
"""
