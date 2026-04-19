import customtkinter as ctk

from osah.domain.entities.import_batch_summary import ImportBatchSummary
from osah.ui.desktop.content.ctk_styles import CARD, label_muted, label_body


# ###### ВІДОБРАЖЕННЯ КАРТКИ ПІДСУМКУ ІМПОРТУ / ОТРИСОВКА КАРТОЧКИ ИТОГА ИМПОРТА ######
def render_import_batch_summary_card(parent: ctk.CTkFrame, import_batch_summary: ImportBatchSummary | None) -> None:
    """Відображає короткий підсумок останньої партії імпорту працівників.
    Отрисовывает краткий итог последней партии импорта сотрудников.
    """

    card_frame = ctk.CTkFrame(parent, **CARD)
    card_frame.pack(fill="x", pady=(0, 20))
    label_muted(card_frame, "Остання партія імпорту").pack(anchor="w", padx=20, pady=(16, 0))

    if import_batch_summary is None:
        label_body(card_frame, "Чернеток імпорту поки немає.").pack(anchor="w", padx=20, pady=(10, 20))
        return

    summary_lines = (
        f"Файл: {import_batch_summary.source_name}",
        f"Формат: {import_batch_summary.source_format.upper()}",
        f"Чернеток: {import_batch_summary.draft_total}",
        f"Валідних: {import_batch_summary.valid_total}",
        f"З помилками: {import_batch_summary.invalid_total}",
        f"Застосовано: {import_batch_summary.applied_at or 'ще ні'}",
    )
    for index, summary_line in enumerate(summary_lines):
        label_body(card_frame, summary_line).pack(anchor="w", padx=20, pady=(8 if index == 0 else 4, 0))
        
    ctk.CTkFrame(card_frame, fg_color="transparent", height=20).pack()
