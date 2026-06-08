from enum import StrEnum


class PortMacrovariable(StrEnum):
    """П'ять макрозмінних моделі ПОРТ-Р (Т-П-С-В-Б).
    Five macrovariables of the PORT-R model (T-P-S-V-B).
    """

    T = "T"
    P = "P"
    S = "S"
    V = "V"
    B = "B"


PORT_MACROVARIABLE_LABELS: dict[PortMacrovariable, str] = {
    PortMacrovariable.T: "Т — Техніка",
    PortMacrovariable.P: "П — Персонал",
    PortMacrovariable.S: "С — Середовище",
    PortMacrovariable.V: "В — Вантаж",
    PortMacrovariable.B: "Б — Бар'єри",
}

PORT_MACROVARIABLE_DESCRIPTIONS: dict[PortMacrovariable, str] = {
    PortMacrovariable.T: "Стан, справність і просторова динаміка техніки",
    PortMacrovariable.P: "Кількісний та якісний склад персоналу, дотримання ролей",
    PortMacrovariable.S: "Погодні та зовнішні умови (видимість, ковзкість, вітер)",
    PortMacrovariable.V: "Фактичний стан вантажу (упаковка, ЦТ, розлив)",
    PortMacrovariable.B: "Огородження, розмітка, зв'язок, сигнальники, ЗІЗ",
}

MACROVARIABLE_ORDER: tuple[PortMacrovariable, ...] = (
    PortMacrovariable.T,
    PortMacrovariable.P,
    PortMacrovariable.S,
    PortMacrovariable.V,
    PortMacrovariable.B,
)


def format_macrovariable(mv: PortMacrovariable) -> str:
    """Повертає україномовну назву макрозмінної.
    Returns the Ukrainian label for a macrovariable.
    """

    return PORT_MACROVARIABLE_LABELS[mv]
