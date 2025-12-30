#!/usr/bin/env python3
"""Generate philosophical content using LLM."""

import sys
from pathlib import Path

import click
from rich.console import Console
from rich.markdown import Markdown

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from tools.generate import generate_article, generate_article_outline
from tools.llm import get_client, list_default_models


console = Console()


@click.group()
def cli() -> None:
    """Generate philosophical content."""
    pass


@cli.command()
@click.argument("topic")
@click.option(
    "--concepts",
    "-c",
    multiple=True,
    help="Related concepts to incorporate",
)
@click.option(
    "--style",
    type=click.Choice(["exploratory", "argumentative", "analytical"]),
    default="exploratory",
    help="Writing style",
)
@click.option(
    "--length",
    type=click.Choice(["short", "medium", "long"]),
    default="medium",
    help="Article length",
)
@click.option(
    "--output",
    "-o",
    type=click.Path(path_type=Path),
    help="Output file path",
)
@click.option(
    "--model",
    "-m",
    help="LLM model to use (e.g., claude-sonnet-4-20250514, gpt-4o, gemini/gemini-pro)",
)
def article(
    topic: str,
    concepts: tuple,
    style: str,
    length: str,
    output: Path | None,
    model: str | None,
) -> None:
    """Generate a philosophical article on TOPIC."""
    console.print(f"[bold]Generating article:[/bold] {topic}")
    console.print(f"  Style: {style}, Length: {length}")

    if concepts:
        console.print(f"  Concepts: {', '.join(concepts)}")

    client = get_client(model) if model else None

    with console.status("Generating content..."):
        content = generate_article(
            topic=topic,
            concepts=list(concepts) if concepts else None,
            style=style,
            length=length,
            client=client,
            output_path=output,
        )

    if output:
        console.print(f"[green]Saved to:[/green] {output}")
    else:
        console.print("\n[bold]Generated Article:[/bold]\n")
        console.print(Markdown(content))


@cli.command()
@click.argument("topic")
@click.option(
    "--model",
    "-m",
    help="LLM model to use",
)
def outline(topic: str, model: str | None) -> None:
    """Generate an outline for TOPIC."""
    console.print(f"[bold]Generating outline:[/bold] {topic}")

    client = get_client(model) if model else None

    with console.status("Generating outline..."):
        result = generate_article_outline(topic=topic, client=client)

    console.print(f"\n[bold]Title:[/bold] {result.get('title', topic)}")
    console.print(f"[bold]Thesis:[/bold] {result.get('thesis', 'N/A')}")

    console.print("\n[bold]Sections:[/bold]")
    for section in result.get("sections", []):
        console.print(f"  • {section.get('heading', 'Untitled')}")
        console.print(f"    {section.get('summary', '')}")

    if result.get("concepts"):
        console.print(f"\n[bold]Concepts:[/bold] {', '.join(result['concepts'])}")


@cli.command()
def models() -> None:
    """List default models by provider."""
    console.print("[bold]Default models:[/bold]")
    for provider, model in list_default_models().items():
        console.print(f"  {provider}: {model}")
    console.print("\n[dim]Set LITELLM_MODEL env var or use --model to override[/dim]")


def main() -> None:
    """Entry point."""
    cli()


if __name__ == "__main__":
    main()
