"""Smoke-диагностика AI-команд: полный проход пайплайна без Qt.

Запуск:
  python tools/run_ai_command_smoke.py
  python tools/run_ai_command_smoke.py --phrase "Выдай Иванову каску"
  python tools/run_ai_command_smoke.py --id ppe_bulk_electricians
  python tools/run_ai_command_smoke.py --category ppe_single
  python tools/run_ai_command_smoke.py --output reports/ai_smoke_latest.json

Требуется demo DB (OSAH_ENABLE_DEMO_SEED=1) и при LLM-фразах — запущенный local llama-server.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import tempfile
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PHRASES_FILE = PROJECT_ROOT / "tools" / "fixtures" / "ai_command_smoke_phrases.json"
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from osah.application.services.ai.build_ai_dialogue_state_from_answer import build_ai_dialogue_state_from_answer
from osah.application.services.ai.dispatch_ai_parsed_command import dispatch_ai_parsed_command
from osah.application.services.ai.prepare_ai_bulk_command import prepare_ai_bulk_command
from osah.application.services.ai.prepare_ai_write_command import prepare_ai_write_command
from osah.application.services.ai.query_employees_by_department import query_employees_by_department
from osah.application.services.ai.query_employees_missing_ppe import query_employees_missing_ppe
from osah.application.services.ai.resolve_user_ai_command import resolve_user_ai_command
from osah.application.services.ai.serialize_ai_command_draft_for_trace import serialize_ai_command_draft_for_trace
from osah.application.services.initialize_application import initialize_application
from osah.domain.entities.access_role import AccessRole
from osah.domain.entities.ai_command_resolution import AiCommandResolution
from osah.domain.entities.ai_command_resolution_status import AiCommandResolutionStatus
from osah.domain.entities.ai_conversation_pending_kind import AiConversationPendingKind
from osah.domain.entities.ai_dialogue_state import AiDialogueState
from osah.domain.entities.ai_dispatch_result_kind import AiDispatchResultKind
from osah.domain.entities.ai_intent_kind import AiIntentKind
from osah.domain.entities.ai_prepared_command_status import AiPreparedCommandStatus
from osah.domain.entities.ai_ui_context import AiUiContext
from osah.domain.services.ai.compiler.compile_ai_command import compile_ai_command
from osah.infrastructure.config.application_paths import build_application_paths
from osah.infrastructure.config.build_ai_runtime_paths import build_ai_runtime_paths, is_ai_runtime_bundle_available
from osah.infrastructure.config.is_ai_command_trace_enabled import build_ai_command_trace_log_path
from osah.infrastructure.logging.shutdown_logging import shut_down_logging

_TRACE_STEP_PATTERN = re.compile(r"^\[([A-Z0-9_]+)\]")


@dataclass(slots=True)
class SmokePhrase:
    """Одна тестовая фраза из fixture.
    One test phrase from the smoke fixture.
    """

    id: str
    category: str
    command: str
    notes: str = ""
    context_setup: dict[str, Any] | None = None
    scenario: tuple[dict[str, Any], ...] = field(default_factory=tuple)


@dataclass(slots=True)
class SmokePhraseResult:
    """Результат диагностики одной фразы.
    Diagnostic result for a single phrase.
    """

    id: str
    category: str
    command: str
    notes: str = ""
    trace_id: str | None = None
    path_steps: list[str] = field(default_factory=list)
    resolution_status: str = ""
    resolution_message: str = ""
    intent: str | None = None
    source: str | None = None
    draft_snapshot: dict[str, Any] = field(default_factory=dict)
    dispatch_kind: str | None = None
    prepare_status: str | None = None
    prepare_message: str = ""
    choices_count: int = 0
    user_outcome: str = ""
    fail_stage: str | None = None
    duration_ms: int = 0
    error: str | None = None
    context_mode: str | None = None
    scenario_steps: list[dict[str, Any]] = field(default_factory=list)


def load_smoke_phrases(path: Path) -> list[SmokePhrase]:
    """Загружает список фраз из JSON-fixture.
    Loads phrase list from a JSON fixture.
    """

    payload = json.loads(path.read_text(encoding="utf-8"))
    phrases: list[SmokePhrase] = []
    for entry in payload.get("phrases", []):
        scenario_raw = entry.get("scenario")
        scenario = tuple(scenario_raw) if isinstance(scenario_raw, list) else ()
        command = str(entry.get("command", "")).strip()
        if not command and scenario:
            command = str(scenario[-1].get("command", "")).strip()
        phrases.append(
            SmokePhrase(
                id=str(entry["id"]),
                category=str(entry.get("category", "uncategorized")),
                command=command,
                notes=str(entry.get("notes", "")),
                context_setup=entry.get("context_setup"),
                scenario=scenario,
            )
        )
    return phrases


def filter_phrases(
    phrases: list[SmokePhrase],
    *,
    phrase_id: str | None,
    category: str | None,
    phrase_text: str | None,
) -> list[SmokePhrase]:
    """Фильтрует фразы по CLI-аргументам.
    Filters phrases by CLI arguments.
    """

    if phrase_text:
        return [SmokePhrase(id="cli", category="cli", command=phrase_text.strip())]
    filtered = phrases
    if phrase_id:
        filtered = [item for item in filtered if item.id == phrase_id]
    if category:
        if category == "context":
            filtered = [
                item
                for item in filtered
                if item.category == "context" or item.category == "context_scenario"
            ]
        else:
            filtered = [item for item in filtered if item.category == category]
    return filtered


def read_trace_steps(trace_id: str | None, *, log_path: Path) -> list[str]:
    """Читает шаги trace-log для trace_id.
    Reads trace-log steps for a trace id.
    """

    if not trace_id or not log_path.is_file():
        return []

    content = log_path.read_text(encoding="utf-8", errors="replace")
    marker = f"TRACE {trace_id} |"
    start = content.find(marker)
    if start < 0:
        return []
    end = content.find(f"TRACE_END {trace_id}", start)
    block = content[start:end] if end >= 0 else content[start:]
    steps: list[str] = []
    for line in block.splitlines():
        match = _TRACE_STEP_PATTERN.match(line.strip())
        if match:
            steps.append(match.group(1))
    return steps


def _draft_snapshot(draft) -> dict[str, Any]:
    if draft is None:
        return {}
    snapshot = serialize_ai_command_draft_for_trace(draft)
    spec = snapshot.get("bulk_audience_spec")
    if isinstance(spec, dict):
        snapshot["bulk_audience_spec"] = {
            key: spec.get(key)
            for key in (
                "employee_queries",
                "department_query",
                "position_query",
                "filter_key",
                "resolved_personnel_numbers",
            )
        }
    return snapshot


def _map_resolution_outcome(resolution: AiCommandResolution) -> tuple[str, str | None]:
    status = resolution.status
    if status == AiCommandResolutionStatus.ANSWER_READY:
        return "answer", None
    if status == AiCommandResolutionStatus.LLM_UNAVAILABLE:
        return "no_llm", "resolve"
    if status == AiCommandResolutionStatus.RUNTIME_UNAVAILABLE:
        return "no_runtime", "resolve"
    if status == AiCommandResolutionStatus.ACCESS_DENIED:
        return "access_denied", "resolve"
    if status == AiCommandResolutionStatus.INVALID_DRAFT:
        return "invalid", "resolve"
    if status == AiCommandResolutionStatus.NEEDS_CLARIFICATION:
        if resolution.entity_choices:
            return "clarify", "grounding"
        if resolution.session is not None:
            return "clarify", "session"
        return "clarify", "resolve"
    if status == AiCommandResolutionStatus.PARSED:
        return "parsed", None
    return status.value, "resolve"


def build_dialogue_state_from_setup(
    database_path: Path,
    setup: dict[str, Any],
) -> AiDialogueState | None:
    """Строит AiDialogueState из context_setup fixture.
    Builds AiDialogueState from a context_setup fixture block.
    """

    setup_type = str(setup.get("type", "manual")).strip().lower()
    if setup_type == "manual":
        numbers = tuple(str(value) for value in setup.get("audience_personnel_numbers", ()) if str(value).strip())
        labels = tuple(str(value) for value in setup.get("audience_labels", ()) if str(value).strip())
        if not numbers:
            return None
        return AiDialogueState(
            audience_personnel_numbers=numbers,
            audience_labels=labels,
            ppe_item_query=(str(setup["ppe_item_query"]).strip() if setup.get("ppe_item_query") else None),
            department_query=(str(setup["department_query"]).strip() if setup.get("department_query") else None),
            position_query=(str(setup["position_query"]).strip() if setup.get("position_query") else None),
            source_intent=(str(setup["source_intent"]).strip() if setup.get("source_intent") else None),
            pending_kind=AiConversationPendingKind.DEPARTMENT_EMPLOYEES
            if setup.get("pending_kind") == "department_employees"
            else None,
            last_answer_intent=(str(setup["last_answer_intent"]).strip() if setup.get("last_answer_intent") else None),
        )

    if setup_type == "from_missing_ppe":
        ppe_item_query = str(setup.get("ppe_item_query", "каска")).strip()
        department_query = (str(setup["department_query"]).strip() if setup.get("department_query") else None)
        position_query = (str(setup["position_query"]).strip() if setup.get("position_query") else None)
        rows = query_employees_missing_ppe(
            database_path,
            ppe_item_query,
            department_query=department_query,
            position_query=position_query,
        )
        if not rows:
            return None
        return AiDialogueState(
            audience_personnel_numbers=tuple(row.personnel_number for row in rows),
            audience_labels=tuple(row.full_name for row in rows),
            ppe_item_query=ppe_item_query,
            department_query=department_query,
            position_query=position_query,
            source_intent=AiIntentKind.QUERY_MISSING_PPE.value,
        )

    if setup_type == "from_department":
        department_query = str(setup.get("department_query", "")).strip()
        if not department_query:
            return None
        rows = query_employees_by_department(database_path, department_query)
        if not rows:
            return None
        return AiDialogueState(
            audience_personnel_numbers=tuple(row.personnel_number for row in rows),
            audience_labels=tuple(row.full_name for row in rows),
            department_query=department_query,
            source_intent=AiIntentKind.QUERY_EMPLOYEES_FILTER.value,
            pending_kind=AiConversationPendingKind.DEPARTMENT_EMPLOYEES,
        )

    return None


def advance_dialogue_state_after_command(
    database_path: Path,
    command: str,
    *,
    dialogue_state: AiDialogueState | None,
    project_root: Path,
    prefer_fallback_model: bool,
) -> AiDialogueState | None:
    """Выполняет read-шаг сценария и обновляет dialogue_state.
    Runs a read scenario step and updates dialogue_state.
    """

    resolution = resolve_user_ai_command(
        command,
        access_role=AccessRole.INSPECTOR,
        project_root=project_root,
        prefer_fallback_model=prefer_fallback_model,
        database_path=database_path,
        dialogue_state=dialogue_state,
        ui_context=AiUiContext(),
    )
    if resolution.status != AiCommandResolutionStatus.PARSED or resolution.draft is None:
        return dialogue_state

    compiled = compile_ai_command(resolution.draft).draft
    dispatch_result = dispatch_ai_parsed_command(
        database_path,
        compiled,
        ui_context=AiUiContext(),
    )
    if dispatch_result.kind != AiDispatchResultKind.ANSWER_READY:
        return dialogue_state
    if not dispatch_result.answer_text:
        return dialogue_state
    return build_ai_dialogue_state_from_answer(
        database_path,
        dispatch_result.draft or compiled,
        answer_text=dispatch_result.answer_text,
        previous_state=dialogue_state,
    )


def diagnose_phrase(
    phrase: SmokePhrase,
    *,
    database_path: Path,
    project_root: Path,
    trace_log_path: Path,
    prefer_fallback_model: bool,
    dialogue_state: AiDialogueState | None = None,
    context_mode: str | None = None,
) -> SmokePhraseResult:
    """Прогоняет фразу через resolve → dispatch → prepare как в UI (без Qt).
    Runs a phrase through resolve → dispatch → prepare like the UI (without Qt).
    """

    started = time.perf_counter()
    result = SmokePhraseResult(
        id=phrase.id,
        category=phrase.category,
        command=phrase.command,
        notes=phrase.notes,
        context_mode=context_mode,
    )
    try:
        resolution = resolve_user_ai_command(
            phrase.command,
            access_role=AccessRole.INSPECTOR,
            project_root=project_root,
            prefer_fallback_model=prefer_fallback_model,
            database_path=database_path,
            dialogue_state=dialogue_state,
            ui_context=AiUiContext(),
        )
    except Exception as error:  # noqa: BLE001
        result.error = f"{type(error).__name__}: {error}"
        result.user_outcome = "error"
        result.fail_stage = "exception"
        result.duration_ms = int((time.perf_counter() - started) * 1000)
        return result

    result.trace_id = resolution.trace_id
    result.path_steps = read_trace_steps(resolution.trace_id, log_path=trace_log_path)
    result.resolution_status = resolution.status.value
    result.resolution_message = resolution.message or ""
    result.choices_count = len(resolution.entity_choices)
    if resolution.draft is not None:
        result.intent = resolution.draft.intent.value
        result.source = resolution.draft.source
        result.draft_snapshot = _draft_snapshot(resolution.draft)

    outcome, fail_stage = _map_resolution_outcome(resolution)
    result.user_outcome = outcome
    result.fail_stage = fail_stage

    if resolution.status != AiCommandResolutionStatus.PARSED:
        result.duration_ms = int((time.perf_counter() - started) * 1000)
        return result

    draft = resolution.draft
    if draft is None:
        result.user_outcome = "error"
        result.fail_stage = "resolve"
        result.duration_ms = int((time.perf_counter() - started) * 1000)
        return result

    compile_result = compile_ai_command(draft)
    compiled_draft = compile_result.draft
    result.draft_snapshot = _draft_snapshot(compiled_draft)
    result.intent = compiled_draft.intent.value
    result.source = compiled_draft.source
    if compile_result.missing_slots:
        result.user_outcome = "clarify"
        result.fail_stage = "compile_session"
        result.prepare_message = compile_result.session_prompt or ""
        result.duration_ms = int((time.perf_counter() - started) * 1000)
        return result

    try:
        dispatch_result = dispatch_ai_parsed_command(
            database_path,
            compiled_draft,
            ui_context=AiUiContext(),
        )
    except Exception as error:  # noqa: BLE001
        result.error = f"{type(error).__name__}: {error}"
        result.user_outcome = "error"
        result.fail_stage = "dispatch"
        result.duration_ms = int((time.perf_counter() - started) * 1000)
        return result

    result.dispatch_kind = dispatch_result.kind.value
    result.resolution_message = dispatch_result.message or result.resolution_message

    if dispatch_result.kind == AiDispatchResultKind.ANSWER_READY:
        result.user_outcome = "answer"
        result.fail_stage = None
        result.duration_ms = int((time.perf_counter() - started) * 1000)
        return result

    if dispatch_result.kind == AiDispatchResultKind.NAVIGATION_READY:
        result.user_outcome = "navigation"
        result.fail_stage = None
        result.duration_ms = int((time.perf_counter() - started) * 1000)
        return result

    if dispatch_result.kind == AiDispatchResultKind.UNSUPPORTED:
        result.user_outcome = "unsupported"
        result.fail_stage = "dispatch"
        result.duration_ms = int((time.perf_counter() - started) * 1000)
        return result

    if dispatch_result.kind == AiDispatchResultKind.NOT_FOUND:
        result.user_outcome = "not_found"
        result.fail_stage = "dispatch"
        result.duration_ms = int((time.perf_counter() - started) * 1000)
        return result

    if dispatch_result.kind == AiDispatchResultKind.ENTITY_CHOICES_REQUIRED:
        result.user_outcome = "clarify"
        result.fail_stage = "dispatch"
        result.choices_count = len(dispatch_result.choices)
        result.duration_ms = int((time.perf_counter() - started) * 1000)
        return result

    try:
        if dispatch_result.kind == AiDispatchResultKind.WRITE_REQUIRED:
            prepared = prepare_ai_write_command(database_path, compiled_draft)
        elif dispatch_result.kind == AiDispatchResultKind.BULK_REQUIRED:
            prepared = prepare_ai_bulk_command(database_path, compiled_draft)
        else:
            result.user_outcome = "unsupported"
            result.fail_stage = "dispatch"
            result.duration_ms = int((time.perf_counter() - started) * 1000)
            return result
    except Exception as error:  # noqa: BLE001
        result.error = f"{type(error).__name__}: {error}"
        result.user_outcome = "error"
        result.fail_stage = "prepare"
        result.duration_ms = int((time.perf_counter() - started) * 1000)
        return result

    result.prepare_status = prepared.status.value
    result.prepare_message = prepared.message or ""
    result.choices_count = max(result.choices_count, len(prepared.choices))
    if prepared.status == AiPreparedCommandStatus.READY:
        result.user_outcome = "ready_confirm"
        result.fail_stage = None
    elif prepared.status == AiPreparedCommandStatus.NEEDS_CLARIFICATION:
        result.user_outcome = "clarify"
        result.fail_stage = "prepare"
    elif prepared.status == AiPreparedCommandStatus.NOT_FOUND:
        result.user_outcome = "not_found"
        result.fail_stage = "prepare"
    else:
        result.user_outcome = "invalid"
        result.fail_stage = "prepare"

    result.duration_ms = int((time.perf_counter() - started) * 1000)
    return result


def diagnose_phrase_entry(
    phrase: SmokePhrase,
    *,
    database_path: Path,
    project_root: Path,
    trace_log_path: Path,
    prefer_fallback_model: bool,
) -> SmokePhraseResult:
    """Диагностика одной записи fixture: сценарий, context_setup или одиночная фраза.
    Diagnoses one fixture entry: scenario, context_setup, or a single phrase.
    """

    if phrase.scenario:
        started = time.perf_counter()
        dialogue_state: AiDialogueState | None = None
        if phrase.context_setup:
            dialogue_state = build_dialogue_state_from_setup(database_path, phrase.context_setup)

        step_snapshots: list[dict[str, Any]] = []
        final_result: SmokePhraseResult | None = None

        for index, step in enumerate(phrase.scenario):
            command = str(step.get("command", "")).strip()
            if not command:
                continue

            if step.get("build_dialogue"):
                dialogue_state = advance_dialogue_state_after_command(
                    database_path,
                    command,
                    dialogue_state=dialogue_state,
                    project_root=project_root,
                    prefer_fallback_model=prefer_fallback_model,
                )
                step_snapshots.append(
                    {
                        "step": step.get("step", index),
                        "command": command,
                        "role": "build_dialogue",
                        "dialogue_audience_size": len(dialogue_state.audience_personnel_numbers)
                        if dialogue_state
                        else 0,
                    }
                )
                continue

            final_result = diagnose_phrase(
                SmokePhrase(
                    id=f"{phrase.id}__step{index}",
                    category=phrase.category,
                    command=command,
                ),
                database_path=database_path,
                project_root=project_root,
                trace_log_path=trace_log_path,
                prefer_fallback_model=prefer_fallback_model,
                dialogue_state=dialogue_state,
                context_mode="scenario",
            )
            step_snapshots.append(
                {
                    "step": step.get("step", index),
                    "command": command,
                    "user_outcome": final_result.user_outcome,
                    "fail_stage": final_result.fail_stage,
                    "intent": final_result.intent,
                    "message": final_result.prepare_message or final_result.resolution_message,
                }
            )

        if final_result is None:
            final_result = SmokePhraseResult(
                id=phrase.id,
                category=phrase.category,
                command=phrase.command,
                notes=phrase.notes,
                user_outcome="error",
                fail_stage="scenario",
                error="scenario has no actionable step (only build_dialogue?)",
            )
        else:
            final_result.id = phrase.id
            final_result.category = phrase.category
            final_result.command = phrase.command
            final_result.notes = phrase.notes

        final_result.context_mode = "scenario"
        final_result.scenario_steps = step_snapshots
        final_result.duration_ms = int((time.perf_counter() - started) * 1000)
        return final_result

    dialogue_state: AiDialogueState | None = None
    context_mode: str | None = None
    if phrase.context_setup:
        dialogue_state = build_dialogue_state_from_setup(database_path, phrase.context_setup)
        context_mode = str(phrase.context_setup.get("type", "manual"))
        if dialogue_state is None:
            return SmokePhraseResult(
                id=phrase.id,
                category=phrase.category,
                command=phrase.command,
                notes=phrase.notes,
                context_mode=context_mode,
                user_outcome="error",
                fail_stage="context_setup",
                error="failed to build dialogue_state from context_setup",
            )

    return diagnose_phrase(
        phrase,
        database_path=database_path,
        project_root=project_root,
        trace_log_path=trace_log_path,
        prefer_fallback_model=prefer_fallback_model,
        dialogue_state=dialogue_state,
        context_mode=context_mode,
    )


def print_summary(results: list[SmokePhraseResult]) -> None:
    """Печатает сводку по исходам.
    Prints a summary grouped by outcomes.
    """

    total = len(results)
    by_outcome: dict[str, int] = {}
    by_fail_stage: dict[str, int] = {}
    for item in results:
        by_outcome[item.user_outcome] = by_outcome.get(item.user_outcome, 0) + 1
        if item.fail_stage:
            by_fail_stage[item.fail_stage] = by_fail_stage.get(item.fail_stage, 0) + 1

    print()
    print("=" * 72)
    print(f"ИТОГО: {total} фраз")
    print("-" * 72)
    print("По user_outcome (что увидел бы пользователь):")
    for outcome, count in sorted(by_outcome.items(), key=lambda pair: (-pair[1], pair[0])):
        pct = (count / total * 100) if total else 0
        print(f"  {outcome:16} {count:3} ({pct:5.1f}%)")
    if by_fail_stage:
        print("По fail_stage (где остановилось):")
        for stage, count in sorted(by_fail_stage.items(), key=lambda pair: (-pair[1], pair[0])):
            print(f"  {stage:16} {count:3}")
    ready = by_outcome.get("ready_confirm", 0)
    answer = by_outcome.get("answer", 0) + by_outcome.get("navigation", 0)
    success_like = ready + answer
    print("-" * 72)
    print(f"Условный успех (ready_confirm + answer + navigation): {success_like}/{total}")
    print("=" * 72)


def print_table(results: list[SmokePhraseResult]) -> None:
    """Печатает компактную таблицу результатов.
    Prints a compact results table.
    """

    header = f"{'ID':28} {'OUTCOME':14} {'STAGE':12} {'INTENT':28} PATH"
    print(header)
    print("-" * len(header))
    for item in results:
        path = "→".join(item.path_steps[:4]) if item.path_steps else "-"
        intent = (item.intent or "-")[:28]
        stage = (item.fail_stage or "-")[:12]
        print(f"{item.id:28} {item.user_outcome:14} {stage:12} {intent:28} {path}")
        if item.scenario_steps:
            print(f"  SCENARIO ({len(item.scenario_steps)} steps):")
            for step in item.scenario_steps:
                print(
                    f"    - {step.get('command', step.get('step'))}: "
                    f"{step.get('user_outcome', step.get('role', '-'))}"
                )
        if item.error:
            print(f"  ERROR: {item.error}")
        elif item.resolution_message and item.user_outcome not in {"ready_confirm", "answer", "navigation"}:
            message = item.resolution_message.replace("\n", " ")[:120]
            print(f"  MSG: {message}")


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Smoke-диагностика AI-команд OSaH")
    parser.add_argument(
        "--phrases-file",
        type=Path,
        default=DEFAULT_PHRASES_FILE,
        help="JSON со списком фраз (по умолчанию tools/fixtures/ai_command_smoke_phrases.json)",
    )
    parser.add_argument("--phrase", help="Одна произвольная фраза")
    parser.add_argument("--id", dest="phrase_id", help="Запустить только фразу с этим id из fixture")
    parser.add_argument("--category", help="Фильтр по category из fixture")
    parser.add_argument("--output", type=Path, help="Сохранить полный JSON-отчёт")
    parser.add_argument(
        "--database",
        type=Path,
        help="Путь к существующей БД (иначе временная demo DB)",
    )
    parser.add_argument("--prefer-fallback-model", action="store_true", help="Использовать fallback LLM")
    parser.add_argument("--list", action="store_true", help="Показать фразы из fixture и выйти")
    return parser


def main() -> int:
    parser = build_arg_parser()
    args = parser.parse_args()

    if not args.phrases_file.is_file():
        print(f"Fixture not found: {args.phrases_file}", file=sys.stderr)
        return 1

    phrases = load_smoke_phrases(args.phrases_file)
    if args.list:
        for item in phrases:
            print(f"{item.id:30} [{item.category:14}] {item.command}")
        return 0

    selected = filter_phrases(
        phrases,
        phrase_id=args.phrase_id,
        category=args.category,
        phrase_text=args.phrase,
    )
    if not selected:
        print("Нет фраз для запуска. Проверьте --id / --category / --phrase.", file=sys.stderr)
        return 1

    os.environ.setdefault("OSAH_ENABLE_DEMO_SEED", "1")
    os.environ.setdefault("OSAH_ENABLE_AI_TRACE_LOG", "1")

    temp_dir: tempfile.TemporaryDirectory[str] | None = None
    project_root = PROJECT_ROOT
    if args.database:
        database_path = args.database
    else:
        temp_dir = tempfile.TemporaryDirectory()
        application_paths = build_application_paths(Path(temp_dir.name))
        context = initialize_application(application_paths)
        database_path = context.database_path

    runtime_paths = build_ai_runtime_paths(project_root)
    llm_available = is_ai_runtime_bundle_available(runtime_paths)
    print(f"DB: {database_path}")
    print(f"LLM runtime: {'available' if llm_available else 'NOT available (будут только fast/rule пути)'}")
    if llm_available:
        from osah.infrastructure.ai.llama_server_session import ensure_llama_server_running
        from osah.infrastructure.config.build_ai_runtime_paths import resolve_active_ai_model_path

        model_path = resolve_active_ai_model_path(
            runtime_paths,
            prefer_fallback=args.prefer_fallback_model,
        )
        print(f"llama-server: starting/checking ({model_path.name})…")
        ensure_llama_server_running(runtime_paths, model_path)
        print("llama-server: ready")

    trace_log_path = build_ai_command_trace_log_path()
    results: list[SmokePhraseResult] = []
    try:
        for index, phrase in enumerate(selected, start=1):
            print(f"\n[{index}/{len(selected)}] {phrase.id}: {phrase.command}")
            item = diagnose_phrase_entry(
                phrase,
                database_path=database_path,
                project_root=project_root,
                trace_log_path=trace_log_path,
                prefer_fallback_model=args.prefer_fallback_model,
            )
            results.append(item)
            stage = item.fail_stage or "-"
            print(
                f"  → {item.user_outcome} | stage={stage} | intent={item.intent or '-'} | "
                f"{item.duration_ms}ms | path={'→'.join(item.path_steps) or '-'}"
            )
            if item.error:
                print(f"  error: {item.error}")
            elif item.prepare_message and item.user_outcome not in {"ready_confirm"}:
                print(f"  msg: {item.prepare_message[:160]}")
    finally:
        shut_down_logging()
        if temp_dir is not None:
            temp_dir.cleanup()

    print_table(results)
    print_summary(results)

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "llm_available": llm_available,
            "database_path": str(database_path),
            "results": [asdict(item) for item in results],
        }
        args.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"\nJSON: {args.output}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
