import json
from datetime import datetime
from pathlib import Path
from uuid import uuid4

from osah.infrastructure.config.is_ai_command_trace_enabled import (
    build_ai_command_trace_log_path,
    is_ai_command_trace_enabled,
)


def begin_ai_command_trace(user_command: str) -> str:
    """Починає новий блок trace для команди користувача.
    Starts a new trace block for a user command.
    """

    trace_id = uuid4().hex[:8]
    if not is_ai_command_trace_enabled():
        return trace_id

    log_path = build_ai_command_trace_log_path()
    log_path.parent.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    block = (
        f"\n{'=' * 72}\n"
        f"TRACE {trace_id} | {timestamp}\n"
        f"USER: {user_command.strip()}\n"
        f"{'-' * 72}\n"
    )
    with log_path.open("a", encoding="utf-8") as handle:
        handle.write(block)
    return trace_id


def append_ai_command_trace_step(
    trace_id: str,
    step: str,
    *,
    detail: str | None = None,
    payload: dict[str, object] | None = None,
) -> None:
    """Додає крок прийняття рішення в trace-log.
    Appends a decision step to the trace log.
    """

    if not is_ai_command_trace_enabled():
        return

    log_path = build_ai_command_trace_log_path()
    lines = [f"[{step}]"]
    if detail:
        lines.append(detail)
    if payload:
        lines.append(json.dumps(payload, ensure_ascii=False, indent=2))
    lines.append("")
    entry = "\n".join(lines)
    with log_path.open("a", encoding="utf-8") as handle:
        handle.write(entry)


def end_ai_command_trace(trace_id: str, *, outcome: str) -> None:
    """Завершує блок trace підсумковим рядком.
    Ends the trace block with a summary line.
    """

    if not is_ai_command_trace_enabled():
        return

    log_path = build_ai_command_trace_log_path()
    with log_path.open("a", encoding="utf-8") as handle:
        handle.write(f"TRACE_END {trace_id} | OUTCOME: {outcome}\n")
