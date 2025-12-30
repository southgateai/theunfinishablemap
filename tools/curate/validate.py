"""Frontmatter validation for content files."""

from pathlib import Path
from typing import Optional

import frontmatter


# Required frontmatter fields
REQUIRED_FIELDS = ["title", "authorship"]

# Required authorship fields
REQUIRED_AUTHORSHIP = ["type"]

# Valid authorship types
VALID_AUTHORSHIP_TYPES = ["ai", "human", "mixed"]


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

    # Validate authorship if present
    if "authorship" in metadata:
        authorship = metadata["authorship"]

        for field in REQUIRED_AUTHORSHIP:
            if field not in authorship:
                result["valid"] = False
                result["errors"].append(f"Missing authorship field: {field}")

        if "type" in authorship:
            if authorship["type"] not in VALID_AUTHORSHIP_TYPES:
                result["valid"] = False
                result["errors"].append(
                    f"Invalid authorship type: {authorship['type']}. "
                    f"Must be one of: {', '.join(VALID_AUTHORSHIP_TYPES)}"
                )

        # Check consistency
        if authorship.get("type") == "ai":
            if authorship.get("ai_contribution", 100) != 100:
                result["warnings"].append(
                    "AI-authored content should have ai_contribution: 100"
                )
            if not authorship.get("ai_system"):
                result["warnings"].append(
                    "AI-authored content should specify ai_system"
                )

        elif authorship.get("type") == "human":
            if authorship.get("ai_contribution", 0) != 0:
                result["warnings"].append(
                    "Human-authored content should have ai_contribution: 0"
                )
            if not authorship.get("human_contributors"):
                result["warnings"].append(
                    "Human-authored content should list contributors"
                )

        elif authorship.get("type") == "mixed":
            if not authorship.get("ai_contribution"):
                result["warnings"].append(
                    "Mixed authorship should specify ai_contribution percentage"
                )

    # Check optional but recommended fields
    if strict:
        if "date" not in metadata:
            result["warnings"].append("Missing recommended field: date")
        if "structured_data" not in metadata:
            result["warnings"].append("Missing recommended field: structured_data")

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
    import datetime

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

    # Add missing date
    if "date" not in post.metadata:
        post.metadata["date"] = defaults.get(
            "date", datetime.date.today().isoformat()
        )
        modified = True

    # Add missing authorship
    if "authorship" not in post.metadata:
        post.metadata["authorship"] = defaults.get(
            "authorship",
            {
                "type": "human",
                "ai_contribution": 0,
                "human_contributors": [],
                "ai_system": None,
                "generated_date": None,
                "last_curated": None,
            },
        )
        modified = True

    # Add missing structured_data
    if "structured_data" not in post.metadata:
        post.metadata["structured_data"] = defaults.get(
            "structured_data",
            {
                "concepts": [],
                "related_articles": [],
            },
        )
        modified = True

    if modified:
        content_path.write_text(frontmatter.dumps(post), encoding="utf-8")

    return modified
