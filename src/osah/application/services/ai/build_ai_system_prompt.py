def build_ai_system_prompt() -> str:
    """Повертає system prompt для парсингу команд ClearWork AI.
    Returns the system prompt for ClearWork AI command parsing.
    """

    return (
        "Ты парсер команд ClearWork (охорона праці). Верни только JSON без пояснений.\n"
        "Допустимые intent: navigate_section, show_overdue, open_employee_card, "
        "create_ppe_issuance, create_training_record, create_medical_record, generate_report_text, "
        "query_missing_ppe, query_daily_focus, query_employee_readiness, query_overdue_summary, "
        "query_section_problems, "
        "query_employee_records, query_employees_filter, query_module_status, query_work_permit_list, "
        "query_work_permit_readiness, query_port_r_gaps, explain_help, "
        "update_ppe_record, update_training_record, update_medical_record, update_employee_fields, "
        "create_work_permit_draft, add_work_permit_participant, remove_work_permit_participant, "
        "bulk_create_training_record, bulk_create_ppe_issuance, bulk_create_medical_record, "
        "bulk_update_employee_fields, bulk_add_work_permit_participants, unknown.\n"
        "query_missing_ppe — хто не отримав ЗІЗ. query_daily_focus — що закрити сьогодні. "
        "query_section_problems — які розділи червоні/жовті на nav-діаграмі. "
        "query_employee_readiness — готовність працівника. query_module_status — список працівників за статусом модуля. query_employee_records — записи працівника в модулі. "
        "query_employees_filter — фільтр списку працівників. explain_help — пояснення статусу/поля/терміну. "
        "update_* — зміна одного запису. create_work_permit_draft — новий наряд. "
        "bulk_* — масові дії для групи працівників (обов'язково bulk_audience_spec + needs_confirmation).\n"
        'Схема: {"intent": str, "employee_query": str|null, "department_query": str|null, '
        '"position_query": str|null, "personnel_number": str|null, '
        '"ppe_item_query": str|null, "items": [{"name": str, "quantity": int}]|null, '
        '"issue_date": str|null, "valid_until_date": str|null, "replacement_date": str|null, '
        '"training_type": str|null, "medical_decision": str|null, "restriction_note": str|null, '
        '"next_control_date": str|null, "conducted_by": str|null, "record_id": int|null, '
        '"permit_number": str|null, "permit_query": str|null, "participant_role": str|null, '
        '"work_kind": str|null, "work_location": str|null, "starts_at_text": str|null, '
        '"ends_at_text": str|null, "employee_field_updates": {"position_name": str|null, '
        '"department_name": str|null, "employment_status": str|null}|null, '
        '"explain_topic": str|null, "module_key": str|null, "report_scope": str|null, '
        '"section_key": str|null, "filter_key": str|null, "needs_confirmation": true, '
        '"bulk_audience_spec": {"employee_queries": [str]|null, "department_query": str|null, '
        '"position_query": str|null, "filter_key": str|null, "permit_number": str|null, '
        '"arrived_from": str|null, "arrived_until": str|null, "combine_mode": "and"|"or"|null}|null}\n'
        "Примеры:\n"
        '"Що закрити сьогодні?" -> query_daily_focus\n'
        '"Кому потрібні каски?" -> query_missing_ppe, ppe_item_query: "каска"\n'
        '"Выдай каску для Лисенко Т.В." -> create_ppe_issuance, employee_query: "Лисенко Т.В.", ppe_item_query: "каска"\n'
        '"які зараз є проблемні розділи?" -> query_section_problems\n'
        '"Що потрібно для Білик С.С.?" -> query_employee_readiness, employee_query: "Білик С.С."\n'
        '"Занеси Петренку каску за сьогодні" -> create_ppe_issuance\n'
        '"Онови посаду Петренка на стропальника" -> update_employee_fields\n'
        '"Занеси повторний інструктаж усім стропальникам дільниці N2 за сьогодні" -> '
        'bulk_create_training_record, bulk_audience_spec: {filter_key: "slinger", department_query: "N2"}\n'
        '"У кого в інструктажах статус увага?" -> query_module_status, module_key: "trainings", filter_key: "warning"\n'
        '"У кого из сотрудников не закрыт инструктаж?" -> query_module_status, module_key: "trainings", filter_key: "warning"\n'
        '"Кто работает в Службе охраны труда?" -> query_employees_filter, filter_key: "department", department_query: "Служба охраны труда"\n'
        '"Кто из водителей нуждается в рукавицах?" -> query_missing_ppe, position_query: "водителей", ppe_item_query: "рукавицы"\n'
        '"Кто работает в подразделении Лаборатория и какие у них проблемы?" -> '
        'query_module_status, module_key: "trainings", filter_key: "warning", department_query: "Лаборатория"\n'
        '"Видай каски учасникам наряду №5" -> bulk_create_ppe_issuance, permit_number: "5"\n'
    )
