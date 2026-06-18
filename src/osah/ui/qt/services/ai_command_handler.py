from pathlib import Path
from dataclasses import replace

from PySide6.QtCore import QObject
from PySide6.QtWidgets import QApplication

from osah.application.services.ai.apply_grounding_bulk_audience_choice import apply_grounding_bulk_audience_choice
from osah.application.services.ai.apply_grounding_entity_choice import apply_grounding_entity_choice
from osah.application.services.ai.build_ai_dialogue_state_from_answer import (
    build_ai_dialogue_state_from_answer,
)
from osah.application.services.ai.dispatch_ai_parsed_command import dispatch_ai_parsed_command
from osah.application.services.ai.execute_confirmed_ai_bulk_command import execute_confirmed_ai_bulk_command
from osah.application.services.ai.execute_confirmed_ai_command import execute_confirmed_ai_command
from osah.application.services.ai.ground_ai_command_draft import effective_department_query, ground_ai_command_draft
from osah.application.services.ai.log_ai_action import log_ai_action
from osah.application.services.ai.prepare_ai_bulk_command import prepare_ai_bulk_command
from osah.application.services.ai.prepare_ai_write_command import prepare_ai_write_command
from osah.application.services.ai.serialize_ai_command_draft_for_trace import serialize_ai_command_draft_for_trace
from osah.application.services.ai.resolve_ai_bulk_audience import (
    apply_bulk_audience_employee_choice,
)
from osah.application.services.ai.resolve_ai_entities import (
    apply_selected_entity_choice,
    apply_selected_ppe_item_choice,
)
from osah.application.services.ai.save_ai_pattern_memory_entry import save_ai_pattern_memory_entry
from osah.domain.entities.access_role import AccessRole
from osah.domain.entities.ai_command_draft import AiCommandDraft
from osah.domain.entities.ai_command_resolution import AiCommandResolution
from osah.domain.entities.ai_command_session import AiCommandSession
from osah.domain.entities.ai_dialogue_state import AiDialogueState
from osah.domain.entities.ai_command_resolution_status import AiCommandResolutionStatus
from osah.domain.entities.ai_dispatch_result import AiDispatchResult
from osah.domain.entities.ai_dispatch_result_kind import AiDispatchResultKind
from osah.domain.entities.ai_intent_kind import AiIntentKind
from osah.domain.entities.ai_navigation_target import AiNavigationTarget
from osah.domain.entities.ai_pending_slot_kind import AiPendingSlotKind
from osah.domain.entities.ai_prepared_command_status import AiPreparedCommandStatus
from osah.domain.entities.ai_ui_context import AiUiContext
from osah.domain.entities.app_section import AppSection
from osah.domain.services.ai.append_ai_dialogue_turn import append_ai_dialogue_turn
from osah.domain.services.ai.build_bulk_audience_guided_choices import (
    bulk_audience_hint_template,
    is_bulk_audience_hint_choice,
    needs_bulk_audience_guided_clarify,
    build_bulk_audience_guided_choices,
)
from osah.domain.services.ai.compiler.ai_intent_slot_specs import session_prompt_for_slot
from osah.domain.services.ai.compiler.compile_ai_command import compile_ai_command
from osah.domain.services.ai.convert_ai_dialogue_state import conversation_context_from_dialogue_state
from osah.infrastructure.logging.append_ai_command_trace import append_ai_command_trace_step, end_ai_command_trace
from osah.ui.qt.components.show_ai_bulk_confirmation_dialog import show_ai_bulk_confirmation_dialog
from osah.ui.qt.components.show_ai_confirmation_dialog import show_ai_confirmation_dialog
from osah.ui.qt.services.build_ai_ui_context import build_qt_navigation_intent


def _serialize_ai_draft(draft: AiCommandDraft | None) -> dict[str, object] | None:
    if draft is None:
        return None
    payload: dict[str, object] = {
        "intent": draft.intent.value,
        "raw_command": draft.raw_command,
        "source": draft.source,
        "employee_query": draft.employee_query,
        "personnel_number": draft.personnel_number,
        "ppe_item_query": draft.ppe_item_query,
        "items": [{"name": item.name, "quantity": item.quantity} for item in draft.items],
        "issue_date": draft.issue_date,
        "section_key": draft.section_key,
        "module_key": draft.module_key,
        "explain_topic": draft.explain_topic,
        "report_scope": draft.report_scope,
        "permit_number": draft.permit_number,
        "needs_confirmation": draft.needs_confirmation,
        "filter_key": draft.filter_key,
        "resolved_audience": list(draft.resolved_audience) if draft.resolved_audience else None,
    }
    if draft.bulk_audience_spec is not None:
        spec = draft.bulk_audience_spec
        payload["bulk_audience_spec"] = {
            "employee_queries": list(spec.employee_queries),
            "department_query": spec.department_query,
            "position_query": spec.position_query,
            "filter_key": spec.filter_key,
            "permit_number": spec.permit_number,
        }
    return payload


class AiCommandHandler(QObject):
    """Обробляє результат AI-команди в UI-шарі.
    Handles AI command resolution outcomes in the UI layer.
    """

    def __init__(
        self,
        *,
        database_path: Path,
        access_role: AccessRole,
        parent_widget,
        navigate_callback,
        show_panel_callback,
        workspace_reload_callback=None,
        submit_command_callback=None,
    ) -> None:
        super().__init__(parent_widget)
        self._database_path = database_path
        self._access_role = access_role
        self._parent_widget = parent_widget
        self._navigate_callback = navigate_callback
        self._show_panel_callback = show_panel_callback
        self._workspace_reload_callback = workspace_reload_callback
        self._submit_command_callback = submit_command_callback
        self._pending_draft: AiCommandDraft | None = None
        self._pending_ppe_item_index: int | None = None
        self._pending_answer_mode = False
        self._pending_bulk_mode = False
        self._pending_bulk_employee_query: str | None = None
        self._pending_grounding_choice_kind: str | None = None
        self._pending_ui_context = AiUiContext()
        self._active_trace_id: str | None = None
        self._active_session: AiCommandSession | None = None
        self._dialogue_state: AiDialogueState | None = None

    @property
    def dialogue_state(self) -> AiDialogueState | None:
        """Повертає стан діалогу для follow-up команд і LLM-контексту.
        Returns dialogue state for follow-up commands and LLM context.
        """

        return self._dialogue_state

    @property
    def conversation_context(self):
        """Зворотна сумісність для conversation context.
        Backward compatibility for conversation context.
        """

        return conversation_context_from_dialogue_state(self._dialogue_state)

    def clear_dialogue_state(self) -> None:
        """Скидає стан діалогу перед новою незалежною командою.
        Clears dialogue state before a new independent command.
        """

        self._dialogue_state = None

    def clear_conversation_context(self) -> None:
        """Скидає контекст діалогу перед новою незалежною командою.
        Clears dialogue context before a new independent command.
        """

        self.clear_dialogue_state()

    def record_user_turn(self, command_text: str) -> None:
        """Додає команду користувача до історії діалогу.
        Appends the user command to dialogue history.
        """

        self._dialogue_state = append_ai_dialogue_turn(
            self._dialogue_state,
            role="user",
            text=command_text,
        )

    @property
    def active_session(self) -> AiCommandSession | None:
        """Повертає активну сесію уточнення слотів.
        Returns the active slot-filling session.
        """

        return self._active_session

    def clear_active_session(self) -> None:
        """Скидає активну сесію після виконання або скасування.
        Clears the active session after execute or cancel.
        """

        self._active_session = None

    def handle_resolution(
        self,
        resolution: AiCommandResolution,
        *,
        ui_context: AiUiContext,
        assistant_panel,
    ) -> None:
        """Маршрутизує результат парсингу AI-команди.
        Routes the parsed AI command resolution.
        """

        if resolution.trace_id:
            self._active_trace_id = resolution.trace_id
        self._trace_ui("UI_HANDLE", detail=f"status={resolution.status.value}")

        if resolution.status == AiCommandResolutionStatus.ACCESS_DENIED:
            assistant_panel.append_assistant_message(resolution.message)
            self._log_action(resolution, was_confirmed=False, result_status="access_denied", result_message=resolution.message)
            return

        if resolution.status in {
            AiCommandResolutionStatus.NEEDS_CLARIFICATION,
            AiCommandResolutionStatus.RUNTIME_UNAVAILABLE,
            AiCommandResolutionStatus.LLM_UNAVAILABLE,
            AiCommandResolutionStatus.INVALID_DRAFT,
        }:
            if resolution.session is not None:
                self._active_session = resolution.session
            if resolution.next_dialogue_state is not None:
                self._dialogue_state = resolution.next_dialogue_state
            elif resolution.next_conversation_context is not None:
                from osah.domain.services.ai.convert_ai_dialogue_state import dialogue_state_from_conversation_context

                self._dialogue_state = dialogue_state_from_conversation_context(resolution.next_conversation_context)
            assistant_panel.append_assistant_message(resolution.message)
            if resolution.entity_choices:
                self._pending_draft = resolution.draft
                self._pending_grounding_choice_kind = resolution.pending_grounding_choice_kind
                self._pending_ui_context = ui_context
                assistant_panel.show_entity_choices(
                    resolution.entity_choices,
                    prompt=_entity_choice_prompt_for_message(resolution.message),
                )
                self._show_panel_callback()
            self._log_action(resolution, was_confirmed=False, result_status=resolution.status.value, result_message=resolution.message)
            return

        if resolution.status == AiCommandResolutionStatus.ANSWER_READY:
            self._trace_ui("UI_OUTPUT", detail=resolution.answer_text)
            assistant_panel.append_assistant_message(resolution.answer_text)
            if resolution.draft is not None:
                updated_state = build_ai_dialogue_state_from_answer(
                    self._database_path,
                    resolution.draft,
                    answer_text=resolution.answer_text,
                    previous_state=self._dialogue_state,
                )
                if updated_state is not None:
                    self._dialogue_state = updated_state
            if (
                self._dialogue_state is not None
                and self._dialogue_state.audience_personnel_numbers
                and self._dialogue_state.ppe_item_query
                and self._submit_command_callback is not None
            ):
                ppe_item = self._dialogue_state.ppe_item_query
                assistant_panel.show_follow_up_action(
                    "Видати всім зі списку",
                    lambda item=ppe_item: self._submit_command_callback(
                        f"выдай им {item} сегодняшней датой"
                    ),
                )
            if resolution.follow_up_navigation is not None:
                assistant_panel.show_follow_up_action(
                    "Показати в реєстрі",
                    lambda: self._navigate_callback(build_qt_navigation_intent(resolution.follow_up_navigation)),
                )
            if resolution.allow_copy:
                assistant_panel.show_follow_up_action(
                    "Копіювати",
                    lambda: QApplication.clipboard().setText(resolution.answer_text),
                )
            self._log_action(
                resolution,
                was_confirmed=False,
                result_status="answer_ready",
                result_message=resolution.message or "answer_ready",
                answer_length=len(resolution.answer_text),
            )
            return

        if resolution.draft is None:
            assistant_panel.append_assistant_message("Не вдалося підготувати чернетку.")
            return

        self._continue_parsed_draft(resolution.draft, ui_context, assistant_panel, resolution)

    def _continue_parsed_draft(
        self,
        draft: AiCommandDraft,
        ui_context: AiUiContext,
        assistant_panel,
        resolution: AiCommandResolution | None = None,
    ) -> None:
        """Компілює чернетку, перевіряє session-слоти і передає в dispatch.
        Compiles the draft, checks session slots, and dispatches.
        """

        compile_result = compile_ai_command(draft)
        compiled_draft = compile_result.draft
        self._trace_ui(
            "UI_COMPILE",
            detail=f"missing={','.join(slot.value for slot in compile_result.missing_slots) or 'none'}",
            payload=serialize_ai_command_draft_for_trace(compiled_draft),
        )

        if compile_result.missing_slots:
            session = AiCommandSession(
                draft=compiled_draft,
                missing_slots=compile_result.missing_slots,
                prompt_message=compile_result.session_prompt
                or session_prompt_for_slot(compile_result.missing_slots[0]),
                trace_id=self._active_trace_id,
            )
            self._active_session = session
            clarification_resolution = AiCommandResolution(
                status=AiCommandResolutionStatus.NEEDS_CLARIFICATION,
                message=session.prompt_message,
                draft=compiled_draft,
                session=session,
                trace_id=self._active_trace_id,
            )
            self.handle_resolution(clarification_resolution, ui_context=ui_context, assistant_panel=assistant_panel)
            return

        base_resolution = resolution or AiCommandResolution(
            status=AiCommandResolutionStatus.PARSED,
            draft=compiled_draft,
            trace_id=self._active_trace_id,
        )
        dispatch_result = dispatch_ai_parsed_command(
            self._database_path,
            compiled_draft,
            ui_context=ui_context,
        )
        self._handle_dispatch_result(
            dispatch_result,
            ui_context,
            assistant_panel,
            replace(base_resolution, draft=compiled_draft),
        )

    def _handle_dispatch_result(
        self,
        dispatch_result: AiDispatchResult,
        ui_context: AiUiContext,
        assistant_panel,
        resolution: AiCommandResolution,
    ) -> None:
        """Застосовує application-level результат маршрутизації в Qt UI.
        Applies an application-level dispatch result in the Qt UI.
        """

        if dispatch_result.kind == AiDispatchResultKind.ANSWER_READY:
            self._trace_ui("UI_OUTPUT", detail=dispatch_result.answer_text)
            assistant_panel.append_assistant_message(dispatch_result.answer_text)
            if dispatch_result.draft is not None:
                updated_state = build_ai_dialogue_state_from_answer(
                    self._database_path,
                    dispatch_result.draft,
                    answer_text=dispatch_result.answer_text,
                    previous_state=self._dialogue_state,
                )
                if updated_state is not None:
                    self._dialogue_state = updated_state
            if (
                self._dialogue_state is not None
                and self._dialogue_state.audience_personnel_numbers
                and self._dialogue_state.ppe_item_query
                and self._submit_command_callback is not None
            ):
                ppe_item = self._dialogue_state.ppe_item_query
                assistant_panel.show_follow_up_action(
                    "Видати всім зі списку",
                    lambda item=ppe_item: self._submit_command_callback(
                        f"выдай им {item} сегодняшней датой"
                    ),
                )
            if dispatch_result.follow_up_navigation is not None:
                assistant_panel.show_follow_up_action(
                    "Показати в реєстрі",
                    lambda: self._navigate_callback(build_qt_navigation_intent(dispatch_result.follow_up_navigation)),
                )
            if dispatch_result.allow_copy:
                assistant_panel.show_follow_up_action(
                    "Копіювати",
                    lambda: QApplication.clipboard().setText(dispatch_result.answer_text),
                )
            self._log_action(
                resolution,
                was_confirmed=False,
                result_status="answer_ready",
                result_message=dispatch_result.message or "answer_ready",
                answer_length=len(dispatch_result.answer_text),
            )
            return

        if dispatch_result.kind == AiDispatchResultKind.NAVIGATION_READY:
            if dispatch_result.navigation_target is None:
                assistant_panel.append_assistant_message("Не вдалося підготувати перехід.")
                return
            self._navigate_callback(build_qt_navigation_intent(dispatch_result.navigation_target))
            assistant_panel.append_assistant_message("Відкрив потрібний розділ.")
            self._log_action(resolution, was_confirmed=False, result_status="navigated", result_message="navigated")
            return

        if dispatch_result.kind == AiDispatchResultKind.ENTITY_CHOICES_REQUIRED:
            self._pending_draft = dispatch_result.draft
            self._pending_ppe_item_index = dispatch_result.pending_ppe_item_index
            self._pending_answer_mode = dispatch_result.pending_answer_mode
            self._pending_ui_context = ui_context
            assistant_panel.append_assistant_message(dispatch_result.message)
            assistant_panel.show_entity_choices(
                dispatch_result.choices,
                prompt=_entity_choice_prompt_for_message(dispatch_result.message),
            )
            self._show_panel_callback()
            return

        if dispatch_result.kind in {AiDispatchResultKind.NOT_FOUND, AiDispatchResultKind.UNSUPPORTED}:
            assistant_panel.append_assistant_message(dispatch_result.message)
            self._log_action(
                resolution,
                was_confirmed=False,
                result_status=dispatch_result.kind.value,
                result_message=dispatch_result.message,
            )
            return

        if dispatch_result.kind == AiDispatchResultKind.BULK_REQUIRED and dispatch_result.draft is not None:
            self._handle_bulk_intent(dispatch_result.draft, assistant_panel, resolution)
            return

        if dispatch_result.kind == AiDispatchResultKind.WRITE_REQUIRED and dispatch_result.draft is not None:
            self._handle_write_intent(dispatch_result.draft, assistant_panel, resolution)
            return

        assistant_panel.append_assistant_message("Ця команда поки не виконується автоматично.")

    def handle_entity_choice(self, choice_id: str, assistant_panel) -> None:
        """Продовжує виконання після вибору сутності.
        Continues execution after an entity has been selected.
        """

        if self._pending_draft is None:
            return

        pending_draft = self._pending_draft
        pending_ppe_item_index = self._pending_ppe_item_index
        pending_answer_mode = self._pending_answer_mode
        pending_bulk_mode = self._pending_bulk_mode
        pending_bulk_employee_query = self._pending_bulk_employee_query
        pending_grounding_choice_kind = self._pending_grounding_choice_kind
        pending_ui_context = self._pending_ui_context
        self._pending_draft = None
        self._pending_ppe_item_index = None
        self._pending_answer_mode = False
        self._pending_bulk_mode = False
        self._pending_bulk_employee_query = None
        self._pending_grounding_choice_kind = None
        self._pending_ui_context = AiUiContext()
        assistant_panel.clear_entity_choices()
        self._trace_ui("UI_ENTITY_CHOICE", detail=f"choice_id={choice_id}; answer_mode={pending_answer_mode}")

        if pending_grounding_choice_kind == "bulk_audience_hint" and is_bulk_audience_hint_choice(choice_id):
            template = bulk_audience_hint_template(choice_id)
            base_command = pending_draft.raw_command.rstrip("?.!").strip()
            session = AiCommandSession(
                draft=pending_draft,
                missing_slots=(AiPendingSlotKind.BULK_AUDIENCE,),
                prompt_message=f"Доповніть команду: «{base_command} {template}»",
                trace_id=self._active_trace_id,
            )
            self._active_session = session
            assistant_panel.append_assistant_message(session.prompt_message)
            self._show_panel_callback()
            return

        if pending_grounding_choice_kind in {"department", "position"}:
            _save_registry_synonym_from_grounding_choice(
                self._database_path,
                pending_draft,
                choice_kind=pending_grounding_choice_kind,
                canonical_value=choice_id,
            )
            if pending_draft.bulk_audience_spec is not None:
                updated_draft = apply_grounding_bulk_audience_choice(
                    pending_draft,
                    choice_id,
                    choice_kind=pending_grounding_choice_kind,
                )
            else:
                updated_draft = apply_grounding_entity_choice(
                    pending_draft,
                    choice_id,
                    choice_kind=pending_grounding_choice_kind,
                )
            grounding = ground_ai_command_draft(self._database_path, updated_draft)
            if not grounding.ok:
                assistant_panel.append_assistant_message(grounding.message)
                if grounding.choices:
                    self._pending_draft = updated_draft
                    self._pending_grounding_choice_kind = grounding.choice_kind
                    self._pending_ui_context = pending_ui_context
                    assistant_panel.show_entity_choices(
                        grounding.choices,
                        prompt=_entity_choice_prompt_for_message(grounding.message),
                    )
                    self._show_panel_callback()
                return
            self._continue_parsed_draft(grounding.draft, pending_ui_context, assistant_panel)
            return

        if pending_grounding_choice_kind:
            updated_draft = apply_grounding_entity_choice(
                pending_draft,
                choice_id,
                choice_kind=pending_grounding_choice_kind,
            )
            grounding = ground_ai_command_draft(self._database_path, updated_draft)
            if not grounding.ok:
                assistant_panel.append_assistant_message(grounding.message)
                if grounding.choices:
                    self._pending_draft = updated_draft
                    self._pending_grounding_choice_kind = grounding.choice_kind
                    self._pending_ui_context = pending_ui_context
                    assistant_panel.show_entity_choices(
                        grounding.choices,
                        prompt=_entity_choice_prompt_for_message(grounding.message),
                    )
                    self._show_panel_callback()
                return
            self._continue_parsed_draft(grounding.draft, pending_ui_context, assistant_panel)
            return

        if pending_bulk_mode and pending_bulk_employee_query:
            updated_draft = apply_bulk_audience_employee_choice(
                pending_draft,
                pending_employee_query=pending_bulk_employee_query,
                choice_id=choice_id,
            )
            resolution = AiCommandResolution(status=AiCommandResolutionStatus.PARSED, draft=updated_draft)
            self._handle_bulk_intent(updated_draft, assistant_panel, resolution)
            return

        if pending_ppe_item_index is not None:
            _save_registry_synonym_from_grounding_choice(
                self._database_path,
                pending_draft,
                choice_kind="ppe_item",
                canonical_value=choice_id,
            )
            updated_draft = apply_selected_ppe_item_choice(pending_draft, pending_ppe_item_index, choice_id)
            self._continue_parsed_draft(updated_draft, pending_ui_context, assistant_panel)
            return

        updated_draft = apply_selected_entity_choice(pending_draft, choice_id)
        self._trace_ui(
            "UI_ENTITY_AFTER_CHOICE",
            payload=serialize_ai_command_draft_for_trace(updated_draft),
        )
        self._continue_parsed_draft(updated_draft, pending_ui_context, assistant_panel)

    def _handle_bulk_intent(
        self,
        draft: AiCommandDraft,
        assistant_panel,
        resolution: AiCommandResolution,
    ) -> None:
        prepared = prepare_ai_bulk_command(self._database_path, draft)
        if prepared.status == AiPreparedCommandStatus.NEEDS_CLARIFICATION:
            self._pending_draft = prepared.draft
            self._pending_bulk_mode = True
            self._pending_bulk_employee_query = prepared.pending_employee_query
            self._pending_grounding_choice_kind = prepared.pending_registry_choice_kind
            assistant_panel.append_assistant_message(prepared.message)
            assistant_panel.show_entity_choices(
                prepared.choices,
                prompt=_entity_choice_prompt_for_message(prepared.message),
            )
            self._show_panel_callback()
            return
        if prepared.status != AiPreparedCommandStatus.READY or prepared.confirmation_view is None:
            assistant_panel.append_assistant_message(prepared.message)
            self._log_action(
                resolution,
                was_confirmed=False,
                result_status=prepared.status.value,
                result_message=prepared.message,
            )
            return

        resolved_draft = prepared.draft
        personnel_numbers = prepared.personnel_numbers
        dialog_result = show_ai_bulk_confirmation_dialog(self._parent_widget, prepared.confirmation_view)
        if dialog_result.action_id != "confirm":
            assistant_panel.append_assistant_message("Дію скасовано.")
            self._log_action(resolution, was_confirmed=False, result_status="cancelled", result_message="user_cancelled")
            return

        try:
            result_message = execute_confirmed_ai_bulk_command(
                self._database_path,
                resolved_draft,
                personnel_numbers=personnel_numbers,
                access_role=self._access_role,
            )
        except Exception as error:  # noqa: BLE001
            assistant_panel.append_assistant_message(str(error))
            self._log_action(resolution, was_confirmed=True, result_status="error", result_message=str(error))
            return

        assistant_panel.append_assistant_message(result_message)
        self._reload_workspace_after_ai_write(resolved_draft)
        self._log_action(
            resolution,
            was_confirmed=True,
            result_status="success",
            result_message=result_message,
            audience_size=len(personnel_numbers),
        )

    def _handle_write_intent(
        self,
        draft: AiCommandDraft,
        assistant_panel,
        resolution: AiCommandResolution,
    ) -> None:
        prepared = prepare_ai_write_command(self._database_path, draft)
        self._trace_ui(
            "UI_WRITE_PREPARE",
            detail=f"status={prepared.status.value}",
            payload=serialize_ai_command_draft_for_trace(prepared.draft),
        )
        if prepared.status == AiPreparedCommandStatus.NEEDS_CLARIFICATION:
            self._pending_draft = prepared.draft
            self._pending_ppe_item_index = prepared.pending_ppe_item_index
            self._pending_answer_mode = False
            assistant_panel.append_assistant_message(prepared.message)
            assistant_panel.show_entity_choices(
                prepared.choices,
                prompt=_entity_choice_prompt_for_message(prepared.message),
            )
            self._show_panel_callback()
            return
        if prepared.status != AiPreparedCommandStatus.READY or prepared.confirmation_view is None:
            assistant_panel.append_assistant_message(prepared.message)
            self._log_action(
                resolution,
                was_confirmed=False,
                result_status=prepared.status.value,
                result_message=prepared.message,
            )
            return

        self._confirm_prepared_and_execute(
            prepared.draft,
            prepared.personnel_number,
            prepared.confirmation_view,
            assistant_panel,
            resolution,
        )

    def _confirm_prepared_and_execute(
        self,
        draft: AiCommandDraft,
        personnel_number: str | None,
        confirmation_view,
        assistant_panel,
        resolution: AiCommandResolution,
    ) -> None:
        """Показує підтвердження для підготовленої write-команди.
        Shows confirmation for a prepared write command.
        """

        synonym_offer = _build_synonym_offer(draft)
        dialog_result = show_ai_confirmation_dialog(
            self._parent_widget,
            confirmation_view,
            synonym_offer=synonym_offer,
        )
        selected_action = dialog_result.action_id
        if selected_action != "confirm":
            assistant_panel.append_assistant_message("Дію скасовано.")
            self.clear_active_session()
            self._log_action(resolution, was_confirmed=False, result_status="cancelled", result_message="user_cancelled")
            return

        if dialog_result.remember_synonym and synonym_offer is not None:
            save_ai_pattern_memory_entry(
                self._database_path,
                source_phrase=synonym_offer.source_phrase,
                mapping_type="ppe_alias",
                target_value=synonym_offer.target_value,
            )

        try:
            result_message = execute_confirmed_ai_command(
                self._database_path,
                draft,
                resolved_personnel_number=personnel_number,
                access_role=self._access_role,
            )
        except Exception as error:  # noqa: BLE001
            assistant_panel.append_assistant_message(str(error))
            self._log_action(resolution, was_confirmed=True, result_status="error", result_message=str(error))
            return

        assistant_panel.append_assistant_message(result_message)
        self.clear_active_session()
        self._reload_workspace_after_ai_write(draft)
        if draft.intent == AiIntentKind.CREATE_WORK_PERMIT_DRAFT:
            self._navigate_callback(
                build_qt_navigation_intent(AiNavigationTarget(section=AppSection.WORK_PERMITS)),
            )
        self._log_action(resolution, was_confirmed=True, result_status="success", result_message=result_message)

    def _reload_workspace_after_ai_write(self, draft: AiCommandDraft) -> None:
        if self._workspace_reload_callback is None:
            return
        self._workspace_reload_callback(draft.intent)

    def _log_action(
        self,
        resolution: AiCommandResolution,
        *,
        was_confirmed: bool,
        result_status: str,
        result_message: str,
        answer_length: int | None = None,
        audience_size: int | None = None,
    ) -> None:
        draft = resolution.draft
        draft_payload = _serialize_ai_draft(draft)
        if draft_payload is not None and answer_length is not None:
            draft_payload["answer_length"] = answer_length
            draft_payload["query_kind"] = draft.intent.value if draft is not None else "unknown"
        if draft_payload is not None and audience_size is not None:
            draft_payload["audience_size"] = audience_size
            draft_payload["bulk_intent"] = draft.intent.value if draft is not None else "unknown"
        log_ai_action(
            self._database_path,
            raw_command=draft.raw_command if draft is not None else "",
            intent=draft.intent.value if draft is not None else "unknown",
            draft_payload=draft_payload,
            was_confirmed=was_confirmed,
            result_status=result_status,
            result_message=result_message,
            actor_role=self._access_role.value,
        )
        self._finish_trace(result_status, result_message)

    def _trace_ui(
        self,
        step: str,
        *,
        detail: str | None = None,
        payload: dict[str, object] | None = None,
    ) -> None:
        if not self._active_trace_id:
            return
        append_ai_command_trace_step(self._active_trace_id, step, detail=detail, payload=payload)

    def _finish_trace(self, outcome: str, detail: str | None = None) -> None:
        if not self._active_trace_id:
            return
        if detail:
            append_ai_command_trace_step(self._active_trace_id, "UI_FINAL", detail=detail)
        end_ai_command_trace(self._active_trace_id, outcome=outcome)
        self._active_trace_id = None


def _build_synonym_offer(draft: AiCommandDraft):
    from osah.ui.qt.components.show_ai_confirmation_dialog import AiSynonymOffer

    if draft.intent != AiIntentKind.CREATE_PPE_ISSUANCE or not draft.items:
        return None
    raw_lower = draft.raw_command.lower()
    for item in draft.items:
        if item.name.lower() in raw_lower:
            continue
        for token in raw_lower.replace(",", " ").split():
            if len(token) < 3:
                continue
            if token in item.name.lower():
                continue
            return AiSynonymOffer(source_phrase=token, target_value=item.name)
    return None


def _entity_choice_prompt_for_message(message: str) -> str | None:
    if "Ви мали на увазі" in message:
        return None
    return "Оберіть потрібний варіант:"


def _save_registry_synonym_from_grounding_choice(
    database_path: Path,
    draft: AiCommandDraft,
    *,
    choice_kind: str,
    canonical_value: str,
) -> None:
    source_query = _grounding_source_query(draft, choice_kind)
    if not source_query:
        return
    if source_query.strip().lower() == canonical_value.strip().lower():
        return
    mapping_type = {
        "department": "department_alias",
        "position": "position_alias",
        "ppe_item": "ppe_alias",
    }.get(choice_kind)
    if mapping_type is None:
        return
    save_ai_pattern_memory_entry(
        database_path,
        source_phrase=source_query,
        mapping_type=mapping_type,
        target_value=canonical_value,
    )


def _grounding_source_query(draft: AiCommandDraft, choice_kind: str) -> str | None:
    if choice_kind == "department":
        if draft.bulk_audience_spec is not None and draft.bulk_audience_spec.department_query:
            return draft.bulk_audience_spec.department_query
        return effective_department_query(draft)
    if choice_kind == "position":
        if draft.bulk_audience_spec is not None and draft.bulk_audience_spec.position_query:
            return draft.bulk_audience_spec.position_query
        return draft.position_query
    if choice_kind == "ppe_item":
        if draft.items:
            return draft.items[0].name
        return draft.ppe_item_query
    return None
