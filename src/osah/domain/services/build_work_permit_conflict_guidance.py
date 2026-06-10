from osah.domain.entities.work_permit_workspace_row import WorkPermitWorkspaceRow


# ###### ПІДКАЗКА ДЛЯ КОНФЛІКТІВ НАРЯДУ / WORK PERMIT CONFLICT GUIDANCE ######
def build_work_permit_conflict_guidance(row: WorkPermitWorkspaceRow | None) -> str:
    """Повертає коротку підказку інспектору, що зробити далі.
    Returns a short next-step hint for the inspector.
    """

    if row is None:
        return ""

    if row.participant_count == 0:
        return "Спочатку натисніть «Задати склад бригади» і додайте учасників."

    if not row.conflict_reasons:
        return "Критичних проблем не виявлено. За потреби зафіксуйте щоденну перевірку або закрийте наряд після робіт."

    if any("Цільовий інструктаж" in reason for reason in row.conflict_reasons):
        return (
            "Заповніть блок «Цільовий інструктаж» нижче (стан, дата, хто провів) "
            "і натисніть «Зберегти зміни». Запис з'явиться у всіх учасників."
        )

    return (
        "Перевірте учасників кнопками «Відкрити інструктажі / медицину / ЗІЗ» "
        "і виправте проблеми в відповідних розділах."
    )
