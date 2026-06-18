import json
import unittest
from pathlib import Path

from osah.domain.entities.ai_intent_kind import AiIntentKind
from osah.domain.services.ai.compiler.compile_ai_command import compile_command_text
from osah.domain.services.ai.try_match_simple_ai_command import try_match_simple_ai_command


class AiGoldenTailScoreTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        fixture_path = Path(__file__).resolve().parent / "fixtures" / "ai_command_golden_set.json"
        cls._golden_entries = json.loads(fixture_path.read_text(encoding="utf-8"))

    def test_tail_score_thresholds(self) -> None:
        total = len(self._golden_entries)
        router_hits = 0
        compile_without_llm = 0
        unknown_count = 0

        for entry in self._golden_entries:
            command = entry["command"]
            routed = try_match_simple_ai_command(command)
            if routed is not None:
                router_hits += 1

            compiled = compile_command_text(command)
            if compiled is not None and not compiled.needs_llm:
                compile_without_llm += 1
                if compiled.draft.intent == AiIntentKind.UNKNOWN:
                    unknown_count += 1

        router_pct = router_hits / total * 100
        unknown_pct = unknown_count / total * 100

        self.assertGreaterEqual(router_pct, 45.0, msg=f"router={router_pct:.1f}%")
        self.assertLessEqual(unknown_pct, 15.0, msg=f"unknown={unknown_pct:.1f}%")


if __name__ == "__main__":
    unittest.main()
