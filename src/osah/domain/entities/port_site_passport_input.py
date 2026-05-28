from dataclasses import dataclass


@dataclass(slots=True)
class PortSitePassportInput:
    """Дані форми створення паспорта ділянки ПОРТ-Р.
    Input data for creating a PORT-R site passport.
    """

    passport_code: str
    site_name: str
    site_type: str
    site_location: str
    site_description: str
    work_kind: str
    typical_operations: str
    work_mode: str
    typical_cargo: str
    cargo_features: str
    main_equipment: str
    lifting_devices: str
    has_railway_zone: bool
    has_auto_zone: bool
    has_crane_zone: bool
    crew_composition: str
    responsible_person: str
    has_contractors: bool
    contractors_note: str
    zone_kind: str
    has_night_works: bool
    weather_features: str
    has_limited_visibility: bool
    has_height_work: bool
    has_water_edge_work: bool
    has_stack_edge_work: bool
    has_communication_barrier: bool
    communication_barrier: str
    has_fencing_barrier: bool
    fencing_barrier: str
    has_signalman: bool
    has_lighting_barrier: bool
    lighting_barrier: str
    ppe_text: str
    additional_barriers: str
