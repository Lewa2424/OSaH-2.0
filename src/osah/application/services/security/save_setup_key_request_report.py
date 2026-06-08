from pathlib import Path

from osah.domain.services.setup_key.build_setup_key_request_report import (
    SetupKeyRequestReportInput,
    build_setup_key_request_report,
)


# ###### ЗБЕРЕЖЕННЯ ЗАПИТУ НА КЛЮЧ / SAVE SETUP KEY REQUEST REPORT ######
def save_setup_key_request_report(
    output_path: Path,
    report_input: SetupKeyRequestReportInput,
) -> Path:
    """Записує текстовий запит на ключ установки у вибраний користувачем файл.
    Writes the setup key request text into the user-selected file.
    """

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        build_setup_key_request_report(report_input),
        encoding="utf-8",
    )
    return output_path
