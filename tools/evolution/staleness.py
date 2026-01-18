"""Staleness detection for maintenance tasks."""

from datetime import datetime, timezone
from typing import Optional

from .state import EvolutionState
from .scoring import ScoredTask, score_synthetic_task


def is_scheduled_hour(
    skill_name: str,
    state: EvolutionState,
    now: Optional[datetime] = None,
) -> bool:
    """
    Check if current hour matches or is past the scheduled hour for a task.

    Tasks with scheduled_hours only run at/after their designated hour each day.

    Args:
        skill_name: Name of the skill to check
        state: Current evolution state
        now: Current time (defaults to now)

    Returns:
        True if no scheduled hour constraint, or if current hour >= scheduled hour
    """
    scheduled_hour = state.scheduled_hours.get(skill_name)
    if scheduled_hour is None:
        return True  # No constraint

    if now is None:
        now = datetime.now(timezone.utc)

    # Ensure timezone awareness
    if now.tzinfo is None:
        now = now.replace(tzinfo=timezone.utc)

    return now.hour >= scheduled_hour


def check_staleness(
    skill_name: str,
    state: EvolutionState,
    now: Optional[datetime] = None,
) -> tuple[bool, int]:
    """
    Check if a maintenance task is overdue.

    Args:
        skill_name: Name of the skill to check
        state: Current evolution state
        now: Current time (defaults to now)

    Returns:
        Tuple of (is_overdue, hours_overdue)
    """
    if now is None:
        now = datetime.now(timezone.utc)

    # Get last run time
    last_run = state.last_runs.get(skill_name)
    if last_run is None:
        # Never run - consider it very overdue (720 hours = 30 days)
        return True, 720

    # Ensure timezone awareness
    if last_run.tzinfo is None:
        last_run = last_run.replace(tzinfo=timezone.utc)
    if now.tzinfo is None:
        now = now.replace(tzinfo=timezone.utc)

    # Get cadence (in hours)
    cadence_hours = state.cadences.get(skill_name, 168)  # default 7 days = 168 hours

    # Calculate hours since last run
    hours_since = int((now - last_run).total_seconds() / 3600)

    # Check against cadence
    hours_overdue = hours_since - cadence_hours

    return hours_overdue > 0, max(0, hours_overdue)


def get_overdue_tasks(
    state: EvolutionState,
    now: Optional[datetime] = None,
) -> list[ScoredTask]:
    """
    Get all overdue maintenance tasks as synthetic scored tasks.

    Only returns tasks that exceed their overdue threshold (not just past cadence).
    Tasks with scheduled_hours constraints only appear if current hour >= scheduled hour.

    Args:
        state: Current evolution state
        now: Current time (defaults to now)

    Returns:
        List of ScoredTask for overdue maintenance tasks
    """
    if now is None:
        now = datetime.now(timezone.utc)

    overdue_tasks: list[ScoredTask] = []

    # Check each maintenance task
    maintenance_skills = [
        "validate-all",
        "pessimistic-review",
        "optimistic-review",
        "check-tenets",
        "check-links",
        "deep-review",
        "tweet-highlight",
    ]

    for skill_name in maintenance_skills:
        # Check scheduled hour constraint (e.g., tweet-highlight only at/after 7am UTC)
        if not is_scheduled_hour(skill_name, state, now):
            continue

        is_overdue, hours_overdue = check_staleness(skill_name, state, now)

        if not is_overdue:
            continue

        # Check against overdue threshold (not just cadence)
        threshold = state.overdue_thresholds.get(skill_name, 72)  # default 3 days = 72 hours
        if hours_overdue < threshold:
            continue

        # Create synthetic task
        scored = score_synthetic_task(skill_name, hours_overdue, state)
        overdue_tasks.append(scored)

    return overdue_tasks


def get_status_report(state: EvolutionState, now: Optional[datetime] = None) -> str:
    """
    Generate a human-readable staleness status report.

    Args:
        state: Current evolution state
        now: Current time (defaults to now)

    Returns:
        Markdown-formatted status report
    """
    if now is None:
        now = datetime.now(timezone.utc)

    lines = ["## Maintenance Status", ""]
    lines.append("| Task | Last Run | Cadence | Status |")
    lines.append("|------|----------|---------|--------|")

    maintenance_skills = [
        "validate-all",
        "pessimistic-review",
        "optimistic-review",
        "check-tenets",
        "check-links",
        "deep-review",
        "tweet-highlight",
    ]

    for skill_name in maintenance_skills:
        last_run = state.last_runs.get(skill_name)
        cadence = state.cadences.get(skill_name, 168)  # default 7 days = 168 hours
        scheduled_hour = state.scheduled_hours.get(skill_name)

        if last_run is None:
            last_run_str = "Never"
            status = "OVERDUE"
        else:
            # Ensure timezone awareness
            if last_run.tzinfo is None:
                last_run = last_run.replace(tzinfo=timezone.utc)
            if now.tzinfo is None:
                now = now.replace(tzinfo=timezone.utc)

            hours_ago = int((now - last_run).total_seconds() / 3600)
            last_run_str = f"{hours_ago}h ago"

            is_overdue, hours_overdue = check_staleness(skill_name, state, now)
            threshold = state.overdue_thresholds.get(skill_name, 72)  # default 3 days = 72 hours

            if hours_overdue >= threshold:
                status = f"OVERDUE ({hours_overdue}h)"
            elif is_overdue:
                status = f"Due ({hours_overdue}h)"
            else:
                status = "OK"

        # Add scheduled hour info if present
        cadence_str = f"{cadence}h"
        if scheduled_hour is not None:
            cadence_str += f" @{scheduled_hour:02d}:00"

        lines.append(f"| {skill_name} | {last_run_str} | {cadence_str} | {status} |")

    return "\n".join(lines)
