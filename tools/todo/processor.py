"""Todo queue parsing and processing."""

import re
from dataclasses import dataclass, field
from datetime import date
from enum import Enum
from pathlib import Path
from typing import Optional


class TaskStatus(Enum):
    """Task status values."""

    PENDING = "pending"
    IN_PROGRESS = "in-progress"
    BLOCKED = "blocked"
    FAILED = "failed"
    COMPLETED = "completed"
    VETOED = "vetoed"


class TaskType(Enum):
    """Known task types."""

    EXPAND_TOPIC = "expand-topic"
    RESEARCH_TOPIC = "research-topic"
    REFINE_DRAFT = "refine-draft"
    VALIDATE_ALL = "validate-all"
    CHECK_TENETS = "check-tenets"
    PESSIMISTIC_REVIEW = "pessimistic-review"
    OPTIMISTIC_REVIEW = "optimistic-review"
    OTHER = "other"


@dataclass
class Task:
    """A parsed task from the todo queue."""

    title: str
    priority: int  # 0-3
    task_type: TaskType
    status: TaskStatus
    notes: str = ""
    blocked_by: Optional[str] = None
    raw_block: str = ""  # Original markdown block
    line_number: int = 0  # For ordering


# Regex patterns
TASK_HEADING_PATTERN = re.compile(
    r"^###\s+P([0-3]):\s+(.+?)(?:\s+#veto)?\s*$", re.IGNORECASE
)
VETO_TAG_PATTERN = re.compile(r"\s*#veto\b", re.IGNORECASE)
COMPLETED_HEADING_PATTERN = re.compile(r"^###\s+[✓✗]\s+[\d-]+:\s+(.+)$")


def _parse_task_block(heading: str, body_lines: list[str], line_number: int) -> Optional[Task]:
    """Parse a single task block into a Task object."""
    # Check for veto tag
    has_veto = bool(VETO_TAG_PATTERN.search(heading))

    # Match the heading
    match = TASK_HEADING_PATTERN.match(heading)
    if not match:
        return None

    priority = int(match.group(1))
    title = match.group(2).strip()

    # Remove veto tag from title if present
    title = VETO_TAG_PATTERN.sub("", title).strip()

    # Parse body fields
    task_type = TaskType.OTHER
    status = TaskStatus.VETOED if has_veto else TaskStatus.PENDING
    notes = ""
    blocked_by = None

    for line in body_lines:
        line = line.strip()
        if line.startswith("- **Type**:"):
            type_str = line.split(":", 1)[1].strip().lower()
            try:
                task_type = TaskType(type_str)
            except ValueError:
                task_type = TaskType.OTHER
        elif line.startswith("- **Status**:"):
            status_str = line.split(":", 1)[1].strip().lower()
            if has_veto:
                status = TaskStatus.VETOED
            else:
                try:
                    status = TaskStatus(status_str)
                except ValueError:
                    status = TaskStatus.PENDING
        elif line.startswith("- **Notes**:"):
            notes = line.split(":", 1)[1].strip()
        elif line.startswith("- **Blocked-by**:"):
            blocked_by = line.split(":", 1)[1].strip()

    # Reconstruct raw block
    raw_block = heading + "\n" + "\n".join(body_lines)

    return Task(
        title=title,
        priority=priority,
        task_type=task_type,
        status=status,
        notes=notes,
        blocked_by=blocked_by,
        raw_block=raw_block,
        line_number=line_number,
    )


def parse_tasks(content: str) -> dict:
    """
    Parse todo.md content into structured data.

    Returns:
        Dict with 'active', 'completed', 'vetoed' task lists and 'sections' dict
    """
    lines = content.split("\n")
    result = {
        "active": [],
        "completed": [],
        "vetoed": [],
        "preamble": [],  # Content before Active Tasks
        "sections": {},  # Section name -> line ranges
    }

    current_section = "preamble"
    section_start = 0
    current_task_heading = None
    current_task_body: list[str] = []
    current_task_line = 0

    for i, line in enumerate(lines):
        # Check for section headers
        if line.startswith("## Active Tasks"):
            result["sections"]["preamble"] = (0, i)
            current_section = "active"
            section_start = i
            continue
        elif line.startswith("## Completed Tasks"):
            result["sections"]["active"] = (section_start, i)
            current_section = "completed"
            section_start = i
            continue
        elif line.startswith("## Vetoed Tasks"):
            result["sections"]["completed"] = (section_start, i)
            current_section = "vetoed"
            section_start = i
            continue

        # Handle preamble
        if current_section == "preamble":
            result["preamble"].append(line)
            continue

        # Check for task headings (### P0-3: ...)
        if line.startswith("### "):
            # Save previous task if any
            if current_task_heading and current_section == "active":
                task = _parse_task_block(
                    current_task_heading, current_task_body, current_task_line
                )
                if task:
                    if task.status == TaskStatus.VETOED:
                        result["vetoed"].append(task)
                    else:
                        result["active"].append(task)

            # Start new task
            if TASK_HEADING_PATTERN.match(line) or VETO_TAG_PATTERN.search(line):
                current_task_heading = line
                current_task_body = []
                current_task_line = i
            else:
                # Completed task heading or other
                current_task_heading = None
                current_task_body = []
        elif current_task_heading:
            current_task_body.append(line)

    # Don't forget the last task
    if current_task_heading and current_section == "active":
        task = _parse_task_block(
            current_task_heading, current_task_body, current_task_line
        )
        if task:
            if task.status == TaskStatus.VETOED:
                result["vetoed"].append(task)
            else:
                result["active"].append(task)

    # Record final section
    result["sections"][current_section] = (section_start, len(lines))

    return result


def process_vetoes(content: str) -> tuple[str, list[Task]]:
    """
    Find tasks tagged with #veto, move them to Vetoed Tasks section.

    Args:
        content: The todo.md file content

    Returns:
        Tuple of (updated content, list of vetoed tasks)
    """
    lines = content.split("\n")
    vetoed_tasks: list[Task] = []
    lines_to_remove: set[int] = set()

    # Find all vetoed tasks
    current_task_start = None
    current_task_heading = None
    current_task_body: list[str] = []
    in_active_section = False

    for i, line in enumerate(lines):
        if line.startswith("## Active Tasks"):
            in_active_section = True
            continue
        elif line.startswith("## Completed Tasks") or line.startswith("## Vetoed Tasks"):
            # Save any pending task before leaving active section
            if current_task_heading and VETO_TAG_PATTERN.search(current_task_heading):
                task = _parse_task_block(
                    current_task_heading, current_task_body, current_task_start
                )
                if task:
                    vetoed_tasks.append(task)
                    for j in range(current_task_start, i):
                        lines_to_remove.add(j)
            in_active_section = False
            current_task_heading = None
            continue

        if not in_active_section:
            continue

        # Check for task headings
        if line.startswith("### P"):
            # Save previous vetoed task
            if current_task_heading and VETO_TAG_PATTERN.search(current_task_heading):
                task = _parse_task_block(
                    current_task_heading, current_task_body, current_task_start
                )
                if task:
                    vetoed_tasks.append(task)
                    for j in range(current_task_start, i):
                        lines_to_remove.add(j)

            current_task_start = i
            current_task_heading = line
            current_task_body = []
        elif current_task_heading:
            current_task_body.append(line)

    if not vetoed_tasks:
        return content, []

    # Remove vetoed task lines
    new_lines = [line for i, line in enumerate(lines) if i not in lines_to_remove]

    # Clean up multiple blank lines
    cleaned_lines = []
    prev_blank = False
    for line in new_lines:
        is_blank = line.strip() == ""
        if is_blank and prev_blank:
            continue
        cleaned_lines.append(line)
        prev_blank = is_blank

    # Find or create Vetoed Tasks section
    vetoed_section_idx = None
    for i, line in enumerate(cleaned_lines):
        if line.startswith("## Vetoed Tasks"):
            vetoed_section_idx = i
            break

    today = date.today().isoformat()

    # Build vetoed task entries
    vetoed_entries = []
    for task in vetoed_tasks:
        entry_lines = [
            f"### {task.title}",
            f"- **Vetoed**: {today}",
            f"- **Original priority**: P{task.priority}",
            f"- **Type**: {task.task_type.value}",
        ]
        if task.notes:
            entry_lines.append(f"- **Notes**: {task.notes}")
        vetoed_entries.append("\n".join(entry_lines))

    vetoed_block = "\n\n".join(vetoed_entries)

    if vetoed_section_idx is not None:
        # Insert after section header
        insert_idx = vetoed_section_idx + 1
        # Skip any description text until next heading or end
        while insert_idx < len(cleaned_lines) and not cleaned_lines[insert_idx].startswith("###"):
            if cleaned_lines[insert_idx].strip() == "":
                insert_idx += 1
                break
            insert_idx += 1

        cleaned_lines.insert(insert_idx, "\n" + vetoed_block + "\n")
    else:
        # Create new section at end
        cleaned_lines.append("")
        cleaned_lines.append("## Vetoed Tasks")
        cleaned_lines.append("")
        cleaned_lines.append("Ideas that were considered and rejected. The AI will not re-propose these.")
        cleaned_lines.append("")
        cleaned_lines.append(vetoed_block)

    return "\n".join(cleaned_lines), vetoed_tasks


def get_next_task(content: str) -> Optional[Task]:
    """
    Get the highest priority pending task.

    Priority order: P0 > P1 > P2 > P3
    Within same priority: first in file (oldest)

    Skips:
    - Tasks with status: in-progress, blocked, failed, vetoed
    - Tasks with unmet blocked-by dependencies
    """
    parsed = parse_tasks(content)

    # Filter to pending tasks only
    pending = [
        t for t in parsed["active"]
        if t.status == TaskStatus.PENDING and not t.blocked_by
    ]

    if not pending:
        return None

    # Sort by priority (ascending) then by line number (ascending)
    pending.sort(key=lambda t: (t.priority, t.line_number))

    return pending[0]


def process_todo_file(todo_path: Path) -> tuple[bool, list[Task], Optional[Task]]:
    """
    Process a todo.md file: handle vetoes and find next task.

    Args:
        todo_path: Path to todo.md

    Returns:
        Tuple of (file_was_modified, vetoed_tasks, next_task)
    """
    content = todo_path.read_text(encoding="utf-8")

    # Process vetoes
    new_content, vetoed = process_vetoes(content)
    modified = new_content != content

    if modified:
        todo_path.write_text(new_content, encoding="utf-8")

    # Get next task from updated content
    next_task = get_next_task(new_content)

    return modified, vetoed, next_task
