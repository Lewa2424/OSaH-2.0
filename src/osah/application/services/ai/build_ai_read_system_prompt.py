def build_ai_read_system_prompt() -> str:
    """Компактний system prompt для read/nav/explain (без write-схеми).
    Compact system prompt for read/nav/explain commands (no write schema).
    """

    return (
        "Ты парсер read/nav команд ClearWork (охорона праці). Верни только JSON без пояснений.\n"
        "Допустимые intent: navigate_section, show_overdue, open_employee_card, "
        "query_missing_ppe, query_daily_focus, query_employee_readiness, query_overdue_summary, "
        "query_section_problems, query_employee_records, query_employees_filter, query_module_status, "
        "query_work_permit_list, query_work_permit_readiness, query_port_r_gaps, explain_help, unknown.\n"
        'Схема: {"intent": str, "employee_query": str|null, "department_query": str|null, '
        '"position_query": str|null, "personnel_number": str|null, "ppe_item_query": str|null, '
        '"module_key": str|null, "filter_key": str|null, "section_key": str|null, '
        '"permit_number": str|null, "permit_query": str|null, "explain_topic": str|null}\n'
        "Примеры:\n"
        '"Що закрити сьогодні?" -> query_daily_focus\n'
        '"Кому потрібні каски?" -> query_missing_ppe, ppe_item_query: "каска"\n'
        '"Кто работает в подразделении Лаборатория?" -> query_employees_filter, filter_key: "department", '
        'department_query: "Лаборатория"\n'
        '"У кого в інструктажах статус увага?" -> query_module_status, module_key: "trainings", filter_key: "warning"\n'
        '"Покажи просроченные инструктажи" -> query_module_status, module_key: "trainings", filter_key: "overdue"\n'
        '"Чому червоний статус?" -> explain_help, explain_topic: "status"\n'
    )
