"""Workflow execution via Claude CLI."""

import json
import re
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Optional


class WorkflowStatus(Enum):
    """Workflow execution status."""

    SUCCESS = "Success"
    ERROR = "Error"
    MAX_TURNS = "MaxTurns"
    PERMISSION_DENIED = "PermissionDenied"


@dataclass
class WorkflowResult:
    """Result of a workflow execution."""

    skill: str
    status: WorkflowStatus
    duration_seconds: float
    cost_usd: float
    turns_used: int
    max_turns: int
    session_id: str
    output: str
    errors: list[str]
    timestamp: datetime


# Default tools to allow during workflow execution
DEFAULT_ALLOWED_TOOLS = [
    "Skill",
    "Task",
    "TaskOutput",
    "Bash",
    "Read",
    "Glob",
    "Grep",
    "Edit",
    "Write",
    "TodoWrite",
    "WebSearch",
    "WebFetch",
]


def _find_claude_path() -> str:
    """Find the Claude CLI executable."""
    # Check common locations
    candidates = [
        Path.home() / ".local" / "bin" / "claude.exe",
        Path.home() / ".local" / "bin" / "claude",
        Path("claude.exe"),
        Path("claude"),
    ]

    for candidate in candidates:
        if candidate.exists():
            return str(candidate)

    # Fall back to hoping it's in PATH
    return "claude"


def _build_input_message(skill: str) -> str:
    """Build the stream-json input message."""
    message = {
        "type": "user",
        "message": {
            "role": "user",
            "content": f"Execute the {skill} skill now.",
        },
        "session_id": "default",
        "parent_tool_use_id": None,
    }
    return json.dumps(message)


def _parse_json_output(output: str) -> dict:
    """Parse JSON output from Claude CLI."""
    try:
        return json.loads(output.strip())
    except json.JSONDecodeError:
        return {}


def run_skill(
    skill: str,
    max_turns: int = 20,
    working_dir: Optional[Path] = None,
    allowed_tools: Optional[list[str]] = None,
    dry_run: bool = False,
) -> WorkflowResult:
    """
    Execute a skill via Claude CLI with stream-json.

    Args:
        skill: Name of the skill to execute (e.g., "validate-all")
        max_turns: Maximum conversation turns
        working_dir: Working directory for Claude (defaults to project root)
        allowed_tools: Tools to allow (defaults to DEFAULT_ALLOWED_TOOLS)
        dry_run: If True, just return what would be executed

    Returns:
        WorkflowResult with execution details
    """
    timestamp = datetime.now()

    if working_dir is None:
        # Default to project root (parent of tools/)
        working_dir = Path(__file__).parent.parent.parent

    if allowed_tools is None:
        allowed_tools = DEFAULT_ALLOWED_TOOLS

    claude_path = _find_claude_path()
    input_message = _build_input_message(skill)

    # Build the prompt to invoke the skill
    prompt = f"Execute the {skill} skill now."

    cmd = [
        claude_path,
        "-p", prompt,
        "--output-format", "json",
        "--max-turns", str(max_turns),
        "--allowedTools", ",".join(allowed_tools),
    ]

    if dry_run:
        return WorkflowResult(
            skill=skill,
            status=WorkflowStatus.SUCCESS,
            duration_seconds=0,
            cost_usd=0,
            turns_used=0,
            max_turns=max_turns,
            session_id="dry-run",
            output=f"Would execute: {' '.join(cmd)}\nWith input: {input_message}",
            errors=[],
            timestamp=timestamp,
        )

    start_time = datetime.now()

    try:
        # Run Claude
        process = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=str(working_dir),
            timeout=600,  # 10 minute timeout
        )

        duration = (datetime.now() - start_time).total_seconds()
        output = process.stdout
        stderr = process.stderr

        # Parse the result
        result_data = _parse_json_output(output)

        # Extract fields with defaults
        subtype = result_data.get("subtype", "unknown")
        session_id = result_data.get("session_id", "unknown")
        cost_usd = result_data.get("total_cost_usd", 0)
        num_turns = result_data.get("num_turns", 0)
        errors = result_data.get("errors", [])
        permission_denials = result_data.get("permission_denials", [])

        # Determine status
        if permission_denials:
            status = WorkflowStatus.PERMISSION_DENIED
            errors = [f"Permission denied: {d.get('tool_name')}" for d in permission_denials]
        elif subtype == "error_max_turns":
            status = WorkflowStatus.MAX_TURNS
        elif subtype == "success":
            status = WorkflowStatus.SUCCESS
        elif result_data.get("is_error"):
            status = WorkflowStatus.ERROR
        else:
            status = WorkflowStatus.SUCCESS

        # Extract result text if available
        result_text = result_data.get("result", "")
        if not result_text and stderr:
            result_text = stderr[:500]

        return WorkflowResult(
            skill=skill,
            status=status,
            duration_seconds=duration,
            cost_usd=cost_usd,
            turns_used=num_turns,
            max_turns=max_turns,
            session_id=session_id,
            output=result_text or f"Completed with status: {subtype}",
            errors=errors if isinstance(errors, list) else [str(errors)],
            timestamp=timestamp,
        )

    except subprocess.TimeoutExpired:
        duration = (datetime.now() - start_time).total_seconds()
        return WorkflowResult(
            skill=skill,
            status=WorkflowStatus.ERROR,
            duration_seconds=duration,
            cost_usd=0,
            turns_used=0,
            max_turns=max_turns,
            session_id="timeout",
            output="Execution timed out after 10 minutes",
            errors=["Timeout"],
            timestamp=timestamp,
        )

    except Exception as e:
        duration = (datetime.now() - start_time).total_seconds()
        return WorkflowResult(
            skill=skill,
            status=WorkflowStatus.ERROR,
            duration_seconds=duration,
            cost_usd=0,
            turns_used=0,
            max_turns=max_turns,
            session_id="error",
            output=str(e),
            errors=[str(e)],
            timestamp=timestamp,
        )


def log_execution(result: WorkflowResult, workflow_path: Path, max_entries: int = 10) -> None:
    """
    Append execution record to workflow.md, keeping only the last N entries.

    Args:
        result: The workflow result to log
        workflow_path: Path to workflow.md
        max_entries: Maximum number of recent executions to keep
    """
    if not workflow_path.exists():
        return

    content = workflow_path.read_text(encoding="utf-8")

    # Build the new entry
    timestamp_str = result.timestamp.strftime("%Y-%m-%d %H:%M")
    entry = f"""
### {timestamp_str} - {result.skill}
- **Status**: {result.status.value}
- **Duration**: {result.duration_seconds:.1f}s
- **Cost**: ${result.cost_usd:.4f}
- **Turns**: {result.turns_used}/{result.max_turns}
- **Output**: {result.output[:200] if result.output else "None"}
- **Session**: `{result.session_id}`
"""
    if result.errors:
        entry += f"- **Errors**: {', '.join(result.errors)}\n"

    # Find the Recent Executions section
    section_pattern = r"(## Recent Executions\n+)((?:### .+\n(?:- .+\n)*\n*)*)"
    match = re.search(section_pattern, content)

    if match:
        section_header = match.group(1)
        existing_entries = match.group(2)

        # Parse existing entries
        entry_pattern = r"(### \d{4}-\d{2}-\d{2} \d{2}:\d{2} - .+\n(?:- .+\n)*)"
        entries = re.findall(entry_pattern, existing_entries)

        # Add new entry at the beginning
        entries.insert(0, entry.strip() + "\n")

        # Keep only max_entries
        entries = entries[:max_entries]

        # Rebuild section
        new_section = section_header + "\n".join(entries) + "\n"

        # Replace in content
        content = content[:match.start()] + new_section + content[match.end():]
    else:
        # No section found - append at end
        content += f"\n## Recent Executions\n{entry}"

    workflow_path.write_text(content, encoding="utf-8")
