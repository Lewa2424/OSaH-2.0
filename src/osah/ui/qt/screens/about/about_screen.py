from PySide6.QtGui import QFont
from PySide6.QtWidgets import QFrame, QLabel, QVBoxLayout, QWidget

from osah.domain.entities.about_snapshot import AboutSnapshot
from osah.ui.qt.components.section_container import SectionContainer
from osah.ui.qt.components.section_header import SectionHeader
from osah.ui.qt.design.tokens import SPACING


class AboutScreen(QWidget):
    """Экран «О программе» в формате подробного обзорного описания.
    About screen presented as a detailed overview of the product.
    """

    def __init__(self, snapshot: AboutSnapshot) -> None:
        """Строит экран «О программе» в нейтральном и презентационном формате.
        Builds the About screen in a neutral and presentation-oriented format.
        """

        super().__init__()
        _ = snapshot

        layout = QVBoxLayout(self)
        layout.setContentsMargins(SPACING["xl"], SPACING["lg"], SPACING["xl"], SPACING["lg"])
        layout.setSpacing(SPACING["lg"])

        layout.addWidget(
            SectionHeader(
                "Про програму",
                "Розгорнутий опис призначення, можливостей і практичної цінності системи OSaH 2.0.",
            )
        )

        container = SectionContainer()
        content_layout = container.content_layout()
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(SPACING["lg"])

        content_layout.addWidget(self._build_intro_card())
        content_layout.addWidget(self._build_audience_card())
        content_layout.addWidget(self._build_capabilities_card())
        content_layout.addWidget(self._build_benefits_card())
        content_layout.addWidget(self._build_positioning_card())
        content_layout.addStretch()

        layout.addWidget(container)

    def _build_intro_card(self) -> QFrame:
        """Создаёт вводный блок с общим позиционированием системы.
        Creates the introductory card with the overall system positioning.
        """

        card = self._build_card()
        layout = card.layout()

        layout.addWidget(self._build_title_label("OSaH 2.0 — робоча система контролю охорони праці"))
        layout.addWidget(
            self._build_body_label(
                "OSaH 2.0 — це локальна настільна система для щоденної організації, обліку та "
                "контролю процесів охорони праці. Вона створена не як формальний довідник і не як "
                "вузький електронний журнал, а як практичний центр управління, у якому в одному "
                "місці зведено ключові контури безпеки підприємства."
            )
        )
        layout.addWidget(
            self._build_body_label(
                "Програма допомагає бачити ситуацію цілісно: хто допущений до роботи, де закінчуються "
                "строки, які працівники потребують уваги, які документи або записи відсутні, які новини "
                "та нормативні зміни варто врахувати вже сьогодні. У результаті користувач отримує не "
                "набір розрізнених таблиць, а керований і зрозумілий інструмент щоденного контролю."
            )
        )
        return card

    def _build_audience_card(self) -> QFrame:
        """Создаёт блок о целевой аудитории и рабочих сценариях.
        Creates the card describing the target users and work scenarios.
        """

        card = self._build_card()
        layout = card.layout()

        layout.addWidget(self._build_title_label("Для кого призначена система"))
        layout.addWidget(
            self._build_body_label(
                "OSaH 2.0 розрахована на інспектора з охорони праці, відповідальну особу, керівника "
                "підрозділу або керівника підприємства, якому потрібна зрозуміла картина стану без "
                "зайвої технічної складності. Система не вимагає спеціальної підготовки в адмініструванні "
                "серверів, поштових сервісів чи хмарних платформ."
            )
        )
        layout.addWidget(
            self._build_body_label(
                "Вона особливо корисна там, де щоденний контроль ведеться вручну, у різних файлах, "
                "окремих таблицях або паперових журналах. OSaH 2.0 зводить ці процеси в єдиний "
                "робочий контур і робить стан охорони праці більш прозорим, дисциплінованим і керованим."
            )
        )
        return card

    def _build_capabilities_card(self) -> QFrame:
        """Создаёт подробный блок с возможностями программы.
        Creates the detailed card describing the program capabilities.
        """

        card = self._build_card()
        layout = card.layout()

        layout.addWidget(self._build_title_label("Що вміє OSaH 2.0"))
        layout.addWidget(
            self._build_rich_text_label(
                "<ul style='margin-top:0px; margin-bottom:0px; padding-left:20px;'>"
                "<li><b>Облік працівників</b> з можливістю швидко перейти від загального реєстру до "
                "конкретної проблеми або ризику.</li>"
                "<li><b>Контроль інструктажів</b> з акцентом на пропущені, прострочені та проблемні записи.</li>"
                "<li><b>Контроль засобів індивідуального захисту</b> за нормами, видачею, строками та відхиленнями.</li>"
                "<li><b>Контроль медичних допусків</b> і стану записів, пов'язаних з допуском до роботи.</li>"
                "<li><b>Контроль нарядів-допусків</b> і суміжних критичних подій у виробничому контурі.</li>"
                "<li><b>Робота з підрядниками</b> у межах загального контуру охорони праці.</li>"
                "<li><b>Новини та нормативно-правові матеріали</b>, відібрані за тематикою охорони праці, "
                "а не змішані з загальною новинною стрічкою.</li>"
                "<li><b>Формування щоденного звіту</b> у зрозумілому файловому сценарії без складних "
                "поштових налаштувань та зовнішніх технічних залежностей.</li>"
                "<li><b>Резервне копіювання, відновлення та службові дії</b> для стабільної локальної роботи.</li>"
                "</ul>"
            )
        )
        return card

    def _build_benefits_card(self) -> QFrame:
        """Создаёт блок с выгодами и преимуществами системы.
        Creates the card describing the benefits and advantages of the system.
        """

        card = self._build_card()
        layout = card.layout()

        layout.addWidget(self._build_title_label("У чому практична перевага"))
        layout.addWidget(
            self._build_body_label(
                "Основна цінність OSaH 2.0 полягає в тому, що програма не просто зберігає дані, а "
                "перетворює їх на керовану картину стану. Користувач швидше бачить критичні точки, "
                "не губиться в другорядних записах і може концентруватися на діях, а не на пошуку інформації."
            )
        )
        layout.addWidget(
            self._build_body_label(
                "Для підприємства це означає більш дисциплінований контроль, менше пропусків, "
                "менше ризику накопичення проблем у тіньовому режимі та кращу готовність до внутрішніх "
                "і зовнішніх перевірок. Для керівника це означає, що стан охорони праці можна оцінити "
                "значно швидше, без довгого ручного зведення відомостей з різних джерел."
            )
        )
        layout.addWidget(
            self._build_body_label(
                "Для інспектора це означає менше рутини, менше повторюваної ручної роботи, менше "
                "перемикань між файлами та більше часу на реальний контроль. Програма працює як "
                "практичний інструмент повсякденної експлуатації, а не як формальна оболонка для зберігання архіву."
            )
        )
        return card

    def _build_positioning_card(self) -> QFrame:
        """Создаёт итоговый блок с позиционированием продукта.
        Creates the final product positioning card.
        """

        card = self._build_card()
        layout = card.layout()

        layout.addWidget(self._build_title_label("Чим OSaH 2.0 вигідно відрізняється"))
        layout.addWidget(
            self._build_body_label(
                "OSaH 2.0 не ускладнює повсякденну роботу зайвими технологічними бар'єрами. "
                "Система робить ставку на локальну надійність, зрозумілий сценарій роботи, тематичну "
                "релевантність даних і відчуття керованості. Саме тому вона може бути корисною як "
                "для невеликих підприємств, так і для виробничих майданчиків, де важливо швидко бачити "
                "реальні проблеми, а не губитися в розрізнених облікових слідах."
            )
        )
        layout.addWidget(
            self._build_body_label(
                "Узагальнено OSaH 2.0 можна описати так: це спокійна, практична і зібрана система, "
                "яка допомагає навести порядок у робочому контурі охорони праці, зробити контроль "
                "послідовним і зменшити залежність від випадковостей, пам'яті окремих людей та "
                "розкиданих по різних місцях записів."
            )
        )
        return card

    def _build_card(self) -> QFrame:
        """Создаёт типовую карточку для раздела «О программе».
        Creates a standard card for the About screen.
        """

        card = QFrame()
        card.setProperty("card", "true")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(SPACING["lg"], SPACING["lg"], SPACING["lg"], SPACING["lg"])
        layout.setSpacing(SPACING["sm"])
        return card

    def _build_title_label(self, text: str) -> QLabel:
        """Создаёт заголовок карточки с увеличенным шрифтом.
        Creates a card title label with enlarged font.
        """

        label = QLabel(text)
        label.setWordWrap(True)
        font = QFont("Segoe UI", 16)
        font.setBold(True)
        label.setFont(font)
        return label

    def _build_body_label(self, text: str) -> QLabel:
        """Создаёт текстовый абзац с увеличенным шрифтом.
        Creates a body paragraph label with enlarged font.
        """

        label = QLabel(text)
        label.setWordWrap(True)
        label.setFont(QFont("Segoe UI", 13))
        return label

    def _build_rich_text_label(self, text: str) -> QLabel:
        """Создаёт форматированный текстовый блок с увеличенным шрифтом.
        Creates a formatted text block with enlarged font.
        """

        label = QLabel(text)
        label.setWordWrap(True)
        label.setStyleSheet("font-size: 13px;")
        return label
