#!/usr/bin/env python3
"""Build pipeline for SouthgateAI."""

import subprocess
import sys
from pathlib import Path

import click
from rich.console import Console

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from tools.sync import convert_obsidian_to_hugo
from tools.build import sync_api_content
from tools.curate.validate import validate_directory


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
    default="hugo",
    help="Path to Hugo project directory",
)
@click.option(
    "--skip-sync",
    is_flag=True,
    help="Skip Obsidian sync step",
)
@click.option(
    "--skip-validate",
    is_flag=True,
    help="Skip validation step",
)
@click.option(
    "--skip-hugo",
    is_flag=True,
    help="Skip Hugo build step",
)
@click.option(
    "--output",
    type=click.Path(path_type=Path),
    default="public",
    help="Hugo output directory",
)
def main(
    obsidian: Path,
    hugo: Path,
    skip_sync: bool,
    skip_validate: bool,
    skip_hugo: bool,
    output: Path,
) -> None:
    """Run the full build pipeline."""
    console.print("[bold blue]SouthgateAI Build Pipeline[/bold blue]\n")

    content_dir = hugo / "content"
    api_dir = content_dir / "api"

    # Step 1: Sync Obsidian → Hugo
    if not skip_sync:
        console.print("[bold]Step 1:[/bold] Syncing Obsidian -> Hugo")
        with console.status("Syncing..."):
            converted = convert_obsidian_to_hugo(
                obsidian_path=obsidian,
                hugo_content_path=content_dir,
            )
        console.print(f"  [green]Done[/green] Synced {len(converted)} files\n")
    else:
        console.print("[dim]Step 1: Skipped Obsidian sync[/dim]\n")

    # Step 2: Validate frontmatter
    if not skip_validate:
        console.print("[bold]Step 2:[/bold] Validating content")
        with console.status("Validating..."):
            results = validate_directory(content_dir)

        if results["invalid"] > 0:
            console.print(
                f"  [red]FAIL[/red] {results['invalid']} invalid files "
                f"({results['valid']} valid)\n"
            )
            # Don't fail the build, just warn
        else:
            console.print(
                f"  [green]Done[/green] All {results['valid']} files valid\n"
            )
    else:
        console.print("[dim]Step 2: Skipped validation[/dim]\n")

    # Step 3: Sync API content
    console.print("[bold]Step 3:[/bold] Syncing API content")
    with console.status("Syncing API..."):
        api_files = sync_api_content(content_dir, api_dir)
    console.print(f"  [green]Done[/green] Synced {len(api_files)} API files\n")

    # Step 4: Build Hugo site
    if not skip_hugo:
        console.print("[bold]Step 4:[/bold] Building Hugo site")

        # Check if Hugo is installed
        try:
            result = subprocess.run(
                ["hugo", "version"],
                capture_output=True,
                text=True,
            )
            if result.returncode != 0:
                console.print("  [red]FAIL[/red] Hugo not found")
                console.print("  Install Hugo: https://gohugo.io/installation/")
                sys.exit(1)
        except FileNotFoundError:
            console.print("  [red]FAIL[/red] Hugo not installed")
            console.print("  Install Hugo: https://gohugo.io/installation/")
            sys.exit(1)

        # Run Hugo build
        with console.status("Building..."):
            result = subprocess.run(
                [
                    "hugo",
                    "--source", str(hugo),
                    "--destination", str(output.absolute()),
                    "--minify",
                ],
                capture_output=True,
                text=True,
            )

        if result.returncode != 0:
            console.print("  [red]FAIL[/red] Hugo build failed")
            console.print(result.stderr)
            sys.exit(1)

        console.print(f"  [green]Done[/green] Built to {output}\n")
    else:
        console.print("[dim]Step 4: Skipped Hugo build[/dim]\n")

    console.print("[bold green]Build complete![/bold green]")


if __name__ == "__main__":
    main()
