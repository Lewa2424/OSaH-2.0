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
    background: {c["bg_panel"]};
    width: 8px;
    border-radius: 4px;
    margin: 4px 2px 4px 2px;
}}
QScrollBar::handle:vertical {{
    background: {c["border_strong"]};
    border-radius: 4px;
    min-height: 30px;
}}
QScrollBar::handle:vertical:hover {{
    background: {c["text_muted"]};
}}
QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical {{
    height: 0px;
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
    border: 1px solid {c["border_soft"]};
}}

/* ── QFrame-інсет (вставлений блок) / Inset frame ── */
QFrame[inset="true"] {{
    background: {c["bg_panel"]};
    border-radius: {r["md"]}px;
    border: 1px solid {c["border_soft"]};
}}

/* ── Кнопка акценту / Accent button ── */
QPushButton[variant="accent"] {{
    background: {c["accent"]};
    color: {c["accent_text"]};
    border: none;
    border-radius: {r["md"]}px;
    padding: 8px 20px;
    font-size: 12px;
    font-weight: bold;
}}
QPushButton[variant="accent"]:hover {{
    background: {c["accent_hover"]};
}}
QPushButton[variant="accent"]:pressed {{
    background: {c["accent_pressed"]};
}}
QPushButton[variant="accent"]:disabled {{
    background: {c["border_strong"]};
    color: {c["text_muted"]};
}}

/* ── Вторинна кнопка / Secondary button ── */
QPushButton[variant="secondary"] {{
    background: {c["bg_card"]};
    color: {c["text_primary"]};
    border: 1px solid {c["border_soft"]};
    border-radius: {r["md"]}px;
    padding: 8px 20px;
    font-size: 12px;
}}
QPushButton[variant="secondary"]:hover {{
    background: {c["bg_panel"]};
    border-color: {c["border_strong"]};
}}
QPushButton[variant="secondary"]:pressed {{
    background: {c["border_soft"]};
}}

/* ── NavButton (idle) ── */
QPushButton[nav="true"] {{
    background: transparent;
    color: {c["text_primary"]};
    border: 1px solid {c["border_soft"]};
    border-radius: {r["md"]}px;
    padding: 8px 12px;
    text-align: left;
    font-size: 12px;
    font-weight: bold;
}}
QPushButton[nav="true"]:hover {{
    background: {c["nav_hover"]};
    border-color: {c["border_strong"]};
}}
QPushButton[nav="true"]:pressed {{
    background: {c["border_soft"]};
}}
QPushButton[nav="true"]:checked {{
    background: {c["nav_active_bg"]};
    color: {c["nav_active_text"]};
    border-color: {c["nav_active_bg"]};
}}

/* NavButton — Warning (рівень уваги) */
QPushButton[nav="true"][alert="warning"] {{
    background: {c["warning_subtle"]};
    border: 1px solid {c["warning"]};
    color: {c["text_primary"]};
}}
QPushButton[nav="true"][alert="warning"]:hover {{
    background: {c["warning_hover"]};
}}

/* NavButton — Critical (критичний рівень) */
QPushButton[nav="true"][alert="critical"] {{
    background: {c["critical_subtle"]};
    border: 2px solid {c["critical"]};
    color: {c["text_primary"]};
}}
QPushButton[nav="true"][alert="critical"]:hover {{
    background: {c["critical_hover"]};
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
    background: {c["critical"]};
    color: #FFFFFF;
    border-radius: 9px;
    padding: 2px 10px;
    font-size: 9px;
    font-weight: bold;
}}
QLabel[pill="warning"] {{
    background: {c["warning"]};
    color: #FFFFFF;
    border-radius: 9px;
    padding: 2px 10px;
    font-size: 9px;
    font-weight: bold;
}}
QLabel[pill="info"] {{
    background: {c["accent"]};
    color: #FFFFFF;
    border-radius: 9px;
    padding: 2px 10px;
    font-size: 9px;
    font-weight: bold;
}}
QLabel[pill="success"] {{
    background: {c["success"]};
    color: #FFFFFF;
    border-radius: 9px;
    padding: 2px 10px;
    font-size: 9px;
    font-weight: bold;
}}

/* ── TopCommandBar фон / TopCommandBar bg ── */
QWidget[role="topbar"] {{
    background: {c["bg_shell"]};
    border-bottom: 1px solid {c["border_soft"]};
}}

/* ── SideNav фон / SideNav bg ── */
QWidget[role="sidenav"] {{
    background: {c["nav_bg"]};
    border-right: 1px solid {c["border_soft"]};
}}

/* ── StatusStrip фон / StatusStrip bg ── */
QWidget[role="statusbar"] {{
    background: {c["bg_panel"]};
    border-top: 1px solid {c["border_soft"]};
}}

/* ── ScrollArea viewport ── */
QScrollArea {{
    background: transparent;
    border: none;
}}
QScrollArea > QWidget > QWidget {{
    background: {c["bg_app"]};
}}
"""
