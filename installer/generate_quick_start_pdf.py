"""Генерує PDF «швидкий старт» для поставки ClearWork.
Generates the ClearWork quick-start PDF for distribution.
"""

from __future__ import annotations

import os
import re
import sys
from pathlib import Path

from fpdf import FPDF

INSTALLER_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = INSTALLER_DIR.parent
VERSION_FILE = PROJECT_ROOT / "src" / "osah" / "version.py"
OUTPUT_PATH = INSTALLER_DIR / "ClearWork_швидкий_старт.pdf"


def _load_version() -> str:
    version_source = VERSION_FILE.read_text(encoding="utf-8")
    match = re.search(r'__version__\s*=\s*"([^"]+)"', version_source)
    if not match:
        raise RuntimeError(f"Could not read version from {VERSION_FILE}")
    return match.group(1)


def _resolve_font_paths() -> tuple[Path, Path]:
    fonts_directory = Path(os.environ.get("WINDIR", r"C:\Windows")) / "Fonts"
    regular_candidates = (
        fonts_directory / "segoeui.ttf",
        fonts_directory / "arial.ttf",
    )
    bold_candidates = (
        fonts_directory / "segoeuib.ttf",
        fonts_directory / "arialbd.ttf",
    )
    regular_path = next((path for path in regular_candidates if path.is_file()), None)
    bold_path = next((path for path in bold_candidates if path.is_file()), None)
    if regular_path is None or bold_path is None:
        raise RuntimeError("Segoe UI or Arial fonts were not found in the Windows Fonts folder.")
    return regular_path, bold_path


class QuickStartPdf(FPDF):
    """Компактний PDF-документ швидкого старту ClearWork."""

    def __init__(self, version_text: str) -> None:
        super().__init__(orientation="P", unit="mm", format="A4")
        self._version_text = version_text
        regular_path, bold_path = _resolve_font_paths()
        self.add_font("ClearWork", "", str(regular_path))
        self.add_font("ClearWork", "B", str(bold_path))
        self.set_auto_page_break(auto=True, margin=14)
        self.set_margins(16, 14, 16)

    def header(self) -> None:
        self.set_font("ClearWork", "B", 15)
        self.set_text_color(58, 95, 138)
        self.cell(self.epw, 8, f"ClearWork — швидкий старт ({self._version_text})", new_x="LMARGIN", new_y="NEXT")
        self.set_draw_color(211, 217, 226)
        self.line(self.l_margin, self.get_y(), self.w - self.r_margin, self.get_y())
        self.ln(3)

    def footer(self) -> None:
        self.set_y(-10)
        self.set_font("ClearWork", "", 8)
        self.set_text_color(107, 114, 128)
        self.cell(0, 5, f"ClearWork {self._version_text}  |  локальна програма обліку охорони праці", align="C")


def _section(pdf: QuickStartPdf, title: str) -> None:
    pdf.set_font("ClearWork", "B", 11)
    pdf.set_text_color(17, 24, 39)
    pdf.cell(0, 6, title, new_x="LMARGIN", new_y="NEXT")
    pdf.ln(1)


def _body(pdf: QuickStartPdf, text: str) -> None:
    pdf.set_font("ClearWork", "", 9.5)
    pdf.set_text_color(55, 65, 81)
    pdf.multi_cell(pdf.epw, 4.6, text)
    pdf.ln(1.5)


def _bullet_list(pdf: QuickStartPdf, items: tuple[str, ...]) -> None:
    pdf.set_font("ClearWork", "", 9.5)
    pdf.set_text_color(55, 65, 81)
    for item in items:
        pdf.multi_cell(pdf.epw, 4.6, f"- {item}")
    pdf.ln(1)


def build_quick_start_pdf(version_text: str) -> FPDF:
    """Збирає двосторінковий PDF швидкого старту.
    Builds the two-page quick-start PDF.
    """

    pdf = QuickStartPdf(version_text)
    pdf.add_page()

    _section(pdf, "Що входить у поставку")
    _body(
        pdf,
        "ClearWork — локальна програма на одному комп'ютері підприємства. "
        "Python окремо встановлювати не потрібно. Для робочої версії потрібен окремий ключ установки для цього ПК.",
    )

    _section(pdf, "Встановлення")
    _bullet_list(
        pdf,
        (
            "Запустіть ClearWork-Setup.exe. Бажано, щоб установку виконував системний адміністратор.",
            "Якщо Windows SmartScreen попереджає: «Докладніше» → «Все одно запустити».",
            "Завершіть майстер установки. Демо-галочку вмикайте лише для ознайомлення з тестовими даними.",
            "На останньому кроці відкрийте цю інструкцію перед першим запуском програми.",
        ),
    )

    _section(pdf, "Перший запуск (робоча версія)")
    _bullet_list(
        pdf,
        (
            "Запустіть ClearWork і скопіюйте ID установки з екрана активації.",
            "Надішліть ID та назву підприємства розробнику: alexeyovch26@gmail.com, +380954553545.",
            "Вставте отриманий ключ (CW-...) і натисніть «Активувати».",
            "Задайте паролі інспектора та керівника (мінімум 8 символів).",
            "Збережіть файл recovery окремо від папки програми.",
        ),
    )

    _section(pdf, "Де зберігаються дані")
    _body(
        pdf,
        "%LOCALAPPDATA%\\Programs\\ClearWork\\data\\ — база; data\\backups\\ — резервні копії; "
        "data\\recovery\\ — відновлення доступу; logs\\ — технічний журнал. "
        "Не видаляйте data\\ при оновленні, якщо потрібно зберегти робочі записи.",
    )

    pdf.add_page()

    _section(pdf, "Основні розділи програми")
    _bullet_list(
        pdf,
        (
            "Працівники — реєстр персоналу та статуси.",
            "Інструктажі, ЗІЗ, Медицина, Наряди-допуски — облік за працівниками.",
            "Підрядники — реєстр зовнішніх організацій.",
            "Звіти — щоденний звіт у форматі Word (.docx) для ручного збереження та відправки.",
            "PORT-R — паспорти ділянок, зміни, оперативні листи.",
            "Налаштування — резервні копії, імпорт, пошта, нагадування про звіт.",
            "Інструкції — довідка по кожному розділу всередині програми.",
        ),
    )

    _section(pdf, "Щоденний звіт")
    _body(
        pdf,
        "Програма не надсилає звіт автоматично. У заданий час з'явиться нагадування — "
        "сформуйте файл .docx і відправте його вручну зручним для підприємства способом.",
    )

    _section(pdf, "Резервні копії та оновлення")
    _bullet_list(
        pdf,
        (
            "Автокопія створюється раз на день при запуску.",
            "Додаткову копію можна зробити в Налаштуваннях перед оновленням.",
            "Нову версію встановлюйте поверх старої. Не видаляйте data\\ без потреби.",
            "Якщо data\\ видалено — з'явиться новий ID установки і знадобиться новий ключ (перепривязка через розробника, один раз).",
        ),
    )

    _section(pdf, "Демонстрація")
    _body(
        pdf,
        "ClearWork-Demo-Setup — окрема демо-збірка на 48 годин без ключа. "
        "Звичайний інсталятор із демо-галочкою дає тестові дані, але ключ установки все одно потрібен.",
    )

    _section(pdf, "Підтримка")
    _body(
        pdf,
        "alexeyovch26@gmail.com  |  +380954553545\n"
        "Повна інструкція: ClearWork_користувач.md у папці програми. "
        "Якщо програма не запускається — перевірте logs\\osah.log.",
    )

    return pdf


# ###### ГЕНЕРАЦІЯ PDF / GENERATE QUICK START PDF ######
def generate_quick_start_pdf(output_path: Path | None = None) -> Path:
    """Створює PDF-файл швидкого старту у каталозі installer.
    Creates the quick-start PDF file in the installer directory.
    """

    target_path = output_path or OUTPUT_PATH
    version_text = _load_version()
    pdf = build_quick_start_pdf(version_text)
    target_path.parent.mkdir(parents=True, exist_ok=True)
    pdf.output(str(target_path))
    return target_path


if __name__ == "__main__":
    generated_path = generate_quick_start_pdf()
    print(f"Generated: {generated_path}")
    sys.exit(0)
