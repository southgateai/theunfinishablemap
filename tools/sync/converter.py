"""Convert Obsidian markdown files to Hugo-compatible format."""

import re
import shutil
from pathlib import Path
from typing import Optional

import frontmatter

from .wikilinks import convert_wikilinks


def convert_obsidian_to_hugo(
    obsidian_path: Path,
    hugo_content_path: Path,
    exclude_drafts: bool = True,
    dry_run: bool = False,
) -> list[Path]:
    """
    Convert Obsidian vault content to Hugo content directory.

    Args:
        obsidian_path: Path to Obsidian vault root
        hugo_content_path: Path to Hugo content directory
        exclude_drafts: Whether to exclude files in drafts/ folder
        dry_run: If True, don't actually copy files

    Returns:
        List of paths to converted files
    """
    converted_files: list[Path] = []

    # Directories to sync (exclude .obsidian, drafts if configured)
    sync_dirs = ["topics", "concepts"]

    for sync_dir in sync_dirs:
        source_dir = obsidian_path / sync_dir
        if not source_dir.exists():
            continue

        target_dir = hugo_content_path / sync_dir

        for md_file in source_dir.rglob("*.md"):
            # Skip draft files if configured
            if exclude_drafts and "drafts" in md_file.parts:
                continue

            # Calculate relative path and target
            rel_path = md_file.relative_to(source_dir)
            target_file = target_dir / rel_path

            # Convert the file
            converted_content = convert_file(md_file)

            if not dry_run:
                target_file.parent.mkdir(parents=True, exist_ok=True)
                target_file.write_text(converted_content, encoding="utf-8")

            converted_files.append(target_file)

    return converted_files


def convert_file(source_path: Path) -> str:
    """
    Convert a single Obsidian markdown file to Hugo format.

    Args:
        source_path: Path to source markdown file

    Returns:
        Converted markdown content as string
    """
    # Parse frontmatter and content
    post = frontmatter.load(source_path)

    # Ensure required frontmatter fields exist
    if "title" not in post.metadata:
        # Use filename as title
        post.metadata["title"] = source_path.stem.replace("-", " ").title()

    if "date" not in post.metadata:
        # Use 'modified' from frontmatter if available, otherwise file modification time
        if "modified" in post.metadata:
            post.metadata["date"] = post.metadata["modified"]
        else:
            import datetime

            mtime = source_path.stat().st_mtime
            post.metadata["date"] = datetime.date.fromtimestamp(mtime).isoformat()

    # Ensure authorship metadata exists (flat schema)
    if "ai_contribution" not in post.metadata:
        post.metadata["ai_contribution"] = 0

    # Ensure content metadata exists (flat schema)
    if "concepts" not in post.metadata:
        post.metadata["concepts"] = []
    if "related_articles" not in post.metadata:
        post.metadata["related_articles"] = []

    # Convert content
    content = post.content

    # Convert Obsidian wikilinks to Hugo links
    content = convert_wikilinks(content)

    # Convert Obsidian callouts to Hugo shortcodes (if needed)
    content = convert_callouts(content)

    # Convert Obsidian embeds
    content = convert_embeds(content)

    # Rebuild the file with frontmatter
    post.content = content
    return frontmatter.dumps(post)


def convert_callouts(content: str) -> str:
    """
    Convert Obsidian callouts to HTML blockquotes with classes.

    Obsidian format: > [!note] Title
    Hugo format: <blockquote class="callout callout-note">...</blockquote>
    """
    # Pattern for Obsidian callouts
    callout_pattern = re.compile(
        r"^>\s*\[!(\w+)\]\s*(.*)$", re.MULTILINE
    )

    def replace_callout(match: re.Match) -> str:
        callout_type = match.group(1).lower()
        title = match.group(2).strip()
        if title:
            return f'> **{title}**\n> \n> *({callout_type})*'
        return f"> *({callout_type})*"

    return callout_pattern.sub(replace_callout, content)


def convert_embeds(content: str) -> str:
    """
    Convert Obsidian embeds (![[file]]) to Hugo references.

    For now, just converts to regular links.
    """
    # Pattern for Obsidian embeds
    embed_pattern = re.compile(r"!\[\[([^\]]+)\]\]")

    def replace_embed(match: re.Match) -> str:
        target = match.group(1)
        # Handle display text
        if "|" in target:
            target, display = target.split("|", 1)
        else:
            display = target

        # Convert to markdown link (embedded content would need more work)
        return f"[{display}](/{target.lower().replace(' ', '-')}/)"

    return embed_pattern.sub(replace_embed, content)


def ensure_frontmatter(content: str, defaults: Optional[dict] = None) -> str:
    """
    Ensure a markdown file has valid frontmatter.

    Args:
        content: Raw markdown content
        defaults: Default frontmatter values

    Returns:
        Content with valid frontmatter
    """
    defaults = defaults or {}

    try:
        post = frontmatter.loads(content)
    except Exception:
        # No valid frontmatter, create new
        post = frontmatter.Post(content)
        post.metadata = defaults

    # Merge defaults
    for key, value in defaults.items():
        if key not in post.metadata:
            post.metadata[key] = value

    return frontmatter.dumps(post)
