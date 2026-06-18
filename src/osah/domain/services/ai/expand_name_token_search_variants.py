"""Варіанти написання імені/прізвища для RU/UA пошуку.
Name token variants for RU/UA employee search.
"""

from __future__ import annotations

from osah.domain.services.ai.normalize_cyrillic_search_text import normalize_cyrillic_search_text


def expand_name_token_search_variants(token: str) -> tuple[str, ...]:
    """Повертає варіанти токена ПІБ з урахуванням дательного відмінка та RU/UA.
    Returns name token variants including dative case and RU/UA spelling.
    """

    cleaned = token.strip()
    if not cleaned:
        return ()

    variants: set[str] = {cleaned, normalize_cyrillic_search_text(cleaned)}

    lowered = cleaned.lower()
    if len(cleaned) > 3 and lowered.endswith("у"):
        stem = cleaned[:-1]
        variants.update({stem, f"{stem}о", normalize_cyrillic_search_text(stem), normalize_cyrillic_search_text(f"{stem}о")})
    if len(cleaned) > 3 and lowered.endswith("ю"):
        stem = cleaned[:-1]
        variants.update({stem, f"{stem}я", normalize_cyrillic_search_text(stem), normalize_cyrillic_search_text(f"{stem}я")})
    if len(cleaned) > 3 and lowered.endswith("е"):
        stem = cleaned[:-1]
        variants.update(
            {
                stem,
                f"{stem}а",
                f"{stem}я",
                normalize_cyrillic_search_text(stem),
                normalize_cyrillic_search_text(f"{stem}а"),
                normalize_cyrillic_search_text(f"{stem}я"),
            }
        )
        if stem.lower().endswith("ль"):
            ua_base = stem[:-1]
            variants.update(
                {
                    f"{ua_base}ія",
                    f"{ua_base}ия",
                    normalize_cyrillic_search_text(f"{ua_base}ія"),
                    normalize_cyrillic_search_text(f"{ua_base}ия"),
                }
            )
    if len(cleaned) > 5 and lowered.endswith("овне"):
        stem = cleaned[:-2]
        variants.add(stem)
        variants.add(normalize_cyrillic_search_text(stem))
        if stem.lower().endswith("ов"):
            base = stem[:-2]
            variants.add(f"{base}івна")
            variants.add(normalize_cyrillic_search_text(f"{base}івна"))
    if len(cleaned) > 4 and lowered.endswith("ей"):
        base = cleaned[:-2]
        if base:
            variants.update(
                {
                    f"{base}ій",
                    f"{base}ий",
                    f"{base}ею",
                    normalize_cyrillic_search_text(f"{base}ій"),
                    normalize_cyrillic_search_text(f"{base}ий"),
                    normalize_cyrillic_search_text(f"{base}ею"),
                }
            )
    if len(cleaned) > 4 and lowered.endswith("ий"):
        base = cleaned[:-2]
        if base:
            variants.update(
                {
                    f"{base}ей",
                    f"{base}ій",
                    normalize_cyrillic_search_text(f"{base}ей"),
                    normalize_cyrillic_search_text(f"{base}ій"),
                }
            )
    if len(cleaned) > 4 and lowered.endswith("ій"):
        base = cleaned[:-2]
        if base:
            variants.update(
                {
                    f"{base}ей",
                    f"{base}ий",
                    normalize_cyrillic_search_text(f"{base}ей"),
                    normalize_cyrillic_search_text(f"{base}ий"),
                }
            )
    if len(cleaned) > 4 and lowered.endswith("ею"):
        base = cleaned[:-2]
        if base:
            variants.update(
                {
                    f"{base}ій",
                    f"{base}ий",
                    f"{base}ей",
                    normalize_cyrillic_search_text(f"{base}ій"),
                    normalize_cyrillic_search_text(f"{base}ий"),
                }
            )
    if len(cleaned) > 4 and lowered.endswith("евне"):
        stem = cleaned[:-2]
        variants.update(
            {
                f"{stem}вич",
                f"{stem}вна",
                normalize_cyrillic_search_text(f"{stem}вич"),
                normalize_cyrillic_search_text(f"{stem}вна"),
            }
        )
    if len(cleaned) > 4 and lowered.endswith("ичу"):
        stem = cleaned[:-1]
        variants.add(f"{stem}а")
        variants.add(normalize_cyrillic_search_text(f"{stem}а"))

    return tuple(value for value in variants if value)
