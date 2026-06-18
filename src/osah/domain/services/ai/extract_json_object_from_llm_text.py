import json
import re


def extract_json_object_from_llm_text(text: str) -> dict[str, object]:
    """Витягує перший JSON-об'єкт із відповіді LLM.
    Extracts the first JSON object from an LLM response.
    """

    normalized_text = text.strip()
    if not normalized_text:
        raise ValueError("Порожня відповідь моделі.")

    fenced_match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", normalized_text, flags=re.DOTALL)
    if fenced_match is not None:
        normalized_text = fenced_match.group(1).strip()

    decoder = json.JSONDecoder()
    for index, character in enumerate(normalized_text):
        if character != "{":
            continue
        try:
            parsed_value, _end_index = decoder.raw_decode(normalized_text[index:])
        except json.JSONDecodeError:
            continue
        if isinstance(parsed_value, dict):
            return parsed_value

    raise ValueError("JSON-об'єкт у відповіді моделі не знайдено.")
