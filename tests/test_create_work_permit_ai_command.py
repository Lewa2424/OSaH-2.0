import unittest

from osah.domain.entities.ai_intent_kind import AiIntentKind
from osah.domain.services.ai.compiler.compile_ai_command import compile_command_text
from osah.domain.services.ai.validate_ai_command_draft import validate_ai_command_draft


class CreateWorkPermitAiCommandTests(unittest.TestCase):
    def test_create_named_permit_with_participant_tail(self) -> None:
        command = (
            "Создай наряд допуск с именем ND-2026-QWER, участники: 0011, 0004, 0026, 0008"
        )
        compiled = compile_command_text(command)
        self.assertIsNotNone(compiled)
        assert compiled is not None
        draft = compiled.draft
        self.assertEqual(draft.intent, AiIntentKind.CREATE_WORK_PERMIT_DRAFT)
        self.assertEqual(draft.permit_query, "ND-2026-QWER")
        self.assertEqual(draft.work_kind, "Наряд-допуск")
        assert draft.bulk_audience_spec is not None
        self.assertEqual(
            draft.bulk_audience_spec.resolved_personnel_numbers,
            ("0011", "0004", "0026", "0008"),
        )
        self.assertEqual(validate_ai_command_draft(draft), [])


if __name__ == "__main__":
    unittest.main()
