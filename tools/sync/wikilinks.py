"""Convert Obsidian wikilinks to Hugo-compatible markdown links."""

import re
from typing import Callable, Optional


def convert_wikilinks(
    content: str,
    base_path: str = "/",
    link_resolver: Optional[Callable[[str], str]] = None,
) -> str:
    """
    Convert Obsidian [[wikilinks]] to Hugo markdown links.

    Args:
        content: Markdown content with wikilinks
        base_path: Base path prefix for generated links
        link_resolver: Optional function to resolve link targets

    Returns:
        Content with wikilinks converted to markdown links

    Examples:
        [[Page Name]] -> [Page Name](/page-name/)
        [[Page Name|Display Text]] -> [Display Text](/page-name/)
        [[folder/Page Name]] -> [Page Name](/folder/page-name/)
        [[Page Name#Heading]] -> [Page Name](/page-name/#heading)
    """
    # Pattern for wikilinks: [[target]] or [[target|display]]
    wikilink_pattern = re.compile(r"\[\[([^\]]+)\]\]")

    def replace_wikilink(match: re.Match) -> str:
        link_content = match.group(1)

        # Parse the wikilink components
        display_text: Optional[str] = None
        heading: Optional[str] = None

        # Check for display text (pipe separator)
        if "|" in link_content:
            target, display_text = link_content.split("|", 1)
        else:
            target = link_content

        # Check for heading anchor
        if "#" in target:
            target, heading = target.split("#", 1)

        # Clean up the target
        target = target.strip()

        # Use display text or derive from target
        if display_text is None:
            # Use the last part of the path as display
            display_text = target.split("/")[-1] if "/" in target else target

        # Resolve the link URL
        if link_resolver:
            url = link_resolver(target)
        else:
            url = default_link_resolver(target, base_path)

        # Add heading anchor if present
        if heading:
            # Slugify the heading
            heading_slug = slugify(heading)
            url = f"{url}#{heading_slug}"

        return f"[{display_text}]({url})"

    return wikilink_pattern.sub(replace_wikilink, content)


def default_link_resolver(target: str, base_path: str = "/") -> str:
    """
    Default resolver for wikilink targets.

    Converts the target to a URL-friendly slug.
    """
    # Handle path separators
    parts = target.split("/")

    # Slugify each part
    slugified_parts = [slugify(part) for part in parts]

    # Build the URL
    path = "/".join(slugified_parts)

    # Ensure base path ends without slash, path starts without slash
    base_path = base_path.rstrip("/")
    path = path.lstrip("/")

    # Return URL with trailing slash (Hugo convention)
    return f"{base_path}/{path}/"


def slugify(text: str) -> str:
    """
    Convert text to URL-friendly slug.

    Args:
        text: Text to slugify

    Returns:
        URL-friendly slug
    """
    # Convert to lowercase
    slug = text.lower()

    # Replace spaces and underscores with hyphens
    slug = re.sub(r"[\s_]+", "-", slug)

    # Remove non-alphanumeric characters (except hyphens)
    slug = re.sub(r"[^a-z0-9\-]", "", slug)

    # Remove consecutive hyphens
    slug = re.sub(r"-+", "-", slug)

    # Remove leading/trailing hyphens
    slug = slug.strip("-")

    return slug


def extract_wikilinks(content: str) -> list[dict]:
    """
    Extract all wikilinks from content for analysis.

    Args:
        content: Markdown content

    Returns:
        List of dicts with wikilink info
    """
    wikilink_pattern = re.compile(r"\[\[([^\]]+)\]\]")
    links = []

    for match in wikilink_pattern.finditer(content):
        link_content = match.group(1)

        display_text = None
        heading = None

        if "|" in link_content:
            target, display_text = link_content.split("|", 1)
        else:
            target = link_content

        if "#" in target:
            target, heading = target.split("#", 1)

        links.append(
            {
                "raw": match.group(0),
                "target": target.strip(),
                "display": display_text,
                "heading": heading,
                "position": match.start(),
            }
        )

    return links


def validate_wikilinks(
    content: str,
    known_pages: set[str],
) -> list[dict]:
    """
    Validate wikilinks against known pages.

    Args:
        content: Markdown content
        known_pages: Set of known page names/paths

    Returns:
        List of invalid/broken links
    """
    links = extract_wikilinks(content)
    broken = []

    for link in links:
        target = link["target"].lower().replace(" ", "-")

        # Check if target exists in known pages
        if target not in known_pages:
            broken.append(link)

    return broken
