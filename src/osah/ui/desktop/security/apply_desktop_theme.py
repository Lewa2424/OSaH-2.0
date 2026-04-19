from tkinter import Misc, ttk


STYLE_TOKENS = {
    "root_background": "#F0F2F5",
    "surface_background": "#FFFFFF",
    "shell_surface": "#F8F9FB",
    "nav_background": "#FFFFFF",
    "nav_surface": "#EFF1F5",
    "nav_surface_hover": "#E2E6EC",
    "nav_surface_inner": "#E8EBF0",
    "nav_button_aura": "#D8DCE4",
    "nav_button_glow": "#C8CDD6",
    "nav_button_shadow": "#BCC1CB",
    "nav_button_bevel": "#DADEEA",
    "nav_button_highlight": "#FFFFFF",
    "nav_button_outline": "#C5CAD6",
    "nav_button_radius": 14,
    "nav_button_neutral_glow": "#D8DCE4",
    "nav_button_warning_glow": "#FEF3C7",
    "nav_button_critical_glow": "#FEE2E2",
    "accent_background": "#2563EB",
    "accent_hover_background": "#1D4ED8",
    "accent_text": "#FFFFFF",
    "muted_text": "#6B7280",
    "strong_text": "#111827",
    "nav_text": "#111827",
    "nav_muted_text": "#6B7280",
    "role_card_background": "#EFF1F5",
    "role_card_text": "#374151",
    "role_tag_background": "#DBEAFE",
    "role_tag_hover_background": "#2563EB",
    "role_tag_text": "#1E40AF",
    "role_tag_hover_text": "#FFFFFF",
    "nav_footer_text": "#9CA3AF",
    "border_color": "#E5E7EB",
    "critical_background": "#DC2626",
    "warning_background": "#D97706",
    "info_background": "#2563EB",
    "soft_radius": 20,
}


# ###### ЗАСТОСУВАННЯ DESKTOP-ТЕМИ / ПРИМЕНЕНИЕ DESKTOP-ТЕМЫ ######
def apply_desktop_theme(root: Misc) -> None:
    """Налаштовує цілісну desktop-тему для shell, карток, форм і таблиць.
    Настраивает целостную desktop-тему для shell, карточек, форм и таблиц.
    """

    style = ttk.Style(root)
    style.theme_use("clam")

    root_background = STYLE_TOKENS["root_background"]
    surface_background = STYLE_TOKENS["surface_background"]
    strong_text = STYLE_TOKENS["strong_text"]
    muted_text = STYLE_TOKENS["muted_text"]
    border_color = STYLE_TOKENS["border_color"]
    accent_background = STYLE_TOKENS["accent_background"]
    accent_hover_background = STYLE_TOKENS["accent_hover_background"]
    critical_background = STYLE_TOKENS["critical_background"]
    warning_background = STYLE_TOKENS["warning_background"]
    info_background = STYLE_TOKENS["info_background"]

    style.configure(".", font=("Segoe UI", 10), background=root_background, foreground=strong_text)

    # ---- Treeview (залишається ttk, адаптований до нової схеми) ----
    style.configure(
        "Treeview",
        background=surface_background,
        fieldbackground=surface_background,
        foreground=strong_text,
        bordercolor=border_color,
        lightcolor=border_color,
        darkcolor=border_color,
        rowheight=30,
        font=("Segoe UI", 10),
    )
    style.map("Treeview", background=[("selected", "#DBEAFE")], foreground=[("selected", strong_text)])
    style.configure(
        "Treeview.Heading",
        background="#F3F4F6",
        foreground=strong_text,
        bordercolor=border_color,
        lightcolor=border_color,
        darkcolor=border_color,
        font=("Segoe UI", 10, "bold"),
        padding=(10, 8),
    )
    style.map("Treeview.Heading", background=[("active", "#E5E7EB")])

    # ---- Entry / Combobox (залишаються ttk) ----
    style.configure(
        "TEntry",
        fieldbackground=surface_background,
        foreground=strong_text,
        bordercolor=border_color,
        lightcolor=border_color,
        darkcolor=border_color,
        insertcolor=strong_text,
        padding=7,
    )
    style.map(
        "TEntry",
        bordercolor=[("focus", accent_background)],
        lightcolor=[("focus", accent_background)],
        darkcolor=[("focus", accent_background)],
    )
    style.configure(
        "TCombobox",
        fieldbackground=surface_background,
        foreground=strong_text,
        background=surface_background,
        bordercolor=border_color,
        lightcolor=border_color,
        darkcolor=border_color,
        arrowsize=16,
        padding=6,
    )
    style.map(
        "TCombobox",
        bordercolor=[("focus", accent_background)],
        lightcolor=[("focus", accent_background)],
        darkcolor=[("focus", accent_background)],
    )

    # ---- Separator ----
    style.configure("Separator.TSeparator", background=border_color)

    # ---- Fallback TButton (залишається для сумісності з ttk-контекстами) ----
    style.configure(
        "TButton",
        background=accent_background,
        foreground="#FFFFFF",
        bordercolor=accent_background,
        darkcolor=accent_background,
        lightcolor=accent_background,
        focusthickness=0,
        focuscolor=accent_background,
        padding=(14, 9),
        font=("Segoe UI", 10, "bold"),
    )
    style.map(
        "TButton",
        background=[("active", accent_hover_background), ("pressed", accent_hover_background)],
        bordercolor=[("active", accent_hover_background), ("pressed", accent_hover_background)],
        foreground=[("disabled", "#D1D5DB")],
    )
    style.configure(
        "Secondary.TButton",
        background=surface_background,
        foreground=strong_text,
        bordercolor=border_color,
        darkcolor=surface_background,
        lightcolor=surface_background,
        focuscolor=surface_background,
    )
    style.map(
        "Secondary.TButton",
        background=[("active", "#F3F4F6"), ("pressed", "#E5E7EB")],
        bordercolor=[("active", "#D1D5DB"), ("pressed", "#C9D0D8")],
    )

    # ---- Pill-мітки (InfoPill / WarningPill / CriticalPill) ----
    style.configure(
        "InfoPill.TLabel",
        background=info_background,
        foreground="#FFFFFF",
        font=("Segoe UI", 9, "bold"),
        padding=(9, 3),
    )
    style.configure(
        "WarningPill.TLabel",
        background=warning_background,
        foreground="#FFFFFF",
        font=("Segoe UI", 9, "bold"),
        padding=(9, 3),
    )
    style.configure(
        "CriticalPill.TLabel",
        background=critical_background,
        foreground="#FFFFFF",
        font=("Segoe UI", 9, "bold"),
        padding=(9, 3),
    )

    # ---- Checkbutton / Radiobutton ----
    style.configure("TRadiobutton", background=surface_background, foreground=strong_text, font=("Segoe UI", 10))
    style.map("TRadiobutton", background=[("active", surface_background)])
    style.configure("TCheckbutton", background=surface_background, foreground=strong_text, font=("Segoe UI", 10))
    style.map("TCheckbutton", background=[("active", surface_background)])

    # ---- TLabel fallbacks (для ttk-контексту) ----
    style.configure("PanelTitle.TLabel", background=surface_background, foreground=strong_text, font=("Segoe UI", 13, "bold"))
    style.configure("PanelText.TLabel", background=surface_background, foreground="#374151", font=("Segoe UI", 10))
    style.configure("CardTitle.TLabel", background=surface_background, foreground=muted_text, font=("Segoe UI", 10, "bold"))
    style.configure("Body.TLabel", background=root_background, foreground="#1F2937", font=("Segoe UI", 11))
