"""
Дизайн-токены для Qt UI-шара OSaH 2.0.
Єдине джерело правди для кольорів, відступів, радіусів і типографіки.
Design tokens for OSaH 2.0 Qt UI layer - single source of truth.
"""

# ------------------------------------------------------------------
# КОЛЬОРИ / COLORS
# ------------------------------------------------------------------
COLOR: dict[str, str] = {
    # Базовые поверхности / Base surfaces
    "bg_app": "#ECEFF3",
    "bg_workspace": "#F7F8FA",
    "bg_panel": "#E1E6EC",
    "bg_card": "#FFFFFF",
    "bg_elevated": "#FFFFFF",

    # Текст / Text
    "text_primary": "#111827",
    "text_secondary": "#4B5563",
    "text_muted": "#6B7280",
    "text_on_accent": "#FFFFFF",

    # Границы / Borders
    "border_default": "#B8C2CF",
    "border_soft": "#D3D9E2",
    "border_focus": "#3A5F8A",
    "divider": "#D3D9E2",

    # Главный акцент / Accent
    "accent": "#3A5F8A",
    "accent_hover": "#2F4D70",
    "accent_active": "#263F5C",
    "accent_soft": "#DCE6F1",

    # Кнопки / Buttons
    "button_primary_bg": "#3A5F8A",
    "button_primary_hover": "#2F4D70",
    "button_primary_active": "#263F5C",
    "button_primary_text": "#FFFFFF",
    "button_primary_border": "#3A5F8A",
    "button_secondary_bg": "#FFFFFF",
    "button_secondary_hover": "#E1E6EC",
    "button_secondary_active": "#D7DDE5",
    "button_secondary_text": "#111827",
    "button_secondary_border": "#B8C2CF",
    "button_ghost_bg": "transparent",
    "button_ghost_hover": "#E1E6EC",
    "button_ghost_text": "#111827",
    "button_ghost_border": "transparent",
    "button_disabled_bg": "#E5EAF0",
    "button_disabled_text": "#8C97A5",
    "button_disabled_border": "#D3D9E2",

    # Поля ввода / Inputs
    "input_bg": "#FFFFFF",
    "input_text": "#111827",
    "input_placeholder": "#6B7280",
    "input_border": "#B8C2CF",
    "input_border_hover": "#8FA0B5",
    "input_border_focus": "#3A5F8A",
    "input_disabled_bg": "#EEF2F6",
    "input_disabled_text": "#8C97A5",
    "input_disabled_border": "#D3D9E2",

    # Статусы / Status palette
    "status_critical": "#B51010",
    "status_warning": "#FCAD0F",
    "status_ok": "#07B551",
    "status_info": "#0669C4",
    "status_archive": "#8B95A5",
    "status_critical_bg": "#FBE7E7",
    "status_warning_bg": "#FFF1D6",
    "status_ok_bg": "#DDF7E8",
    "status_info_bg": "#DCEBFA",
    "status_archive_bg": "#EEF1F4",
    "status_critical_text": "#8E0D0D",
    "status_warning_text": "#9A6700",
    "status_ok_text": "#057A39",
    "status_info_text": "#05539B",
    "status_archive_text": "#667085",

    # Специальные UI состояния / Special UI states
    "selection_bg": "#DCE6F1",
    "hover_bg": "#E9EEF4",
    "active_row": "#DCE6F1",
    "readonly_bg": "#F2F4F7",
    "readonly_text": "#667085",
    "error_bg": "#FBE7E7",
    "warning_bg": "#FFF1D6",
    "success_bg": "#DDF7E8",
    "info_bg": "#DCEBFA",

    # Навигация / Navigation
    "nav_bg": "#E1E6EC",
    "nav_item_text": "#111827",
    "nav_item_hover_bg": "#D7DEE7",
    "nav_item_active_bg": "#3A5F8A",
    "nav_item_active_text": "#FFFFFF",
    "nav_item_problem_border": "#B51010",
    "nav_item_problem_badge_bg": "#B51010",
    "nav_item_problem_badge_text": "#FFFFFF",

    # Карточки / Cards
    "card_bg": "#FFFFFF",
    "card_border": "#B8C2CF",
    "card_border_soft": "#D3D9E2",
    "card_hover_bg": "#F8FAFC",
    "card_selected_bg": "#DCE6F1",
    "mini_card_bg": "#FFFFFF",
    "mini_card_hover_bg": "#EEF2F6",
    "mini_card_border": "#D3D9E2",
    "metric_card_bg": "#FFFFFF",
    "metric_card_border": "#B8C2CF",
    "metric_card_value": "#111827",
    "metric_card_label": "#4B5563",

    # Таблицы / Tables
    "table_bg": "#FFFFFF",
    "table_header_bg": "#E1E6EC",
    "table_header_text": "#111827",
    "table_row_bg": "#FFFFFF",
    "table_row_alt_bg": "#F8FAFC",
    "table_row_hover_bg": "#E9EEF4",
    "table_row_selected_bg": "#DCE6F1",
    "table_border": "#D3D9E2",
    "table_text": "#111827",
    "table_text_secondary": "#4B5563",

    # Ограничено / Restricted status (for employee & medical flow)
    "restricted": "#0669C4",
    "restricted_subtle": "#DCEBFA",
    "restricted_text": "#05539B",

    # Совместимость со старыми ключами / Backward compatibility
    "bg_shell": "#F7F8FA",
    "bg_panel_elevated": "#FFFFFF",
    "bg_card_hover": "#F8FAFC",
    "accent_pressed": "#263F5C",
    "accent_text": "#FFFFFF",
    "accent_subtle": "#DCE6F1",
    "accent_subtle_text": "#3A5F8A",
    "success": "#07B551",
    "success_subtle": "#DDF7E8",
    "warning": "#FCAD0F",
    "warning_subtle": "#FFF1D6",
    "warning_hover": "#FFF1D6",
    "critical": "#B51010",
    "critical_subtle": "#FBE7E7",
    "critical_hover": "#FBE7E7",
    "border_strong": "#8FA0B5",
    "nav_hover": "#D7DEE7",
    "nav_active_bg": "#3A5F8A",
    "nav_active_text": "#FFFFFF",
    "nav_footer": "#667085",
    "role_card_bg": "#EEF1F4",
    "role_tag_bg": "#DCE6F1",
    "role_tag_text": "#3A5F8A",
    "metric_title": "#4B5563",
    "news_accent": "#0669C4",
}

# ------------------------------------------------------------------
# ТІНІ / SHADOWS
# ------------------------------------------------------------------
SHADOW: dict[str, dict] = {
    "card_sm": {"radius": 8, "offset_y": 1, "alpha": 12},
    "card_md": {"radius": 16, "offset_y": 2, "alpha": 18},
    "card_lg": {"radius": 24, "offset_y": 4, "alpha": 24},
}

# ------------------------------------------------------------------
# АНІМАЦІЇ / ANIMATIONS (ms)
# ------------------------------------------------------------------
ANIMATION: dict[str, int] = {
    "fast": 150,     # hover, active
    "normal": 300,   # fade-in
    "slow": 500,     # screens, heavy transitions
}

# ------------------------------------------------------------------
# ВІДСТУПИ / SPACING (px)
# ------------------------------------------------------------------
SPACING: dict[str, int] = {
    "xs": 4,
    "sm": 8,
    "md": 12,
    "lg": 16,
    "xl": 24,
    "xxl": 32,
}

# ------------------------------------------------------------------
# РАДІУСИ / BORDER RADIUS (px)
# ------------------------------------------------------------------
RADIUS: dict[str, int] = {
    "sm": 8,
    "md": 12,
    "lg": 16,
    "xl": 20,
    "xxl": 24,
}

# ------------------------------------------------------------------
# ГЕОМЕТРІЯ / GEOMETRY (px)
# ------------------------------------------------------------------
SIZE: dict[str, int] = {
    "btn_height_sm": 36,
    "btn_height_md": 44,
    "nav_width": 240,
    "top_bar_height": 60,
    "status_bar_height": 32,
    "icon_sm": 16,
    "icon_md": 20,
    "card_min_width": 160,
    "card_min_height": 100,
    "window_min_w": 1100,
    "window_min_h": 720,
}

# ------------------------------------------------------------------
# ТИПОГРАФІКА / TYPOGRAPHY
# Формат: (family, size, bold)
# ------------------------------------------------------------------
FONT: dict[str, tuple] = {
    "title_xl": ("Segoe UI", 22, True),
    "title_l": ("Segoe UI", 16, True),
    "title_m": ("Segoe UI", 13, True),
    "body": ("Segoe UI", 11, False),
    "caption": ("Segoe UI", 9, False),
    "metric": ("Segoe UI", 28, True),
    "label": ("Segoe UI", 10, True),
    "nav_item": ("Segoe UI", 12, True),
}
