from osah.domain.entities.contractor_readiness_snapshot import ContractorReadinessSnapshot
from osah.domain.entities.contractor_readiness_status import ContractorReadinessStatus
from osah.domain.entities.contractor_record import ContractorRecord
from osah.domain.entities.contractor_worker import ContractorWorker


def build_contractor_readiness_snapshot(record: ContractorRecord) -> ContractorReadinessSnapshot:
    """Будує легкий зріз готовності підрядника до робіт.
    Builds a lightweight readiness snapshot for contractor work access.
    """

    if record.activity_status == "archived":
        return ContractorReadinessSnapshot(
            status=ContractorReadinessStatus.ARCHIVED,
            status_label="Архівний",
            can_work_now=False,
            total_workers=len(record.workers),
            ready_workers=0,
            problem_workers=len(record.workers),
            headline_text="Запис переведено в архів.",
            issues_text="Архівний підрядник не використовується для поточного допуску.",
        )
    if record.activity_status == "finished":
        return ContractorReadinessSnapshot(
            status=ContractorReadinessStatus.FINISHED,
            status_label="Завершений",
            can_work_now=False,
            total_workers=len(record.workers),
            ready_workers=_count_ready_workers(record.workers),
            problem_workers=_count_problem_workers(record.workers),
            headline_text="Роботи з підрядником завершені.",
            issues_text=_build_issues_text(record.workers) or "Поточні роботи не ведуться.",
        )

    total_workers = len(record.workers)
    ready_workers = _count_ready_workers(record.workers)
    problem_workers = total_workers - ready_workers
    if total_workers == 0:
        return ContractorReadinessSnapshot(
            status=ContractorReadinessStatus.BLOCKED,
            status_label="Не готовий",
            can_work_now=False,
            total_workers=0,
            ready_workers=0,
            problem_workers=0,
            headline_text="Склад працівників підрядника не заповнено.",
            issues_text="Неможливо оцінити допуск без списку людей підрядника.",
        )
    if problem_workers == 0:
        return ContractorReadinessSnapshot(
            status=ContractorReadinessStatus.READY,
            status_label="Готовий",
            can_work_now=True,
            total_workers=total_workers,
            ready_workers=ready_workers,
            problem_workers=0,
            headline_text=f"Усі {ready_workers} працівн. готові до роботи.",
            issues_text="Критичних зауважень по складу підрядника не виявлено.",
        )
    if ready_workers == 0:
        return ContractorReadinessSnapshot(
            status=ContractorReadinessStatus.BLOCKED,
            status_label="Не готовий",
            can_work_now=False,
            total_workers=total_workers,
            ready_workers=0,
            problem_workers=problem_workers,
            headline_text="Жоден працівник підрядника не готовий до роботи.",
            issues_text=_build_issues_text(record.workers),
        )
    return ContractorReadinessSnapshot(
        status=ContractorReadinessStatus.WARNING,
        status_label="Є зауваження",
        can_work_now=False,
        total_workers=total_workers,
        ready_workers=ready_workers,
        problem_workers=problem_workers,
        headline_text=f"Готові {ready_workers} з {total_workers} працівн.; є проблемні допуски.",
        issues_text=_build_issues_text(record.workers),
    )


def _count_ready_workers(workers: tuple[ContractorWorker, ...]) -> int:
    return sum(1 for worker in workers if _is_worker_ready(worker))


def _count_problem_workers(workers: tuple[ContractorWorker, ...]) -> int:
    return sum(1 for worker in workers if not _is_worker_ready(worker))


def _is_worker_ready(worker: ContractorWorker) -> bool:
    return worker.training_ok and worker.ppe_ok and worker.medical_ok and worker.access_ok


def _build_issues_text(workers: tuple[ContractorWorker, ...]) -> str:
    issue_lines: list[str] = []
    for worker in workers:
        missing_parts = []
        if not worker.training_ok:
            missing_parts.append("інструктаж")
        if not worker.ppe_ok:
            missing_parts.append("ЗІЗ")
        if not worker.medical_ok:
            missing_parts.append("медицина")
        if not worker.access_ok:
            missing_parts.append("допуск")
        if not missing_parts and not worker.note_text.strip():
            continue
        details = ", ".join(missing_parts) if missing_parts else "службова примітка"
        note_suffix = f"; {worker.note_text.strip()}" if worker.note_text.strip() else ""
        issue_lines.append(f"{worker.full_name}: {details}{note_suffix}")
    return " | ".join(issue_lines) if issue_lines else "Зауважень до складу підрядника не зафіксовано."
