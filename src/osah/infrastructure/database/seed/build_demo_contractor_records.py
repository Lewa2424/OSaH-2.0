from osah.domain.entities.contractor_record import ContractorRecord
from osah.domain.entities.contractor_worker import ContractorWorker


def build_demo_contractor_records() -> tuple[ContractorRecord, ...]:
    """Повертає демо-підрядників з різними станами готовності.
    Returns demo contractors with different readiness states.
    """

    return (
        ContractorRecord(
            contractor_id="ctr-ready",
            company_name="Інтертек",
            contact_person="Шелестов Є.В.",
            contact_phone="+380954553545",
            contact_email="shelestov@intertek.test",
            activity_status="active",
            note_text="Планові електромонтажні роботи без зауважень.",
            enterprise_supervisor="Іваненко Сергій Петрович",
            work_scope_text="Щитова №2, профілактичний ремонт та перевірка кабельних трас.",
            workers=(
                ContractorWorker("ctr-ready-1", "Шевченко Ігор Іванович", "Електромонтажник", True, True, True, True),
                ContractorWorker("ctr-ready-2", "Коваль Віктор Сергійович", "Виконавець", True, True, True, True),
            ),
        ),
        ContractorRecord(
            contractor_id="ctr-warning",
            company_name="ПромВисота Сервіс",
            contact_person="Гнатюк Л.М.",
            contact_phone="+380671112233",
            contact_email="office@promvysota.test",
            activity_status="active",
            note_text="Роботи на висоті, є окремі люди з неготовими позиціями.",
            enterprise_supervisor="Бондар Андрій Олександрович",
            work_scope_text="Склад №4, ревізія металоконструкцій і заміна кріплень.",
            workers=(
                ContractorWorker("ctr-warning-1", "Мельник Юрій Олександрович", "Монтажник", True, True, True, True),
                ContractorWorker(
                    "ctr-warning-2",
                    "Кравченко Роман Петрівна",
                    "Стропальник",
                    False,
                    True,
                    True,
                    True,
                    "Не зафіксовано повторний інструктаж.",
                ),
                ContractorWorker(
                    "ctr-warning-3",
                    "Ткаченко Микола Вікторович",
                    "Спостерігач",
                    True,
                    False,
                    True,
                    True,
                    "Потрібна заміна каски та пояса.",
                ),
            ),
        ),
        ContractorRecord(
            contractor_id="ctr-blocked",
            company_name="ГазЛайн Монтаж",
            contact_person="Сидоренко О.О.",
            contact_phone="+380501234567",
            contact_email="dispatch@gasline.test",
            activity_status="active",
            note_text="Газонебезпечні роботи призупинені до усунення зауважень.",
            enterprise_supervisor="Іваненко Сергій Петрович",
            work_scope_text="Зварювальна дільниця, підключення газопроводу та огневі роботи.",
            workers=(
                ContractorWorker(
                    "ctr-blocked-1",
                    "Яценко Андрій Миколайович",
                    "Газорізальник",
                    False,
                    True,
                    False,
                    False,
                    "Немає актуального медогляду і допуску до вогневих робіт.",
                ),
                ContractorWorker(
                    "ctr-blocked-2",
                    "Яценко Олександр Миколайович",
                    "Виконавець",
                    False,
                    False,
                    True,
                    False,
                    "Не видані ЗІЗ і не оформлено допуск на ділянку.",
                ),
            ),
        ),
        ContractorRecord(
            contractor_id="ctr-finished",
            company_name="ЕкоКлін Про",
            contact_person="Марченко І.В.",
            contact_phone="+380631998877",
            contact_email="office@ecoclean.test",
            activity_status="finished",
            note_text="Очищення резервуара завершено, запис збережено для довідки.",
            enterprise_supervisor="Бондар Андрій Олександрович",
            work_scope_text="Резервуар №3, післяремонтне очищення і промивка.",
            workers=(
                ContractorWorker("ctr-finished-1", "Білик Сергій Сергійович", "Оператор очищення", True, True, True, True),
            ),
        ),
        ContractorRecord(
            contractor_id="ctr-archived",
            company_name="СтарБуд Реконструкція",
            contact_person="Петрова Н.С.",
            contact_phone="+380441234500",
            contact_email="archive@starbud.test",
            activity_status="archived",
            note_text="Старий підрядник, запис лишено в архіві.",
            enterprise_supervisor="",
            work_scope_text="",
            workers=(
                ContractorWorker("ctr-archived-1", "Демченко Наталія Миколаївна", "Інженер", True, True, True, True),
            ),
        ),
    )
