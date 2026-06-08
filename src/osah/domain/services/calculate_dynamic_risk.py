from math import prod

from osah.domain.entities.port_shift_zone import PortShiftZone, zone_from_r_dyn


# ###### РОЗРАХУНОК ДИНАМІЧНОГО РИЗИКУ / CALCULATE DYNAMIC RISK ######
def calculate_dynamic_risk(
    r_base: float,
    k_values: list[float],
    k_comp: float = 1.0,
) -> tuple[float, PortShiftZone]:
    """Обчислює динамічний ризик зміни за формулою ПОРТ-Р та повертає R_dyn і зону.
    Calculates the shift dynamic risk using the PORT-R formula and returns R_dyn and zone.

    Формула: R_dyn = R_base × K_т × K_п × K_с × K_в × K_б × K_comp
    Де k_values = [K_т, K_п, K_с, K_в, K_б] (1.0..2.0, крок 0.1).
    K_comp < 1.0 — знижувальний множник компенсуючого бар'єра.

    Зони:
        ≤ 1.40  — зелена (продовжити)
        1.41–1.80 — жовта (обмежити з бар'єром)
        ≥ 1.81  — червона (СТОП)
    """

    effective_k = k_values if k_values else [1.0]
    r_dyn = r_base * prod(effective_k) * k_comp
    r_dyn = round(r_dyn, 3)
    return r_dyn, zone_from_r_dyn(r_dyn)


def combine_k_comp(barrier_k_values: list[float]) -> float:
    """Повертає сумарний K_comp як добуток обраних компенсуючих бар'єрів.
    Returns the combined K_comp as the product of selected compensating barriers.
    """

    if not barrier_k_values:
        return 1.0
    return prod(barrier_k_values)
