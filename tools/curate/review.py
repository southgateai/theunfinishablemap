"""Content review and improvement using LLM."""

from pathlib import Path
from typing import Optional

import frontmatter

from ..llm import get_client, LLMClient


def review_content(
    content_path: Path,
    client: Optional[LLMClient] = None,
    aspects: Optional[list[str]] = None,
) -> dict:
    """
    Review content for quality and suggest improvements.

    Args:
        content_path: Path to the markdown file to review
        client: LLM client to use
        aspects: Aspects to review (clarity, accuracy, structure, etc.)

    Returns:
        Dict with review results and suggestions
    """
    if client is None:
        client = get_client()

    aspects = aspects or ["clarity", "structure", "depth", "accessibility"]

    # Load the content
    post = frontmatter.load(content_path)

    schema = {
        "type": "object",
        "properties": {
            "overall_quality": {
                "type": "number",
                "description": "Overall quality score 1-10",
            },
            "aspects": {
                "type": "object",
                "description": "Scores for each aspect",
            },
            "strengths": {
                "type": "array",
                "items": {"type": "string"},
            },
            "improvements": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "issue": {"type": "string"},
                        "suggestion": {"type": "string"},
                        "priority": {"type": "string"},
                    },
                },
            },
            "missing_concepts": {
                "type": "array",
                "items": {"type": "string"},
            },
        },
    }

    prompt = f"""Review this philosophical article for quality:

Title: {post.metadata.get('title', 'Untitled')}

Content:
{post.content}

Evaluate these aspects: {', '.join(aspects)}

For each aspect, provide a score (1-10) and specific feedback.
Identify strengths, suggest improvements, and note any philosophical concepts
that should be added or better explained."""

    return client.generate_structured(
        prompt=prompt,
        schema=schema,
        system="You are a philosophical editor reviewing content for quality and depth.",
    )


def improve_content(
    content_path: Path,
    suggestions: list[dict],
    client: Optional[LLMClient] = None,
    auto_apply: bool = False,
) -> str:
    """
    Apply improvements to content based on review suggestions.

    Args:
        content_path: Path to the markdown file
        suggestions: List of improvement suggestions from review
        client: LLM client to use
        auto_apply: If True, write improved content to file

    Returns:
        Improved content as string
    """
    if client is None:
        client = get_client()

    post = frontmatter.load(content_path)

    # Build improvement prompt
    suggestions_text = "\n".join(
        f"- {s['issue']}: {s['suggestion']}" for s in suggestions
    )

    prompt = f"""Improve this philosophical article based on the following suggestions:

Title: {post.metadata.get('title', 'Untitled')}

Current content:
{post.content}

Suggestions to address:
{suggestions_text}

Rewrite the article incorporating these improvements while maintaining the author's
voice and core arguments. Return only the improved content (no frontmatter)."""

    response = client.generate(
        prompt=prompt,
        system="You are an editor improving philosophical content.",
        max_tokens=5000,
    )

    # Update the content
    post.content = response.content

    # Update curation metadata
    import datetime

    if "authorship" in post.metadata:
        post.metadata["authorship"]["last_curated"] = datetime.date.today().isoformat()
        if post.metadata["authorship"]["type"] == "human":
            post.metadata["authorship"]["type"] = "mixed"
            post.metadata["authorship"]["ai_contribution"] = 20

    result = frontmatter.dumps(post)

    if auto_apply:
        content_path.write_text(result, encoding="utf-8")

    return result
