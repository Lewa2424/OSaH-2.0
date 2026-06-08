from pathlib import Path

from osah.domain.entities.port_shift_decision import PortShiftDecision
from osah.domain.entities.port_shift_zone import PortShiftZone
from osah.domain.services.calculate_dynamic_risk import calculate_dynamic_risk, combine_k_comp
from osah.infrastructure.database.commands.insert_audit_log import insert_audit_log
from osah.infrastructure.database.commands.insert_port_shift_checklist import insert_port_shift_checklist
from osah.infrastructure.database.create_database_connection import create_database_connection
from osah.infrastructure.database.queries.load_port_calibration import load_port_calibration


# ###### СТВОРЕННЯ ОЦІНКИ ЗМІНИ ПОРТ-Р / CREATE PORT-R SHIFT CHECKLIST ######
def create_port_shift_checklist(
    database_path: Path,
    passport_id: int,
    shift_date: str,
    shift_label: str,
    responsible_person: str,
    triggered_threshold_ids: list[int],
    active_barrier_ids: list[int],
    stop_reason: str,
    *,
    actor_name: str,
) -> tuple[float, PortShiftZone, PortShiftDecision, int]:
    """Розраховує динамічний ризик зміни, визначає зону і рішення та зберігає запис у журнал.
    Calculates the shift dynamic risk, determines the zone and decision, and saves the log record.

    active_barrier_ids — один або кілька компенсуючих бар'єрів (K_comp перемножуються).
    active_barrier_ids — one or more compensating barriers (K_comp values are multiplied).

    Повертає (R_dyn, zone, decision, checklist_id).
    Returns (R_dyn, zone, decision, checklist_id).
    """

    connection = create_database_connection(database_path)
    try:
        calibration = load_port_calibration(connection, passport_id)

        k_values: list[float] = []
        all_k_pairs: list[tuple[str, int | None, float]] = []

        for threshold in calibration.thresholds:
            if threshold.threshold_id in triggered_threshold_ids:
                k = threshold.k_value
            else:
                k = 1.0
            if threshold.threshold_id in triggered_threshold_ids:
                k_values.append(k)
            all_k_pairs.append((threshold.macrovariable.value, threshold.threshold_id, k))

        k_comp_values: list[float] = []
        for barrier_id in active_barrier_ids:
            for barrier in calibration.compensating_barriers:
                if barrier.barrier_id == barrier_id:
                    k_comp_values.append(barrier.k_comp)
                    break
        k_comp = combine_k_comp(k_comp_values)

        has_stop_trigger = any(
            t.is_stop_trigger and t.threshold_id in triggered_threshold_ids
            for t in calibration.thresholds
        )

        if has_stop_trigger or stop_reason:
            r_dyn, zone = calculate_dynamic_risk(calibration.r_base, k_values, k_comp)
            zone = PortShiftZone.RED
            decision = PortShiftDecision.STOP
        else:
            r_dyn, zone = calculate_dynamic_risk(calibration.r_base, k_values, k_comp)
            if zone == PortShiftZone.GREEN:
                decision = PortShiftDecision.CONTINUE
            elif zone == PortShiftZone.YELLOW:
                decision = PortShiftDecision.RESTRICT if active_barrier_ids else PortShiftDecision.STOP
            else:
                decision = PortShiftDecision.STOP

        checklist_id = insert_port_shift_checklist(
            connection,
            passport_id=passport_id,
            shift_date=shift_date,
            shift_label=shift_label,
            responsible_person=responsible_person,
            r_base=calibration.r_base,
            r_dyn=r_dyn,
            zone=zone,
            decision=decision,
            active_barrier_ids=active_barrier_ids,
            stop_reason=stop_reason,
            triggered_threshold_ids=triggered_threshold_ids,
            all_macrovariable_k_pairs=all_k_pairs,
        )
        insert_audit_log(
            connection,
            event_type="port_r.shift_checklist.created",
            module_name="port_r",
            event_level="info",
            actor_name=actor_name,
            entity_name=f"port_site_passport:{passport_id}",
            result_status="success",
            description_text=(
                f"checklist_id={checklist_id};"
                f"r_dyn={r_dyn};"
                f"zone={zone.value};"
                f"decision={decision.value};"
                f"barriers={len(active_barrier_ids)}"
            ),
        )
        connection.commit()
        return r_dyn, zone, decision, checklist_id
    finally:
        connection.close()
