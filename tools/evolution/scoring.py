"""Task scoring algorithm for intelligent task selection."""

from dataclasses import dataclass
from typing import Optional

from tools.todo.processor import Task, TaskStatus
from .state import EvolutionState


@dataclass
class ScoredTask:
    """A task with its computed score and breakdown."""

    task: Task
    base_priority_score: int
    staleness_bonus: int
    urgency_modifier: int
    dependency_bonus: int
    failure_penalty: int
    total_score: int
    is_synthetic: bool = False  # True for auto-injected maintenance tasks
    reason: str = ""  # Why this score


def score_task(
    task: Task,
    state: EvolutionState,
    has_research: bool = False,
    addresses_critical: bool = False,
    addresses_medium: bool = False,
    unlocks_count: int = 0,
) -> ScoredTask:
    """
    Score a task based on multiple factors.

    Score formula:
        SCORE = PRIORITY_BASE + STALENESS_BONUS + URGENCY_MOD + DEPENDENCY_BONUS - FAILURE_PENALTY

    Args:
        task: The task to score
        state: Current evolution state
        has_research: Whether research exists for this topic
        addresses_critical: Whether this task addresses a critical review issue
        addresses_medium: Whether this task addresses a medium review issue
        unlocks_count: How many other tasks this would unblock

    Returns:
        ScoredTask with breakdown of score components
    """
    # Base priority score: P0=400, P1=300, P2=200, P3=100
    base_priority_score = (4 - task.priority) * 100

    # Staleness bonus: not applicable to queue tasks (only synthetic maintenance tasks)
    staleness_bonus = 0

    # Urgency modifier
    urgency_modifier = 0
    urgency_reasons = []

    if addresses_critical:
        urgency_modifier += 50
        urgency_reasons.append("+50 critical issue")
    if addresses_medium:
        urgency_modifier += 30
        urgency_reasons.append("+30 medium issue")
    if has_research:
        urgency_modifier += 20
        urgency_reasons.append("+20 has research")

    # Dependency bonus: tasks that unlock others are more valuable
    dependency_bonus = 0
    if unlocks_count > 0:
        dependency_bonus = 40 + min(unlocks_count - 1, 3) * 10  # 40 base + 10 per additional
        urgency_reasons.append(f"+{dependency_bonus} unlocks {unlocks_count} tasks")

    # Failure penalty: -100 per failure, -500 at 3+ failures (effectively blocked)
    failure_count = state.failed_tasks.get(task.title, 0)
    if failure_count >= 3:
        failure_penalty = 500
        urgency_reasons.append(f"-500 blocked ({failure_count} failures)")
    else:
        failure_penalty = failure_count * 100
        if failure_penalty > 0:
            urgency_reasons.append(f"-{failure_penalty} ({failure_count} failures)")

    total_score = (
        base_priority_score
        + staleness_bonus
        + urgency_modifier
        + dependency_bonus
        - failure_penalty
    )

    reason = f"P{task.priority}={base_priority_score}"
    if urgency_reasons:
        reason += " " + " ".join(urgency_reasons)

    return ScoredTask(
        task=task,
        base_priority_score=base_priority_score,
        staleness_bonus=staleness_bonus,
        urgency_modifier=urgency_modifier,
        dependency_bonus=dependency_bonus,
        failure_penalty=failure_penalty,
        total_score=total_score,
        is_synthetic=False,
        reason=reason,
    )


def create_synthetic_task(
    skill_name: str,
    hours_overdue: int,
    priority: int = 2,
) -> tuple[Task, int]:
    """
    Create a synthetic task for an overdue maintenance skill.

    Args:
        skill_name: Name of the skill (e.g., 'pessimistic-review')
        hours_overdue: How many hours past due
        priority: Base priority (default P2)

    Returns:
        Tuple of (Task, staleness_bonus)
    """
    from tools.todo.processor import TaskType

    # Map skill names to task types
    type_map = {
        "validate-all": TaskType.VALIDATE_ALL,
        "pessimistic-review": TaskType.PESSIMISTIC_REVIEW,
        "optimistic-review": TaskType.OPTIMISTIC_REVIEW,
        "check-tenets": TaskType.CHECK_TENETS,
        "deep-review": TaskType.DEEP_REVIEW,
    }

    task_type = type_map.get(skill_name, TaskType.OTHER)

    task = Task(
        title=f"Run {skill_name} (overdue by {hours_overdue}h)",
        priority=priority,
        task_type=task_type,
        status=TaskStatus.PENDING,
        notes=f"Auto-generated: maintenance task overdue",
        blocked_by=None,
        raw_block="",
        line_number=-1,  # Synthetic tasks sort after real ones at same score
    )

    # Staleness bonus: 1 point per hour overdue (20 per day), capped at 150
    staleness_bonus = min(hours_overdue, 150)

    return task, staleness_bonus


def score_synthetic_task(
    skill_name: str,
    hours_overdue: int,
    state: EvolutionState,
) -> ScoredTask:
    """
    Score a synthetic maintenance task.

    Args:
        skill_name: Name of the skill
        hours_overdue: How many hours past due
        state: Current evolution state

    Returns:
        ScoredTask for the synthetic task
    """
    task, staleness_bonus = create_synthetic_task(skill_name, hours_overdue)

    # Base priority score (synthetic tasks are P2 by default)
    base_priority_score = (4 - task.priority) * 100

    total_score = base_priority_score + staleness_bonus

    return ScoredTask(
        task=task,
        base_priority_score=base_priority_score,
        staleness_bonus=staleness_bonus,
        urgency_modifier=0,
        dependency_bonus=0,
        failure_penalty=0,
        total_score=total_score,
        is_synthetic=True,
        reason=f"P{task.priority}={base_priority_score} +{staleness_bonus} overdue",
    )


def get_ranked_tasks(
    tasks: list[Task],
    state: EvolutionState,
    synthetic_tasks: Optional[list[ScoredTask]] = None,
) -> list[ScoredTask]:
    """
    Score and rank all tasks (queue + synthetic).

    Args:
        tasks: Active tasks from todo.md (pending status only)
        state: Current evolution state
        synthetic_tasks: Pre-scored synthetic maintenance tasks

    Returns:
        List of ScoredTasks sorted by total_score descending
    """
    scored: list[ScoredTask] = []

    # Score queue tasks
    for task in tasks:
        if task.status != TaskStatus.PENDING:
            continue

        # Skip tasks blocked by 3+ failures (they go to Blocked section)
        failure_count = state.failed_tasks.get(task.title, 0)
        if failure_count >= 3:
            continue

        scored_task = score_task(task, state)
        scored.append(scored_task)

    # Add synthetic tasks
    if synthetic_tasks:
        scored.extend(synthetic_tasks)

    # Sort by score descending, then by line number ascending (for ties)
    scored.sort(key=lambda s: (-s.total_score, s.task.line_number))

    return scored
