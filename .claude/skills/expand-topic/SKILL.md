---
name: expand-topic
description: Generate a new article on a topic. Content is published directly.
---

# Expand Topic

Generate a new article on a philosophical topic.

## When to Use

- When a todo item is type `expand-topic`
- When `/expand-topic [topic]` is invoked
- After research has been completed on a topic

## Instructions

### 1. Check for Research

Look in `obsidian/workflow/research/` for existing research on this topic.

If no research exists:
- For simple topics, proceed with general knowledge
- For complex topics, run `/research-topic` first

### 2. Determine Target Location

- **Topics** (big questions): `obsidian/topics/[slug].md`
- **Concepts** (philosophical ideas): `obsidian/concepts/[slug].md`

Use kebab-case for filenames (e.g., `hard-problem-of-consciousness.md`).

### 3. Check Tenet Alignment

Before writing, review `obsidian/tenets/tenets.md` and ensure the article will:
- Not contradict any tenet
- Not endorse positions that tenets "rule out"
- Acknowledge the site's perspective where relevant

### 4. Generate Article

Use the existing generation tool:
```bash
uv run python scripts/generate.py article "[Topic Title]" --style exploratory
```

Or write directly with this structure:

```markdown
---
title: "[Topic Title]"
created: YYYY-MM-DD
modified: YYYY-MM-DD
human_modified:
ai_modified: YYYY-MM-DDTHH:MM:SS+00:00
draft: false
topics: []
concepts: []
related_articles: []
ai_contribution: 100
author:
ai_system: [current model]
ai_generated_date: YYYY-MM-DD
last_curated:
---

[Opening paragraph - accessible hook into the topic]

## [First Major Section]

[Content...]

## [Second Major Section]

[Content...]

## Relation to Site Perspective

[How this topic connects to the site's tenets - be explicit]

## Further Reading

- [[related-article-1]]
- [[related-article-2]]

## References

[If based on research, cite sources]
```

### 5. Run Crosslink Generation

After creating the file:
```bash
uv run python scripts/curate.py crosslink hugo/content/ --apply
```

### 6. Update Todo

If this was a todo item:
1. Mark the task as complete
2. Note the output file

### 7. Log to Changelog

Append to `obsidian/workflow/changelog.md`:
```markdown
### HH:MM - expand-topic
- **Status**: Success
- **Topic**: [topic name]
- **Output**: [filepath]
- **Based on research**: [yes/no, link if yes]
```

### 8. Commit

Create a git commit with message:
```
feat(content): Add article on [topic]

Based on research: [yes/no]
```

## Content Guidelines

### Voice and Tone
- Accessible but intellectually rigorous
- Exploratory rather than dogmatic
- Acknowledge uncertainty where appropriate
- Take positions where the site's tenets warrant

### Structure
- Lead with the most important/interesting point
- Use clear section headings
- Keep paragraphs digestible
- Link to related content

### Length
- Short: 500-800 words (simple concepts)
- Medium: 1000-1500 words (standard topics)
- Long: 2000-3000 words (complex topics)

## Important

- ALWAYS include `ai_contribution: 100`
- ALWAYS include current model in `ai_system`
- ALWAYS update `ai_modified` timestamp
- Content must align with site tenets
