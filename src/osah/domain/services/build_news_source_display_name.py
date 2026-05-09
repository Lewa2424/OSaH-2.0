def build_news_source_display_name(source_name: str) -> str:
    """Повертає спрощену назву джерела без технічної згадки RSS.
    Returns a simplified source name without the technical RSS mention.
    """

    normalized_name = source_name.replace(" — RSS новин", "").replace(" — RSS новини", "")
    normalized_name = normalized_name.replace(" — RSS", "").replace("RSS ", "")
    return normalized_name.strip()
