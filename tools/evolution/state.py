"""Evolution state management - dataclasses and I/O for evolution-state.yaml."""

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional

import yaml


@dataclass
class ContentStats:
    """Statistics about site content."""

    total_files: int = 0
    published_files: int = 0
    draft_files: int = 0
    placeholder_files: int = 0


@dataclass
class ConvergenceTargets:
    """What 'done' looks like."""

    min_topics: int = 10
    min_concepts: int = 15
    min_arguments: int = 5
    max_critical_issues: int = 0
    max_medium_issues: int = 3


@dataclass
class Progress:
    """Current progress toward convergence."""

    topics_written: int = 0
    concepts_written: int = 0
    arguments_written: int = 0
    questions_written: int = 0
    voids_written: int = 0
    research_notes: int = 0
    reviews_completed: int = 0


@dataclass
class Quality:
    """Quality metrics from last review."""

    critical_issues: int = 0
    medium_issues: int = 0
    low_issues: int = 0
    orphaned_files: int = 0


@dataclass
class TaskRecord:
    """Record of a completed task."""

    task: str
    task_type: str
    date: str
    outcome: str  # success, failed, partial
    duration_minutes: Optional[float] = None
    issues_found: Optional[int] = None


@dataclass
class EvolutionState:
    """Complete evolution state."""

    last_updated: datetime
    session_count: int
    last_runs: dict[str, Optional[datetime]]
    cadences: dict[str, int]
    overdue_thresholds: dict[str, int]
    scheduled_hours: dict[str, int]  # task -> hour (0-23 UTC) when task should run
    last_git_push: Optional[datetime]  # for rate-limiting pushes across processes
    content_stats: ContentStats
    convergence_targets: ConvergenceTargets
    progress: Progress
    quality: Quality
    failed_tasks: dict[str, int]  # task_title -> retry_count
    recent_tasks: list[TaskRecord] = field(default_factory=list)


def load_state(path: Path) -> EvolutionState:
    """Load evolution state from YAML file."""
    with open(path, encoding="utf-8") as f:
        data = yaml.safe_load(f)

    # Parse last_runs timestamps
    last_runs = {}
    for key, value in data.get("last_runs", {}).items():
        if value is None:
            last_runs[key] = None
        elif isinstance(value, datetime):
            last_runs[key] = value
        else:
            last_runs[key] = datetime.fromisoformat(str(value))

    # Parse last_updated
    last_updated = data.get("last_updated")
    if isinstance(last_updated, str):
        last_updated = datetime.fromisoformat(last_updated)
    elif last_updated is None:
        last_updated = datetime.now()

    # Parse last_git_push
    last_git_push = data.get("last_git_push")
    if isinstance(last_git_push, str):
        last_git_push = datetime.fromisoformat(last_git_push)
    elif isinstance(last_git_push, datetime):
        pass  # already datetime
    else:
        last_git_push = None

    # Parse recent_tasks
    recent_tasks = []
    for task_data in data.get("recent_tasks", []):
        recent_tasks.append(
            TaskRecord(
                task=task_data.get("task", ""),
                task_type=task_data.get("type", ""),
                date=task_data.get("date", ""),
                outcome=task_data.get("outcome", ""),
                duration_minutes=task_data.get("duration_minutes"),
                issues_found=task_data.get("issues_found"),
            )
        )

    return EvolutionState(
        last_updated=last_updated,
        session_count=data.get("session_count", 0),
        last_runs=last_runs,
        cadences=data.get("cadences", {}),
        overdue_thresholds=data.get("overdue_thresholds", {}),
        scheduled_hours=data.get("scheduled_hours", {}),
        last_git_push=last_git_push,
        content_stats=ContentStats(**data.get("content_stats", {})),
        convergence_targets=ConvergenceTargets(**data.get("convergence_targets", {})),
        progress=Progress(**data.get("progress", {})),
        quality=Quality(**data.get("quality", {})),
        failed_tasks=data.get("failed_tasks", {}),
        recent_tasks=recent_tasks,
    )


def save_state(state: EvolutionState, path: Path) -> None:
    """Save evolution state to YAML file."""
    # Convert last_runs to serializable format
    last_runs = {}
    for key, value in state.last_runs.items():
        if value is None:
            last_runs[key] = None
        else:
            last_runs[key] = value.isoformat()

    # Convert recent_tasks to dicts
    recent_tasks = []
    for task in state.recent_tasks[-20:]:  # Keep last 20 tasks
        task_dict = {
            "task": task.task,
            "type": task.task_type,
            "date": task.date,
            "outcome": task.outcome,
        }
        if task.duration_minutes is not None:
            task_dict["duration_minutes"] = task.duration_minutes
        if task.issues_found is not None:
            task_dict["issues_found"] = task.issues_found
        recent_tasks.append(task_dict)

    data = {
        "last_updated": state.last_updated.isoformat(),
        "session_count": state.session_count,
        "last_runs": last_runs,
        "cadences": state.cadences,
        "overdue_thresholds": state.overdue_thresholds,
        "scheduled_hours": state.scheduled_hours,
        "last_git_push": state.last_git_push.isoformat() if state.last_git_push else None,
        "content_stats": {
            "total_files": state.content_stats.total_files,
            "published_files": state.content_stats.published_files,
            "draft_files": state.content_stats.draft_files,
            "placeholder_files": state.content_stats.placeholder_files,
        },
        "convergence_targets": {
            "min_topics": state.convergence_targets.min_topics,
            "min_concepts": state.convergence_targets.min_concepts,
            "min_arguments": state.convergence_targets.min_arguments,
            "max_critical_issues": state.convergence_targets.max_critical_issues,
            "max_medium_issues": state.convergence_targets.max_medium_issues,
        },
        "progress": {
            "topics_written": state.progress.topics_written,
            "concepts_written": state.progress.concepts_written,
            "arguments_written": state.progress.arguments_written,
            "questions_written": state.progress.questions_written,
            "voids_written": state.progress.voids_written,
            "research_notes": state.progress.research_notes,
            "reviews_completed": state.progress.reviews_completed,
        },
        "quality": {
            "critical_issues": state.quality.critical_issues,
            "medium_issues": state.quality.medium_issues,
            "low_issues": state.quality.low_issues,
            "orphaned_files": state.quality.orphaned_files,
        },
        "failed_tasks": state.failed_tasks,
        "recent_tasks": recent_tasks,
    }

    # Write with header comment
    header = """# Evolution State
# Machine-readable tracking for the automatic site evolution system
# Updated by /evolve skill after each session

"""
    with open(path, "w", encoding="utf-8") as f:
        f.write(header)
        yaml.dump(data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)


def calculate_convergence(state: EvolutionState) -> float:
    """
    Calculate convergence score (0.0 to 1.0).

    Measures how close the site is to being "complete" based on:
    - Content breadth (topics, concepts, arguments written)
    - Quality (issues from reviews)
    - Completeness (no placeholders)
    """
    targets = state.convergence_targets
    progress = state.progress

    # Content breadth (50% weight)
    topic_ratio = min(progress.topics_written / max(targets.min_topics, 1), 1.0)
    concept_ratio = min(progress.concepts_written / max(targets.min_concepts, 1), 1.0)
    argument_ratio = min(progress.arguments_written / max(targets.min_arguments, 1), 1.0)
    breadth_score = (topic_ratio + concept_ratio + argument_ratio) / 3

    # Quality (30% weight)
    critical_penalty = min(state.quality.critical_issues * 0.2, 1.0)
    medium_penalty = min(state.quality.medium_issues * 0.05, 0.3)
    quality_score = max(0, 1 - critical_penalty - medium_penalty)

    # Completeness (20% weight)
    total = max(state.content_stats.total_files, 1)
    placeholder_ratio = state.content_stats.placeholder_files / total
    completeness_score = 1 - placeholder_ratio

    # Weighted sum
    return 0.5 * breadth_score + 0.3 * quality_score + 0.2 * completeness_score
