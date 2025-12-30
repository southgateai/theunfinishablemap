#!/usr/bin/env python3
"""Content curation tools."""

import sys
from pathlib import Path

import click
from rich.console import Console
from rich.table import Table

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from tools.curate import review_content, generate_crosslinks, validate_frontmatter
from tools.curate.crosslink import apply_crosslinks, suggest_concepts
from tools.curate.validate import validate_directory, fix_frontmatter
from tools.llm import get_client


console = Console()


@click.group()
def cli() -> None:
    """Content curation tools."""
    pass


@cli.command()
@click.argument("path", type=click.Path(exists=True, path_type=Path))
@click.option(
    "--model",
    "-m",
    help="LLM model to use (e.g., claude-sonnet-4-20250514, gpt-4o)",
)
def review(path: Path, model: str | None) -> None:
    """Review content quality at PATH."""
    console.print(f"[bold]Reviewing:[/bold] {path}")

    client = get_client(model) if model else None

    with console.status("Analyzing content..."):
        result = review_content(path, client=client)

    console.print(f"\n[bold]Quality Score:[/bold] {result.get('overall_quality', 'N/A')}/10")

    if result.get("strengths"):
        console.print("\n[bold green]Strengths:[/bold green]")
        for s in result["strengths"]:
            console.print(f"  ✓ {s}")

    if result.get("improvements"):
        console.print("\n[bold yellow]Suggested Improvements:[/bold yellow]")
        for imp in result["improvements"]:
            priority = imp.get("priority", "medium")
            icon = "🔴" if priority == "high" else "🟡" if priority == "medium" else "🟢"
            console.print(f"  {icon} {imp.get('issue', 'Issue')}")
            console.print(f"     → {imp.get('suggestion', '')}")

    if result.get("missing_concepts"):
        console.print(f"\n[bold]Missing Concepts:[/bold] {', '.join(result['missing_concepts'])}")


@cli.command()
@click.argument("path", type=click.Path(exists=True, path_type=Path))
@click.option(
    "--strict",
    is_flag=True,
    help="Require all recommended fields",
)
@click.option(
    "--fix",
    is_flag=True,
    help="Attempt to fix issues automatically",
)
def validate(path: Path, strict: bool, fix: bool) -> None:
    """Validate frontmatter at PATH (file or directory)."""
    if path.is_file():
        result = validate_frontmatter(path, strict=strict)
        _print_validation_result(result)

        if fix and not result["valid"]:
            if fix_frontmatter(path):
                console.print("[green]Fixed frontmatter issues[/green]")
    else:
        results = validate_directory(path, strict=strict)

        table = Table(title=f"Validation Results: {path}")
        table.add_column("Metric", style="cyan")
        table.add_column("Count", style="white")

        table.add_row("Total files", str(results["total"]))
        table.add_row("Valid", f"[green]{results['valid']}[/green]")
        table.add_row("Invalid", f"[red]{results['invalid']}[/red]")
        table.add_row("Warnings", f"[yellow]{results['warnings']}[/yellow]")

        console.print(table)

        # Show details for invalid files
        for file_result in results["files"]:
            if not file_result["valid"] or file_result["warnings"]:
                console.print(f"\n[bold]{file_result['path']}[/bold]")
                for error in file_result["errors"]:
                    console.print(f"  [red]✗ {error}[/red]")
                for warning in file_result["warnings"]:
                    console.print(f"  [yellow]⚠ {warning}[/yellow]")


def _print_validation_result(result: dict) -> None:
    """Print a single validation result."""
    status = "[green]✓ Valid[/green]" if result["valid"] else "[red]✗ Invalid[/red]"
    console.print(f"{result['path']}: {status}")

    for error in result["errors"]:
        console.print(f"  [red]✗ {error}[/red]")
    for warning in result["warnings"]:
        console.print(f"  [yellow]⚠ {warning}[/yellow]")


@cli.command()
@click.argument("directory", type=click.Path(exists=True, path_type=Path))
@click.option(
    "--apply",
    is_flag=True,
    help="Apply crosslinks to frontmatter",
)
@click.option(
    "--min-relevance",
    type=float,
    default=0.7,
    help="Minimum relevance score (0-1)",
)
@click.option(
    "--model",
    "-m",
    help="LLM model to use",
)
def crosslink(
    directory: Path,
    apply: bool,
    min_relevance: float,
    model: str | None,
) -> None:
    """Generate cross-links between content in DIRECTORY."""
    console.print(f"[bold]Generating crosslinks:[/bold] {directory}")

    client = get_client(model) if model else None

    with console.status("Analyzing content relationships..."):
        links = generate_crosslinks(
            directory, client=client, min_relevance=min_relevance
        )

    if not links:
        console.print("[yellow]No crosslinks found[/yellow]")
        return

    table = Table(title=f"Found {sum(len(v) for v in links.values())} relationships")
    table.add_column("Source", style="cyan")
    table.add_column("Related To", style="white")

    for source, targets in links.items():
        table.add_row(source, ", ".join(targets))

    console.print(table)

    if apply:
        updated = apply_crosslinks(directory, links)
        console.print(f"[green]Updated {updated} files[/green]")


@cli.command()
@click.argument("path", type=click.Path(exists=True, path_type=Path))
@click.option(
    "--model",
    "-m",
    help="LLM model to use",
)
def concepts(path: Path, model: str | None) -> None:
    """Suggest concepts for content at PATH."""
    console.print(f"[bold]Suggesting concepts:[/bold] {path}")

    client = get_client(model) if model else None

    with console.status("Analyzing content..."):
        suggested = suggest_concepts(path, client=client)

    if suggested:
        console.print("\n[bold]Suggested Concepts:[/bold]")
        for concept in suggested:
            console.print(f"  • {concept}")
    else:
        console.print("[yellow]No concepts identified[/yellow]")


def main() -> None:
    """Entry point."""
    cli()


if __name__ == "__main__":
    main()
