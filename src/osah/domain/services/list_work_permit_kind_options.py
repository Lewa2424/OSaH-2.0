from osah.domain.entities.work_permit_kind_option import WorkPermitKindOption


def list_work_permit_kind_options() -> tuple[WorkPermitKindOption, ...]:
    """Повертає типовий каталог видів нарядів-допусків без жорсткої нормативної валідації.
    Returns a typical catalog of work-permit kinds without strict normative validation.
    """

    return (
        WorkPermitKindOption(
            key="hot_work",
            label="Вогневі роботи",
            guidance_text="Універсальний шаблон для робіт із джерелом відкритого полум'я, іскроутворенням або нагрівом.",
        ),
        WorkPermitKindOption(
            key="work_at_height",
            label="Роботи на висоті",
            guidance_text="Універсальний шаблон для робіт на висоті, де потрібен окремий контроль складу бригади та строку дії наряду.",
        ),
        WorkPermitKindOption(
            key="gas_hazardous",
            label="Газонебезпечні роботи",
            guidance_text="Універсальний шаблон для робіт у середовищі з ризиком шкідливих, токсичних або вибухонебезпечних газів.",
        ),
        WorkPermitKindOption(
            key="confined_space",
            label="Роботи в замкненому просторі",
            guidance_text="Універсальний шаблон для робіт у колодязях, резервуарах, ємностях та інших обмежених просторах.",
        ),
        WorkPermitKindOption(
            key="electrical",
            label="Роботи в електроустановках",
            guidance_text="Універсальний шаблон для робіт в електроустановках, шафах, комірках та на лініях живлення.",
        ),
        WorkPermitKindOption(
            key="excavation",
            label="Земляні роботи",
            guidance_text="Універсальний шаблон для траншей, котлованів, шурфів та інших робіт із розкриттям ґрунту.",
        ),
        WorkPermitKindOption(
            key="lifting",
            label="Вантажопідіймальні роботи",
            guidance_text="Універсальний шаблон для робіт із кранами, тельферами, підіймачами та переміщенням важких вантажів.",
        ),
        WorkPermitKindOption(
            key="repair",
            label="Ремонтні роботи",
            guidance_text="Універсальний шаблон для ремонтів обладнання, вузлів, агрегатів і виробничих дільниць.",
        ),
        WorkPermitKindOption(
            key="other",
            label="Інший вид робіт",
            guidance_text="Використовуйте цей варіант, якщо потрібного типу немає в каталозі, і уточніть вид робіт вручну.",
        ),
    )
