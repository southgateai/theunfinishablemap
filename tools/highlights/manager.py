"""Manage the highlights page - add items, enforce limits, check dates."""

from __future__ import annotations

import logging
import re
import subprocess
import time
from datetime import date, datetime
from pathlib import Path
from typing import TYPE_CHECKING

import frontmatter
import httpx

from .twitter import TweetResult, post_tweet, wikilink_to_url

if TYPE_CHECKING:
    from typing import TypedDict
else:
    from typing import TypedDict

logger = logging.getLogger(__name__)

# Repository root (three levels up from this file)
REPO_ROOT = Path(__file__).parent.parent.parent

MAX_HIGHLIGHTS = 20
MARKER_START = "<!-- HIGHLIGHTS_START -->"
MARKER_END = "<!-- HIGHLIGHTS_END -->"

# Pattern to match highlight headers: ### 2026-01-07: Title
HIGHLIGHT_PATTERN = re.compile(r"^### (\d{4}-\d{2}-\d{2}): (.+)$", re.MULTILINE)


class Highlight(TypedDict):
    """Structured highlight for parsing/serialization."""

    date: str
    title: str
    description: str
    highlight_type: str
    link: str | None


def get_latest_date(file_path: Path) -> date | None:
    """
    Get the date of the most recent highlight.

    Args:
        file_path: Path to highlights.md

    Returns:
        Date of most recent highlight, or None if no highlights exist.
    """
    if not file_path.exists():
        return None

    content = file_path.read_text(encoding="utf-8")

    # Find all highlight dates
    matches = HIGHLIGHT_PATTERN.findall(content)
    if not matches:
        return None

    # First match is most recent (newest first)
    date_str = matches[0][0]
    try:
        return date.fromisoformat(date_str)
    except ValueError:
        return None


def can_add_today(file_path: Path) -> bool:
    """
    Check if we can add a highlight today (max 1 per day).

    Args:
        file_path: Path to highlights.md

    Returns:
        True if no highlight has been added today.
    """
    latest = get_latest_date(file_path)
    if latest is None:
        return True
    return latest < date.today()


def _git_commit_and_push(title: str) -> bool:
    """
    Commit highlight changes and push to origin.

    Also updates last_git_push in evolution-state.yaml so evolve_loop.py
    knows a push happened.

    Args:
        title: Highlight title for the commit message

    Returns:
        True if commit and push succeeded.
    """
    try:
        # Stage the highlights file (and synced Hugo content)
        subprocess.run(
            ["git", "add", "obsidian/workflow/highlights.md", "hugo/content/highlights.md"],
            cwd=REPO_ROOT,
            check=True,
            capture_output=True,
        )

        # Commit
        commit_msg = f"feat(auto): add highlight - {title}"
        subprocess.run(
            ["git", "commit", "-m", commit_msg],
            cwd=REPO_ROOT,
            check=True,
            capture_output=True,
        )

        # Push
        subprocess.run(
            ["git", "push"],
            cwd=REPO_ROOT,
            check=True,
            capture_output=True,
        )

        logger.info("Committed and pushed highlight")

        # Update last_git_push in evolution state so evolve_loop knows about this push
        _update_last_git_push()

        return True

    except subprocess.CalledProcessError as e:
        logger.error(f"Git operation failed: {e.cmd} returned {e.returncode}")
        if e.stderr:
            logger.error(f"stderr: {e.stderr.decode()}")
        return False


def _update_last_git_push() -> None:
    """Update last_git_push timestamp in evolution-state.yaml."""
    from datetime import timezone

    from tools.evolution.state import load_state, save_state

    state_path = REPO_ROOT / "obsidian" / "workflow" / "evolution-state.yaml"
    try:
        state = load_state(state_path)
        state.last_git_push = datetime.now(timezone.utc)
        save_state(state, state_path)
        logger.info("Updated last_git_push in evolution state")
    except Exception as e:
        logger.warning(f"Could not update last_git_push: {e}")


def _wait_for_deployment(
    url: str,
    poll_interval: int = 10,
    max_wait: int = 300,
) -> bool:
    """
    Wait for a URL to become available after deployment.

    Args:
        url: The URL to check
        poll_interval: Seconds between checks (default: 10)
        max_wait: Maximum seconds to wait (default: 300 = 5 minutes)

    Returns:
        True if URL became available, False if timed out.
    """
    start_time = time.time()
    attempts = 0

    while time.time() - start_time < max_wait:
        attempts += 1
        try:
            response = httpx.get(url, timeout=10, follow_redirects=True)
            if response.status_code == 200:
                elapsed = time.time() - start_time
                logger.info(f"Page available after {elapsed:.0f}s ({attempts} attempts): {url}")
                return True
            else:
                logger.debug(f"Attempt {attempts}: HTTP {response.status_code}")
        except httpx.RequestError as e:
            logger.debug(f"Attempt {attempts}: {e}")

        time.sleep(poll_interval)

    logger.error(f"Page not available after {max_wait}s ({attempts} attempts): {url}")
    return False


def add_highlight(
    file_path: Path,
    title: str,
    description: str,
    highlight_type: str,
    link: str | None = None,
    tweet: bool = False,
    dry_run: bool = False,
) -> tuple[bool, TweetResult | None]:
    """
    Add a highlight to the top of the list.

    Args:
        file_path: Path to highlights.md
        title: Short, engaging title (5-10 words)
        description: 1-2 sentences, max 280 chars for Twitter
        highlight_type: One of: new-article, insight, research, refinement
        link: Optional wikilink to related content
        tweet: If True, post to Twitter after adding highlight
        dry_run: If True with tweet, format tweet but don't actually post

    Returns:
        Tuple of (highlight_added: bool, tweet_result: TweetResult | None).
        highlight_added is False if rate-limited (already added today).
        tweet_result is None if tweet=False or rate-limited.
    """
    if not can_add_today(file_path):
        return False, None

    # Validate description length
    if len(description) > 280:
        description = description[:277] + "..."

    # Build the highlight markdown
    today = date.today().isoformat()
    highlight_md = f"### {today}: {title}\n\n{description}\n\n"
    highlight_md += f"**Type**: {highlight_type}"
    if link:
        highlight_md += f"  \n**Link**: {link}"
    highlight_md += "\n\n---\n\n"

    # Read the file
    post = frontmatter.load(file_path)
    content = post.content

    # Find the markers and insert
    start_idx = content.find(MARKER_START)
    end_idx = content.find(MARKER_END)

    if start_idx == -1 or end_idx == -1:
        # No markers found - append to end
        content = content.rstrip() + "\n\n" + MARKER_START + "\n" + highlight_md + MARKER_END
    else:
        # Insert after start marker
        insert_pos = start_idx + len(MARKER_START) + 1
        content = content[:insert_pos] + highlight_md + content[insert_pos:]

    # Update frontmatter
    post.content = content
    post.metadata["modified"] = today
    post.metadata["ai_modified"] = datetime.now().isoformat()

    # Write back
    file_path.write_text(frontmatter.dumps(post), encoding="utf-8")

    # Trim to max highlights
    trim_highlights(file_path, MAX_HIGHLIGHTS)

    # Optionally post to Twitter (after successful file write)
    tweet_result: TweetResult | None = None
    if tweet:
        if dry_run:
            # Dry run: just format the tweet without committing/pushing/waiting
            tweet_result = post_tweet(
                title=title,
                description=description,
                link=link,
                dry_run=True,
            )
        else:
            # Real tweet: commit, push, wait for deployment, then tweet
            # First, commit and push the highlight
            if not _git_commit_and_push(title):
                logger.error("Failed to commit/push highlight, skipping tweet")
                return True, TweetResult(
                    success=False,
                    tweet_id=None,
                    error="Failed to commit/push highlight",
                    url=None,
                )

            # Wait for the linked page to become available
            if link:
                page_url = wikilink_to_url(link)
                if not _wait_for_deployment(page_url):
                    logger.error(f"Page not available after deployment timeout: {page_url}")
                    return True, TweetResult(
                        success=False,
                        tweet_id=None,
                        error=f"Page not available after 5 minutes: {page_url}",
                        url=None,
                    )

            # Now post the tweet
            tweet_result = post_tweet(
                title=title,
                description=description,
                link=link,
                dry_run=False,
            )

    return True, tweet_result


def trim_highlights(file_path: Path, max_items: int = MAX_HIGHLIGHTS) -> int:
    """
    Trim highlights to keep only the most recent N items.

    Args:
        file_path: Path to highlights.md
        max_items: Maximum number of highlights to keep

    Returns:
        Number of highlights removed.
    """
    post = frontmatter.load(file_path)
    content = post.content

    # Find the markers
    start_idx = content.find(MARKER_START)
    end_idx = content.find(MARKER_END)

    if start_idx == -1 or end_idx == -1:
        return 0

    # Extract highlights section
    before = content[: start_idx + len(MARKER_START) + 1]
    highlights_section = content[start_idx + len(MARKER_START) + 1 : end_idx]
    after = content[end_idx:]

    # Split into individual highlights (each starts with ###)
    highlights = re.split(r"(?=^### \d{4}-\d{2}-\d{2}:)", highlights_section, flags=re.MULTILINE)
    highlights = [h for h in highlights if h.strip()]  # Remove empty

    if len(highlights) <= max_items:
        return 0

    # Keep only the most recent
    removed_count = len(highlights) - max_items
    highlights = highlights[:max_items]

    # Reconstruct
    post.content = before + "".join(highlights) + after

    # Write back
    file_path.write_text(frontmatter.dumps(post), encoding="utf-8")

    return removed_count


def parse_highlights(file_path: Path) -> list[Highlight]:
    """
    Parse highlights into structured data (for future Twitter integration).

    Args:
        file_path: Path to highlights.md

    Returns:
        List of Highlight dicts with date, title, description, type, link.
    """
    if not file_path.exists():
        return []

    content = file_path.read_text(encoding="utf-8")

    # Find the markers
    start_idx = content.find(MARKER_START)
    end_idx = content.find(MARKER_END)

    if start_idx == -1 or end_idx == -1:
        return []

    highlights_section = content[start_idx + len(MARKER_START) + 1 : end_idx]

    # Split into individual highlights
    raw_highlights = re.split(
        r"(?=^### \d{4}-\d{2}-\d{2}:)", highlights_section, flags=re.MULTILINE
    )
    raw_highlights = [h for h in raw_highlights if h.strip()]

    results: list[Highlight] = []

    for raw in raw_highlights:
        # Parse the header
        header_match = HIGHLIGHT_PATTERN.search(raw)
        if not header_match:
            continue

        highlight_date = header_match.group(1)
        title = header_match.group(2)

        # Parse description (text between header and **Type**)
        lines = raw.split("\n")
        description_lines = []
        highlight_type = ""
        link = None

        in_description = False
        for line in lines:
            if line.startswith("### "):
                in_description = True
                continue
            if line.startswith("**Type**:"):
                highlight_type = line.replace("**Type**:", "").strip()
                in_description = False
            elif line.startswith("**Link**:"):
                link = line.replace("**Link**:", "").strip()
            elif in_description and line.strip() and not line.startswith("---"):
                description_lines.append(line.strip())

        description = " ".join(description_lines)

        results.append(
            Highlight(
                date=highlight_date,
                title=title,
                description=description,
                highlight_type=highlight_type,
                link=link,
            )
        )

    return results
