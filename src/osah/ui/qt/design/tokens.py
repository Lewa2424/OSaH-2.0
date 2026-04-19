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
    "bg_shell":            "#FFFFFF",   # Основні панелі / main panels
    "bg_panel":            "#F8F9FB",   # Трохи піднята поверхня / slightly elevated
    "bg_panel_elevated":   "#FFFFFF",   # Картки / cards
    "bg_card":             "#FFFFFF",   # Картки / cards
    "bg_card_hover":       "#F8FAFC",   # Hover картки / card hover

    # Текст / Text
    "text_primary":        "#111827",   # Основний текст / primary text
    "text_secondary":      "#374151",   # Другорядний / secondary
    "text_muted":          "#6B7280",   # Приглушений / muted

    # Акцент / Accent
    "accent":              "#2563EB",   # Основний акцент
    "accent_hover":        "#1D4ED8",   # Hover акценту
    "accent_pressed":      "#1E40AF",   # Pressed акценту
    "accent_text":         "#FFFFFF",   # Текст на акценті
    "accent_subtle":       "#DBEAFE",   # Слабкий акцент / subtle tint
    "accent_subtle_text":  "#1E40AF",   # Текст на слабкому акценті

    # Статуси / Status
    "success":             "#059669",
    "success_subtle":      "#D1FAE5",

    "warning":             "#D97706",
    "warning_subtle":      "#FFFBEB",
    "warning_hover":       "#FEF3C7",

    "critical":            "#DC2626",
    "critical_subtle":     "#FEF2F2",
    "critical_hover":      "#FEE2E2",

    # Межі / Borders
    "border_soft":         "#E5E7EB",
    "border_strong":       "#D1D5DB",

    # Навігація / Navigation
    "nav_bg":              "#FFFFFF",
    "nav_hover":           "#E2E6EC",
    "nav_active_bg":       "#2563EB",
    "nav_active_text":     "#FFFFFF",
    "nav_footer":          "#9CA3AF",

    # Роль / Role card
    "role_card_bg":        "#EFF1F5",
    "role_tag_bg":         "#DBEAFE",
    "role_tag_text":       "#1E40AF",
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
