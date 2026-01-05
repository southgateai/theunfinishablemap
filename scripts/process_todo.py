#!/usr/bin/env python3
"""Process the todo queue: handle vetoes and get next task."""

import json
import sys
from pathlib import Path

import click
from rich.console import Console

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from tools.todo import process_vetoes, get_next_task, Task
from tools.todo.processor import process_todo_file

console = Console()

DEFAULT_TODO_PATH = Path(__file__).parent.parent / "obsidian" / "workflow" / "todo.md"


def task_to_dict(task: Task) -> dict:
    """Convert a Task to a JSON-serializable dict."""
    return {
        "title": task.title,
        "priority": task.priority,
        "type": task.task_type.value,
        "status": task.status.value,
        "notes": task.notes,
        "blocked_by": task.blocked_by,
    }


@click.group()
def cli() -> None:
    """Todo queue processing tools."""
    pass


@cli.command("process-vetoes")
@click.option(
    "--todo-file",
    type=click.Path(exists=True, path_type=Path),
    default=DEFAULT_TODO_PATH,
    help="Path to todo.md",
)
@click.option("--dry-run", is_flag=True, help="Don't modify file, just show what would happen")
def process_vetoes_cmd(todo_file: Path, dry_run: bool) -> None:
    """Process #veto tagged items, moving them to the Vetoed section."""
    content = todo_file.read_text(encoding="utf-8")
    new_content, vetoed = process_vetoes(content)

    if not vetoed:
        console.print("[dim]No vetoed items found[/dim]")
        return

    console.print(f"[bold]Found {len(vetoed)} vetoed item(s):[/bold]")
    for task in vetoed:
        console.print(f"  • P{task.priority}: {task.title}")

    if dry_run:
        console.print("\n[yellow]Dry run - file not modified[/yellow]")
    else:
        todo_file.write_text(new_content, encoding="utf-8")
        console.print("\n[green]Moved to Vetoed Tasks section[/green]")


@cli.command("next-task")
@click.option(
    "--todo-file",
    type=click.Path(exists=True, path_type=Path),
    default=DEFAULT_TODO_PATH,
    help="Path to todo.md",
)
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
@click.option("--process-vetoes", "do_vetoes", is_flag=True, help="Process vetoes first")
def next_task_cmd(todo_file: Path, as_json: bool, do_vetoes: bool) -> None:
    """Get the next task to execute."""
    content = todo_file.read_text(encoding="utf-8")

    if do_vetoes:
        new_content, vetoed = process_vetoes(content)
        if vetoed:
            todo_file.write_text(new_content, encoding="utf-8")
            if not as_json:
                console.print(f"[dim]Processed {len(vetoed)} vetoed item(s)[/dim]\n")
            content = new_content

    task = get_next_task(content)

    if task is None:
        if as_json:
            print(json.dumps({"task": None}))
        else:
            console.print("[yellow]No pending tasks[/yellow]")
        return

    if as_json:
        print(json.dumps({"task": task_to_dict(task)}))
    else:
        console.print(f"[bold]Next task:[/bold] P{task.priority}: {task.title}")
        console.print(f"  Type: {task.task_type.value}")
        if task.notes:
            console.print(f"  Notes: {task.notes}")


@cli.command("process")
@click.option(
    "--todo-file",
    type=click.Path(exists=True, path_type=Path),
    default=DEFAULT_TODO_PATH,
    help="Path to todo.md",
)
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
def process_cmd(todo_file: Path, as_json: bool) -> None:
    """Process vetoes and get next task in one step."""
    modified, vetoed, next_task = process_todo_file(todo_file)

    if as_json:
        result = {
            "modified": modified,
            "vetoed": [task_to_dict(t) for t in vetoed],
            "next_task": task_to_dict(next_task) if next_task else None,
        }
        print(json.dumps(result, indent=2))
    else:
        if vetoed:
            console.print(f"[bold]Processed {len(vetoed)} vetoed item(s):[/bold]")
            for task in vetoed:
                console.print(f"  ✗ P{task.priority}: {task.title}")
            console.print()

        if next_task:
            console.print(f"[bold]Next task:[/bold] P{next_task.priority}: {next_task.title}")
            console.print(f"  Type: {next_task.task_type.value}")
            if next_task.notes:
                console.print(f"  Notes: {next_task.notes}")
        else:
            console.print("[yellow]No pending tasks[/yellow]")


def main() -> None:
    """Entry point."""
    cli()


if __name__ == "__main__":
    main()
