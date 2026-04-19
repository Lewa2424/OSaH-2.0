from pathlib import Path

from osah.application.services.build_daily_report_document import build_daily_report_document
from osah.application.services.save_daily_report_copy import save_daily_report_copy


# ###### ЗБЕРЕЖЕННЯ КОПІЇ ДОКУМЕНТА ЩОДЕННОГО ЗВІТУ / СОХРАНЕНИЕ КОПИИ ДОКУМЕНТА ЕЖЕДНЕВНОГО ОТЧЁТА ######
def save_daily_report_document_copy(database_path: Path) -> Path:
    """Генерує щоденний звіт та зберігає його текстову копію.
    Генерирует ежедневный отчёт и сохраняет его текстовую копию.
    """

    return save_daily_report_copy(database_path, build_daily_report_document(database_path))
