"""
Дизайн-токени для Qt UI-шару OSaH 2.0.
Єдине джерело правди для кольорів, відступів, радіусів і типографіки.
Design tokens for OSaH 2.0 Qt UI layer — single source of truth.
"""

# ──────────────────────────────────────────────────────────────────
# КОЛЬОРИ / COLORS
# ──────────────────────────────────────────────────────────────────
COLOR: dict[str, str] = {
    # Фони / Backgrounds
    "bg_app":              "#F0F2F5",   # Корінь вікна / root window
    "bg_shell":            "#DBF0F3EA",   # Основні панелі / main panels
    "bg_panel":            "#F8F9FB",   # Трохи піднята поверхня / slightly elevated panel
    "bg_panel_elevated":   "#FFFFFF",   # Піднята панель або велика картка / elevated panel or large card
    "bg_card":             "#FFFFFF",   # Звичайна картка / regular card
    "bg_card_hover":       "#F8FAFC",   # Фон картки при наведенні / card hover background

    # Текст / Text
    "text_primary":        "#111827",   # Основний текст / primary text
    "text_secondary":      "#374151",   # Другорядний текст / secondary text
    "text_muted":          "#6B7280",   # Приглушений текст / muted text

    # Акцент / Accent
    "accent":              "#2563EB",   # Основний акцентний колір / primary accent
    "accent_hover":        "#1D4ED8",   # Акцент при наведенні / accent hover
    "accent_pressed":      "#1E40AF",   # Акцент при натисканні / accent pressed
    "accent_text":         "#FFFFFF",   # Текст на акцентній кнопці або плашці / text on accent surfaces
    "accent_subtle":       "#DBEAFE",   # Слабкий акцентний фон / subtle accent background
    "accent_subtle_text":  "#1E40AF",   # Текст на слабкому акцентному фоні / text on subtle accent background

    # Статуси / Status
    "success":             "#059669",   # Успіх / success state
    "success_subtle":      "#D1FAE5",   # М’який фон успіху / subtle success background

    "warning":             "#D97706",   # Попередження / warning state
    "warning_subtle":      "#FFFBEB",   # М’який фон попередження / subtle warning background
    "warning_hover":       "#FEF3C7",   # Попередження при наведенні / warning hover background

    "critical":            "#DC2626",   # Критичний стан / critical state
    "critical_subtle":     "#FEF2F2",   # М’який фон критичного стану / subtle critical background
    "critical_hover":      "#FEE2E2",   # Критичний стан при наведенні / critical hover background

    # Межі / Borders
    "border_soft":         "#AEC9FD",   # М’яка межа / soft border
    "border_strong":       "#97BEF8",   # Виразніша межа / stronger border

    # Навігація / Navigation
    "nav_bg":              "#DBF0F3EA",   # Фон бокової навігації / side navigation background
    "nav_hover":           "#CAEDF1",   # Фон кнопки навігації при наведенні / navigation hover background
    "nav_active_bg":       "#2563EB",   # Активний пункт навігації / active navigation item background
    "nav_active_text":     "#FFFFFF",   # Текст активного пункту навігації / active navigation text
    "nav_footer":          "#9CA3AF",   # Текст або службова зона внизу навігації / navigation footer text

    # Роль / Role card
    "role_card_bg":        "#EFF1F5",   # Фон картки ролі / role card background
    "role_tag_bg":         "#DBEAFE",   # Фон ярлика ролі / role tag background
    "role_tag_text":       "#1E40AF",   # Текст ярлика ролі / role tag text

    # Dashboard специфіка / Dashboard specific
    "metric_title":        "#6B7280",   # Заголовок метрики / metric title
    "news_accent":         "#8B5CF6",   # Акцент для блоку новин / news accent
}

# ──────────────────────────────────────────────────────────────────
# ТІНІ / SHADOWS
# ──────────────────────────────────────────────────────────────────
SHADOW: dict[str, dict] = {
    "card_sm": {"radius": 8, "offset_y": 1, "alpha": 12},
    "card_md": {"radius": 16, "offset_y": 2, "alpha": 18},
    "card_lg": {"radius": 24, "offset_y": 4, "alpha": 24},
}

# ──────────────────────────────────────────────────────────────────
# АНІМАЦІЇ / ANIMATIONS (ms)
# ──────────────────────────────────────────────────────────────────
ANIMATION: dict[str, int] = {
    "fast":    150,     # hover, active
    "normal":  300,     # fade-in
    "slow":    500,     # screens, heavy transitions
}

# ──────────────────────────────────────────────────────────────────
# ВІДСТУПИ / SPACING (px)
# ──────────────────────────────────────────────────────────────────
SPACING: dict[str, int] = {
    "xs":   4,
    "sm":   8,
    "md":   12,
    "lg":   16,
    "xl":   24,
    "xxl":  32,
}

# ──────────────────────────────────────────────────────────────────
# РАДІУСИ / BORDER RADIUS (px)
# ──────────────────────────────────────────────────────────────────
RADIUS: dict[str, int] = {
    "sm":   8,
    "md":   12,
    "lg":   16,
    "xl":   20,
    "xxl":  24,
}

# ──────────────────────────────────────────────────────────────────
# ГЕОМЕТРІЯ / GEOMETRY (px)
# ──────────────────────────────────────────────────────────────────
SIZE: dict[str, int] = {
    "btn_height_sm":      36,
    "btn_height_md":      44,
    "nav_width":         240,
    "top_bar_height":     60,
    "status_bar_height":  32,
    "icon_sm":            16,
    "icon_md":            20,
    "card_min_width":    160,
    "card_min_height":   100,
    "window_min_w":     1100,
    "window_min_h":      720,
}

# ──────────────────────────────────────────────────────────────────
# ТИПОГРАФІКА / TYPOGRAPHY
# Формат: (family, size, bold)
# ──────────────────────────────────────────────────────────────────
FONT: dict[str, tuple] = {
    "title_xl": ("Segoe UI", 22, True),
    "title_l":  ("Segoe UI", 16, True),
    "title_m":  ("Segoe UI", 13, True),
    "body":     ("Segoe UI", 11, False),
    "caption":  ("Segoe UI",  9, False),
    "metric":   ("Segoe UI", 28, True),
    "label":    ("Segoe UI", 10, True),
    "nav_item": ("Segoe UI", 12, True),
}
