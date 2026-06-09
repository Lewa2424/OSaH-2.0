import customtkinter as ctk

from osah.domain.entities.daily_report_document import DailyReportDocument
from osah.domain.services.build_daily_report_email_body_text import build_daily_report_email_body_text
from osah.ui.desktop.content.ctk_styles import CARD, label_title, label_body
from osah.ui.desktop.security.apply_desktop_theme import STYLE_TOKENS


# ###### ВІДОБРАЖЕННЯ ПЕРЕГЛЯДУ ЩОДЕННОГО ЗВІТУ / ОТРИСОВКА ПРЕДПРОСМОТРА ЕЖЕДНЕВНОГО ОТЧЁТА ######
def render_daily_report_preview(parent: ctk.CTkFrame, daily_report_document: DailyReportDocument) -> None:
    """Відображає короткий текстовий preview щоденного звіту.
    Renders a short text preview of the daily report.
    """

    preview_frame = ctk.CTkFrame(parent, **CARD)
    preview_frame.pack(fill="both", expand=True, padx=24, pady=(0, 24))

    label_title(preview_frame, "Перегляд щоденного звіту").pack(anchor="w", padx=20, pady=(18, 0))
    label_body(preview_frame, daily_report_document.subject_text).pack(anchor="w", padx=20, pady=(8, 12))
    label_body(
        preview_frame,
        "Повний звіт формується у форматі Word (.docx). Збережіть файл, щоб відкрити його в Microsoft Word або аналогах.",
    ).pack(anchor="w", padx=20, pady=(0, 8))

    text_widget = ctk.CTkTextbox(
        preview_frame,
        wrap="word",
        font=("Consolas", 12),
        text_color=STYLE_TOKENS["strong_text"],
        fg_color=STYLE_TOKENS["shell_surface"],
        corner_radius=12,
        border_width=1,
        border_color=STYLE_TOKENS["border_color"],
    )
    text_widget.pack(fill="both", expand=True, padx=20, pady=(0, 20))
    text_widget.insert("1.0", build_daily_report_email_body_text(daily_report_document.snapshot))
    text_widget.configure(state="disabled")
