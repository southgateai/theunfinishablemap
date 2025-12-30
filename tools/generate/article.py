"""Article generation using LiteLLM."""

import datetime
from pathlib import Path
from typing import Optional

import frontmatter

from ..llm import get_client, LLMClient


# Default system prompt for article generation
SYSTEM_PROMPT = """You are a thoughtful philosopher and writer creating content for SouthgateAI,
an opinionated resource about philosophy and the meaning of life.

Your writing should be:
- Clear and accessible, avoiding unnecessary jargon
- Intellectually rigorous but not academic
- Opinionated and willing to take positions
- Well-structured with clear sections
- Engaging and thought-provoking

Always present multiple perspectives fairly before offering your own view."""


def generate_article(
    topic: str,
    concepts: Optional[list[str]] = None,
    style: str = "exploratory",
    length: str = "medium",
    client: Optional[LLMClient] = None,
    system_prompt: Optional[str] = None,
    output_path: Optional[Path] = None,
) -> str:
    """
    Generate a philosophical article on a topic.

    Args:
        topic: The topic to write about
        concepts: Related philosophical concepts to incorporate
        style: Writing style (exploratory, argumentative, analytical)
        length: Article length (short, medium, long)
        client: LLM client to use (defaults to configured client)
        system_prompt: Custom system prompt
        output_path: Optional path to write the article

    Returns:
        Generated article content with frontmatter
    """
    if client is None:
        client = get_client()

    # Build the generation prompt
    prompt = build_generation_prompt(topic, concepts, style, length)

    # Generate the content
    response = client.generate(
        prompt=prompt,
        system=system_prompt or SYSTEM_PROMPT,
        max_tokens=get_max_tokens(length),
        temperature=0.7,
    )

    # Build the article with frontmatter
    article = build_article(
        content=response.content,
        topic=topic,
        concepts=concepts or [],
        client=client,
    )

    # Write to file if path provided
    if output_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(article, encoding="utf-8")

    return article


def build_generation_prompt(
    topic: str,
    concepts: Optional[list[str]],
    style: str,
    length: str,
) -> str:
    """Build the prompt for article generation."""
    length_guide = {
        "short": "around 500-800 words",
        "medium": "around 1000-1500 words",
        "long": "around 2000-3000 words",
    }

    style_guide = {
        "exploratory": "Explore the topic openly, considering multiple angles and raising questions.",
        "argumentative": "Build a clear argument with thesis, evidence, and conclusion.",
        "analytical": "Break down the topic systematically, examining its components and implications.",
    }

    prompt = f"""Write a philosophical article about: {topic}

Style: {style_guide.get(style, style_guide['exploratory'])}

Length: {length_guide.get(length, length_guide['medium'])}

"""

    if concepts:
        prompt += f"""Incorporate these philosophical concepts where relevant: {', '.join(concepts)}

"""

    prompt += """Structure the article with:
1. An engaging introduction that frames the question
2. Clear sections exploring different aspects
3. Your considered perspective (be opinionated but fair)
4. A thoughtful conclusion

Use markdown formatting with ## for section headers."""

    return prompt


def get_max_tokens(length: str) -> int:
    """Get max tokens based on desired length."""
    return {
        "short": 1500,
        "medium": 3000,
        "long": 5000,
    }.get(length, 3000)


def build_article(
    content: str,
    topic: str,
    concepts: list[str],
    client: LLMClient,
) -> str:
    """Build article with frontmatter."""
    post = frontmatter.Post(content)

    # Set frontmatter
    post.metadata = {
        "title": topic,
        "date": datetime.date.today().isoformat(),
        "draft": True,  # Generated content starts as draft
        "topics": [],
        "authorship": {
            "type": "ai",
            "ai_contribution": 100,
            "human_contributors": [],
            "ai_system": client.model,
            "generated_date": datetime.date.today().isoformat(),
            "last_curated": None,
        },
        "structured_data": {
            "concepts": concepts,
            "related_articles": [],
        },
    }

    return frontmatter.dumps(post)


def generate_article_outline(
    topic: str,
    client: Optional[LLMClient] = None,
) -> dict:
    """
    Generate an outline for an article.

    Args:
        topic: The topic to outline
        client: LLM client to use

    Returns:
        Dict with title, sections, and concepts
    """
    if client is None:
        client = get_client()

    schema = {
        "type": "object",
        "properties": {
            "title": {"type": "string"},
            "thesis": {"type": "string"},
            "sections": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "heading": {"type": "string"},
                        "summary": {"type": "string"},
                    },
                },
            },
            "concepts": {
                "type": "array",
                "items": {"type": "string"},
            },
        },
    }

    return client.generate_structured(
        prompt=f"Create an outline for a philosophical article about: {topic}",
        schema=schema,
        system="You are a philosopher creating article outlines.",
    )
