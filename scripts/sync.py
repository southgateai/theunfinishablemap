#!/usr/bin/env python3
"""Sync Obsidian vault to Hugo content directory."""

import sys
from pathlib import Path

import click
from rich.console import Console
from rich.table import Table

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from tools.sync import convert_obsidian_to_hugo


console = Console()


@click.command()
@click.option(
    "--obsidian",
    "-o",
    type=click.Path(exists=True, path_type=Path),
    default="obsidian",
    help="Path to Obsidian vault",
)
@click.option(
    "--hugo",
    "-h",
    type=click.Path(path_type=Path),
    default="hugo/content",
    help="Path to Hugo content directory",
)
@click.option(
    "--include-drafts",
    is_flag=True,
    help="Include files from drafts folder",
)
@click.option(
    "--dry-run",
    "-n",
    is_flag=True,
    help="Show what would be synced without making changes",
)
def main(
    obsidian: Path,
    hugo: Path,
    include_drafts: bool,
    dry_run: bool,
) -> None:
    """Sync Obsidian vault content to Hugo."""
    console.print(f"[bold]Syncing Obsidian → Hugo[/bold]")
    console.print(f"  Source: {obsidian.absolute()}")
    console.print(f"  Target: {hugo.absolute()}")

    if dry_run:
        console.print("  [yellow]Dry run - no changes will be made[/yellow]")

    converted = convert_obsidian_to_hugo(
        obsidian_path=obsidian,
        hugo_content_path=hugo,
        exclude_drafts=not include_drafts,
        dry_run=dry_run,
    )

    if converted:
        table = Table(title=f"{'Would sync' if dry_run else 'Synced'} {len(converted)} files")
        table.add_column("File", style="cyan")
        table.add_column("Status", style="green")

        for path in converted:
            table.add_row(str(path.relative_to(hugo)), "✓" if not dry_run else "pending")

        console.print(table)
    else:
        console.print("[yellow]No files to sync[/yellow]")


if __name__ == "__main__":
    main()
