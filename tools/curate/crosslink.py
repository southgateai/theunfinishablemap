"""Cross-linking content based on related concepts."""

from pathlib import Path
from typing import Optional

import frontmatter

from ..llm import get_client, LLMClient


def generate_crosslinks(
    content_dir: Path,
    client: Optional[LLMClient] = None,
    min_relevance: float = 0.7,
) -> dict[str, list[str]]:
    """
    Generate cross-links between related content.

    Args:
        content_dir: Directory containing markdown files
        client: LLM client to use
        min_relevance: Minimum relevance score (0-1) for linking

    Returns:
        Dict mapping file paths to lists of related file paths
    """
    if client is None:
        client = get_client()

    # Collect all content summaries
    content_summaries = []
    for md_file in content_dir.rglob("*.md"):
        if md_file.name.startswith("_"):
            continue

        post = frontmatter.load(md_file)
        content_summaries.append(
            {
                "path": str(md_file.relative_to(content_dir)),
                "title": post.metadata.get("title", md_file.stem),
                "concepts": post.metadata.get("structured_data", {}).get("concepts", []),
                "summary": post.content[:500],  # First 500 chars as summary
            }
        )

    if len(content_summaries) < 2:
        return {}

    # Generate relationships
    schema = {
        "type": "object",
        "properties": {
            "relationships": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "source": {"type": "string"},
                        "target": {"type": "string"},
                        "relevance": {"type": "number"},
                        "reason": {"type": "string"},
                    },
                },
            }
        },
    }

    # Build content list for prompt
    content_list = "\n".join(
        f"- {c['path']}: {c['title']} (concepts: {', '.join(c['concepts'])})"
        for c in content_summaries
    )

    result = client.generate_structured(
        prompt=f"""Analyze these philosophical articles and identify meaningful relationships:

{content_list}

For each pair that shares concepts, themes, or arguments, indicate:
- The relevance score (0.0 to 1.0)
- Why they're related

Only include pairs with relevance >= {min_relevance}""",
        schema=schema,
        system="You are a philosophical librarian identifying connections between ideas.",
    )

    # Build crosslink map
    crosslinks: dict[str, list[str]] = {}

    for rel in result.get("relationships", []):
        if rel.get("relevance", 0) >= min_relevance:
            source = rel["source"]
            target = rel["target"]

            if source not in crosslinks:
                crosslinks[source] = []
            if target not in crosslinks[source]:
                crosslinks[source].append(target)

            # Bidirectional linking
            if target not in crosslinks:
                crosslinks[target] = []
            if source not in crosslinks[target]:
                crosslinks[target].append(source)

    return crosslinks


def apply_crosslinks(
    content_dir: Path,
    crosslinks: dict[str, list[str]],
) -> int:
    """
    Apply cross-links to content frontmatter.

    Args:
        content_dir: Directory containing markdown files
        crosslinks: Dict mapping paths to related paths

    Returns:
        Number of files updated
    """
    updated = 0

    for source_path, related_paths in crosslinks.items():
        full_path = content_dir / source_path
        if not full_path.exists():
            continue

        post = frontmatter.load(full_path)

        # Ensure structured_data exists
        if "structured_data" not in post.metadata:
            post.metadata["structured_data"] = {}

        # Update related articles
        current_related = set(
            post.metadata["structured_data"].get("related_articles", [])
        )
        new_related = current_related.union(set(related_paths))

        if new_related != current_related:
            post.metadata["structured_data"]["related_articles"] = sorted(new_related)
            full_path.write_text(frontmatter.dumps(post), encoding="utf-8")
            updated += 1

    return updated


def suggest_concepts(
    content_path: Path,
    client: Optional[LLMClient] = None,
) -> list[str]:
    """
    Suggest philosophical concepts that should be tagged for this content.

    Args:
        content_path: Path to markdown file
        client: LLM client to use

    Returns:
        List of suggested concept tags
    """
    if client is None:
        client = get_client()

    post = frontmatter.load(content_path)

    schema = {
        "type": "object",
        "properties": {
            "concepts": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Philosophical concepts discussed in this content",
            }
        },
    }

    result = client.generate_structured(
        prompt=f"""Identify the key philosophical concepts in this article:

Title: {post.metadata.get('title', 'Untitled')}

Content:
{post.content}

List specific philosophical concepts, theories, and ideas mentioned or discussed.
Use canonical names (e.g., "existentialism", "categorical imperative", "qualia").""",
        schema=schema,
        system="You are a philosopher identifying concepts in text.",
    )

    return result.get("concepts", [])
