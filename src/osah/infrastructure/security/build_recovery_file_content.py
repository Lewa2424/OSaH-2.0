# ###### ПОБУДОВА ВМІСТУ RECOVERY-ФАЙЛУ / ПОСТРОЕНИЕ СОДЕРЖИМОГО RECOVERY-ФАЙЛА ######
def build_recovery_file_content(installation_id: str, recovery_code: str, created_at_text: str) -> str:
    """Формує текст recovery-файлу для окремого офлайн-зберігання.
    Формирует текст recovery-файла для отдельного офлайн-хранения.
    """

    return (
        "OSaH 2.0 recovery file\n"
        f"Installation ID: {installation_id}\n"
        f"Recovery code: {recovery_code}\n"
        f"Created at: {created_at_text}\n"
        "\n"
        "Зберігайте цей файл окремо від робочого ПК.\n"
        "Не передавайте файл стороннім особам.\n"
        "Пароль програми тут не зберігається.\n"
    )
