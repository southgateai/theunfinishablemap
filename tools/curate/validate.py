"""Frontmatter validation for content files."""

from datetime import datetime
from pathlib import Path
from typing import Optional, Union

import frontmatter


def _is_valid_timestamp(value: Union[str, datetime, None]) -> bool:
    """Check if a value is a valid ISO timestamp."""
    if value is None:
        return True
    if isinstance(value, datetime):
        return True
    try:
        datetime.fromisoformat(str(value))
        return True
    except (ValueError, TypeError):
        return False


# Required frontmatter fields
REQUIRED_FIELDS = ["title"]


def get_authorship_type(ai_contribution: int) -> str:
    """Derive authorship type from ai_contribution percentage."""
    if ai_contribution == 0:
        return "human"
    elif ai_contribution == 100:
        return "ai"
    else:
        return "mixed"


def validate_frontmatter(
    content_path: Path,
    strict: bool = False,
) -> dict:
    """
    Validate frontmatter in a markdown file.

    Args:
        content_path: Path to markdown file
        strict: If True, require all optional fields too

    Returns:
        Dict with validation results
    """
    result = {
        "valid": True,
        "errors": [],
        "warnings": [],
        "path": str(content_path),
    }

    try:
        post = frontmatter.load(content_path)
    except Exception as e:
        result["valid"] = False
        result["errors"].append(f"Failed to parse frontmatter: {e}")
        return result

    metadata = post.metadata

    # Check required fields
    for field in REQUIRED_FIELDS:
        if field not in metadata:
            result["valid"] = False
            result["errors"].append(f"Missing required field: {field}")

    # Validate ai_contribution if present
    ai_contribution = metadata.get("ai_contribution")
    if ai_contribution is not None:
        if not isinstance(ai_contribution, (int, float)):
            result["errors"].append("ai_contribution must be a number")
            result["valid"] = False
        elif not (0 <= ai_contribution <= 100):
            result["errors"].append("ai_contribution must be between 0 and 100")
            result["valid"] = False
        else:
            # Derive type and validate consistency
            authorship_type = get_authorship_type(int(ai_contribution))

            if authorship_type == "ai":
                if not metadata.get("ai_system"):
                    result["warnings"].append(
                        "AI-authored content (ai_contribution=100) should specify ai_system"
                    )

            elif authorship_type == "human":
                if not metadata.get("author"):
                    result["warnings"].append(
                        "Human-authored content should specify author"
                    )

    # Validate timestamp fields if present
    for field in ["human_modified", "ai_modified", "ai_generated_date", "last_curated"]:
        if field in metadata and metadata[field]:
            if not _is_valid_timestamp(metadata[field]):
                result["warnings"].append(
                    f"Invalid timestamp format for {field}: {metadata[field]}"
                )

    # Check optional but recommended fields
    if strict:
        if "created" not in metadata:
            result["warnings"].append("Missing recommended field: created")
        if "concepts" not in metadata:
            result["warnings"].append("Missing recommended field: concepts")

    # Check content
    if not post.content.strip():
        result["warnings"].append("Content is empty")

    return result


def validate_directory(
    content_dir: Path,
    strict: bool = False,
) -> dict:
    """
    Validate all markdown files in a directory.

    Args:
        content_dir: Directory to validate
        strict: If True, require all optional fields

    Returns:
        Dict with summary and per-file results
    """
    results = {
        "total": 0,
        "valid": 0,
        "invalid": 0,
        "warnings": 0,
        "files": [],
    }

    for md_file in content_dir.rglob("*.md"):
        result = validate_frontmatter(md_file, strict=strict)
        results["total"] += 1

        if result["valid"]:
            results["valid"] += 1
        else:
            results["invalid"] += 1

        if result["warnings"]:
            results["warnings"] += len(result["warnings"])

        results["files"].append(result)

    return results


def fix_frontmatter(
    content_path: Path,
    defaults: Optional[dict] = None,
) -> bool:
    """
    Attempt to fix common frontmatter issues.

    Args:
        content_path: Path to markdown file
        defaults: Default values to use for missing fields

    Returns:
        True if file was modified
    """
    import datetime as dt

    defaults = defaults or {}

    try:
        post = frontmatter.load(content_path)
    except Exception:
        return False

    modified = False

    # Add missing title
    if "title" not in post.metadata:
        post.metadata["title"] = defaults.get(
            "title", content_path.stem.replace("-", " ").title()
        )
        modified = True

    # Add missing created date
    if "created" not in post.metadata:
        post.metadata["created"] = defaults.get(
            "created", dt.date.today().isoformat()
        )
        modified = True

    # Add missing ai_contribution (default to human)
    if "ai_contribution" not in post.metadata:
        post.metadata["ai_contribution"] = defaults.get("ai_contribution", 0)
        modified = True

    # Add missing concepts
    if "concepts" not in post.metadata:
        post.metadata["concepts"] = defaults.get("concepts", [])
        modified = True

    # Add missing related_articles
    if "related_articles" not in post.metadata:
        post.metadata["related_articles"] = defaults.get("related_articles", [])
        modified = True

    if modified:
        content_path.write_text(frontmatter.dumps(post), encoding="utf-8")

    return modified
