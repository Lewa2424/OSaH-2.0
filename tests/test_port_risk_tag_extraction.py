import unittest

from osah.domain.services.extract_port_risk_tags_from_text import extract_port_risk_tags_from_text
from osah.domain.services.stem_ukrainian_word import stem_ukrainian_word


class PortRiskTagExtractionTests(unittest.TestCase):
    def test_stem_inflected_forms_match(self) -> None:
        self.assertEqual(
            stem_ukrainian_word("навантажувача"),
            stem_ukrainian_word("навантажувачу"),
        )
        self.assertEqual(
            stem_ukrainian_word("працівника"),
            stem_ukrainian_word("працівнику"),
        )

    def test_extracts_keywords_from_risk_text(self) -> None:
        tags = extract_port_risk_tags_from_text(
            "Перебування працівника в зоні руху навантажувача",
            "Колісна техніка на складських майданчиках",
        )
        self.assertIn(stem_ukrainian_word("працівник"), tags)
        self.assertIn(stem_ukrainian_word("навантажувач"), tags)
        zone_movement = f"{stem_ukrainian_word('зони')} {stem_ukrainian_word('руху')}"
        self.assertIn(zone_movement, tags)


if __name__ == "__main__":
    unittest.main()
