import unittest

from osah.application.services.ai.parse_ai_command_draft_from_llm import _map_llm_payload_to_command_draft
from osah.domain.entities.ai_intent_kind import AiIntentKind


class AiSemanticLlmMappingTests(unittest.TestCase):
    def test_semantic_bulk_ppe_payload_maps_to_current_bulk_draft(self) -> None:
        draft = _map_llm_payload_to_command_draft(
            "Выдай всем участникам наряда 22 по паре перчаток и каске",
            {
                "intent": "create_ppe_issuance_for_work_permit_participants",
                "mode": "preview_then_confirm",
                "module": "ppe",
                "audience": {
                    "type": "work_permit_participants",
                    "permit_number": "22",
                },
                "payload": {
                    "event_date": "today",
                    "items": [
                        {"name": "перчатки", "quantity": 1},
                        {"name": "каска", "quantity": 1},
                    ],
                },
                "conditions": ["skip_if_active_ppe_exists"],
                "needs_confirmation": True,
            },
        )

        self.assertEqual(draft.intent, AiIntentKind.BULK_CREATE_PPE_ISSUANCE)
        self.assertIsNotNone(draft.bulk_audience_spec)
        assert draft.bulk_audience_spec is not None
        self.assertEqual(draft.bulk_audience_spec.permit_number, "22")
        self.assertEqual(tuple(item.name for item in draft.items), ("перчатки", "каска"))
        self.assertTrue(draft.needs_confirmation)
        self.assertIn("skip_if_active_ppe_exists", draft.semantic_conditions)

    def test_unsupported_semantic_payload_returns_safe_unknown(self) -> None:
        draft = _map_llm_payload_to_command_draft(
            "Добавь нового сотрудника: Петров Сергей Иванович",
            {
                "intent": "create_employee",
                "mode": "draft_only",
                "module": "employees",
                "audience": {"type": "none"},
                "payload": {"full_name": "Петров Сергей Иванович"},
                "conditions": [],
                "needs_confirmation": True,
            },
        )

        self.assertEqual(draft.intent, AiIntentKind.UNKNOWN)
        self.assertIsNotNone(draft.clarification_message)

    def test_legacy_payload_still_maps_when_model_returns_old_contract(self) -> None:
        draft = _map_llm_payload_to_command_draft(
            "Выдай каску Петрову",
            {
                "intent": "create_ppe_issuance",
                "employee_query": "Петров",
                "items": [{"name": "каска", "quantity": 1}],
                "issue_date": "today",
                "needs_confirmation": True,
            },
        )

        self.assertEqual(draft.intent, AiIntentKind.CREATE_PPE_ISSUANCE)
        self.assertEqual(draft.employee_query, "Петров")
        self.assertEqual(tuple(item.name for item in draft.items), ("каска",))


if __name__ == "__main__":
    unittest.main()
