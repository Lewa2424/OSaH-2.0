from pathlib import Path

from osah.application.services.load_medical_workspace import load_medical_workspace
from osah.application.services.load_ppe_workspace import load_ppe_workspace
from osah.application.services.load_training_workspace import load_training_workspace
from osah.application.services.load_work_permit_workspace import load_work_permit_workspace
from osah.domain.entities.app_section import AppSection
from osah.domain.entities.nav_fill_palette import NavFillPalette
from osah.domain.services.build_nav_fill_palette import build_nav_fill_palette
from osah.domain.services.build_section_nav_fill_buckets import build_section_nav_fill_bucket_profiles


# ###### ЗАВАНТАЖЕННЯ ПАЛІТР NAV-ДІАГРАМ / LOAD NAV DIAGRAM PALETTES ######
def load_section_nav_fill_profiles(database_path: Path) -> dict[AppSection, NavFillPalette | None]:
    """Зчитує дані модулів і будує палітри nav-діаграм для shell.
    Reads module data and builds nav diagram palettes for the shell.
    """

    training_workspace = load_training_workspace(database_path)
    ppe_workspace = load_ppe_workspace(database_path)
    medical_workspace = load_medical_workspace(database_path)
    work_permit_workspace = load_work_permit_workspace(database_path)

    bucket_profiles = build_section_nav_fill_bucket_profiles(
        training_workspace.summary,
        ppe_workspace.summary,
        medical_workspace.summary,
        work_permit_workspace.summary,
    )

    palettes: dict[AppSection, NavFillPalette | None] = {}
    for section, buckets in bucket_profiles.items():
        if buckets is None or buckets.total <= 0:
            palettes[section] = None
            continue
        palettes[section] = build_nav_fill_palette(buckets)
    return palettes
