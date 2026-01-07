#!/usr/bin/env python3
"""Commit obsidian changes with appropriate authorship.

Compares 'human_modified' vs 'ai_modified' timestamps to determine
whether to attribute changes to human or AI author.
"""

import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

import click
import frontmatter
from rich.console import Console

console = Console()

# AI author for commits
AI_AUTHOR = "unfinishablemap.org Agent <agent@unfinishablemap.org>"


def parse_timestamp(value: Optional[str]) -> Optional[datetime]:
    """Parse an ISO timestamp from frontmatter."""
    if not value:
        return None

    # Handle various ISO formats
    if isinstance(value, datetime):
        return value

    try:
        # Try parsing with timezone
        if "T" in str(value):
            # ISO format with time
            return datetime.fromisoformat(str(value))
        else:
            # Date only format
            return datetime.fromisoformat(f"{value}T00:00:00")
    except (ValueError, TypeError):
        return None


def get_changed_files(obsidian_path: Path) -> list[Path]:
    """Get list of changed markdown files in obsidian directory."""
    # Use -uall to show individual files in untracked directories
    result = subprocess.run(
        ["git", "status", "--porcelain", "-uall", str(obsidian_path)],
        capture_output=True,
        text=True,
    )

    # Regex to parse git status --porcelain output
    # Format: XY PATH or XY "PATH" or XY PATH -> NEWPATH
    # X = index status, Y = work tree status
    # Examples:
    #   M  file.txt           (staged modification)
    #    M file.txt           (unstaged modification)
    #   ?? file.txt           (untracked)
    #   R  old.txt -> new.txt (rename)
    #   A  "path with spaces.txt"
    status_pattern = re.compile(
        r'^(?P<status>[MADRCU?! ]{2})\s+'  # XY status + whitespace
        r'(?:"(?P<quoted_path>[^"]+)"|(?P<path>\S+))'  # quoted or unquoted path
        r'(?:\s+->\s+(?:"(?P<quoted_new>[^"]+)"|(?P<new_path>\S+)))?$'  # optional rename target
    )

    files = []
    for line in result.stdout.splitlines():
        if not line.strip():
            continue

        match = status_pattern.match(line)
        if not match:
            # Fallback for unexpected formats
            console.print(f"  [yellow]Warning: Could not parse git status line: {line!r}[/yellow]")
            continue

        status = match.group("status")
        # For renames, use the new path; otherwise use the regular path
        filepath = (
            match.group("quoted_new")
            or match.group("new_path")
            or match.group("quoted_path")
            or match.group("path")
        )

        path = Path(filepath)

        # Only include markdown files, exclude templates
        if path.suffix == ".md" and "templates" not in path.parts:
            # Check if file exists (not deleted)
            if "D" not in status:
                files.append(path)

    return files


def determine_author(file_path: Path) -> str:
    """Determine if a file was last modified by human or AI.

    Returns 'human' or 'ai'.
    """
    try:
        post = frontmatter.load(file_path)
    except Exception:
        # If we can't parse, default to human
        return "human"

    human_modified = parse_timestamp(post.get("human_modified"))
    ai_modified = parse_timestamp(post.get("ai_modified"))

    # Decision logic:
    # - If both missing: human (conservative)
    # - If only human_modified: human
    # - If only ai_modified: ai
    # - If both present: most recent wins, tie goes to human

    if not human_modified and not ai_modified:
        return "human"

    if human_modified and not ai_modified:
        return "human"

    if ai_modified and not human_modified:
        return "ai"

    # Both present - compare
    if ai_modified > human_modified:
        return "ai"
    else:
        return "human"


def commit_files(
    files: list[Path],
    author: Optional[str],
    message: str,
    dry_run: bool = False,
) -> bool:
    """Stage and commit files with optional author override."""
    if not files:
        return True

    # Stage files
    stage_cmd = ["git", "add"] + [str(f) for f in files]

    if dry_run:
        console.print(f"  [dim]Would run: {' '.join(stage_cmd)}[/dim]")
    else:
        result = subprocess.run(stage_cmd, capture_output=True, text=True)
        if result.returncode != 0:
            console.print(f"  [red]Failed to stage files:[/red] {result.stderr}")
            return False

    # Commit
    commit_cmd = ["git", "commit", "-m", message]
    if author:
        commit_cmd.extend(["--author", author])

    if dry_run:
        console.print(f"  [dim]Would run: {' '.join(commit_cmd)}[/dim]")
    else:
        result = subprocess.run(commit_cmd, capture_output=True, text=True)
        if result.returncode != 0:
            # Check if it's just "nothing to commit"
            if "nothing to commit" in result.stdout or "nothing to commit" in result.stderr:
                console.print("  [dim]Nothing to commit[/dim]")
                return True
            console.print(f"  [red]Failed to commit:[/red] {result.stderr}")
            return False

    return True


@click.command()
@click.option(
    "--obsidian",
    "-o",
    type=click.Path(exists=True, path_type=Path),
    default="obsidian",
    help="Path to Obsidian vault",
)
@click.option(
    "--dry-run",
    "-n",
    is_flag=True,
    help="Show what would be committed without making changes",
)
@click.option(
    "--message",
    "-m",
    default=None,
    help="Custom commit message (otherwise auto-generated)",
)
def main(obsidian: Path, dry_run: bool, message: Optional[str]) -> None:
    """Commit obsidian changes with appropriate authorship."""
    console.print("[bold blue]Obsidian Commit[/bold blue]\n")

    # Get changed files
    changed_files = get_changed_files(obsidian)

    if not changed_files:
        console.print("[dim]No changed files in obsidian directory[/dim]")
        return

    console.print(f"Found {len(changed_files)} changed file(s)\n")

    # Group by author
    human_files: list[Path] = []
    ai_files: list[Path] = []

    for f in changed_files:
        author = determine_author(f)
        if author == "ai":
            ai_files.append(f)
            console.print(f"  [cyan]AI:[/cyan]    {f}")
        else:
            human_files.append(f)
            console.print(f"  [green]Human:[/green] {f}")

    console.print()

    # Commit human files first (no author override)
    if human_files:
        human_message = message or f"Update {len(human_files)} file(s) (human edit)"
        console.print(f"[bold]Committing {len(human_files)} human file(s)[/bold]")
        if not commit_files(human_files, None, human_message, dry_run):
            sys.exit(1)
        console.print("  [green]Done[/green]\n")

    # Commit AI files with AI author
    if ai_files:
        ai_message = message or f"Update {len(ai_files)} file(s) (AI edit)"
        console.print(f"[bold]Committing {len(ai_files)} AI file(s)[/bold]")
        if not commit_files(ai_files, AI_AUTHOR, ai_message, dry_run):
            sys.exit(1)
        console.print("  [green]Done[/green]\n")

    if dry_run:
        console.print("[yellow]Dry run - no changes made[/yellow]")
    else:
        console.print("[bold green]Done![/bold green]")


if __name__ == "__main__":
    main()
